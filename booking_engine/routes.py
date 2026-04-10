from flask import flash, render_template, redirect, session, request, jsonify, json
from flask_session import Session
from flask_mail import Message
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from booking_engine import app, db, os, basedir, mail
from booking_engine.helpers import login_required, allowed_file, usd
from booking_engine.room_search import single_room_search, multiple_rooms_search_no_children, multiple_rooms_search_children
from booking_engine.models import Admin, Room, RateType, RatePlan, ListedRoom, RoomAvailability, bookings, Client, Reservation, SiteContent, SiteSetting, GalleryImage
from datetime import datetime, timedelta
import calendar
from iteration_utilities import unique_everseen
import pandas as pd
import random


def ensure_cms_defaults():
    db.create_all()

    defaults = {
        "home": ("Welcome to Aqua Viva", "Discover our rooms and book your next stay in a few clicks."),
        "about": ("About Aqua Viva", "Aqua Viva is a modern hotel experience focused on comfort and service."),
        "prices": ("Aqua Viva Prices", "Browse our prices and current offers."),
        "gallery": ("Aqua Viva Gallery", "Explore our hotel spaces and atmosphere."),
    }

    for page_key, values in defaults.items():
        existing = SiteContent.query.filter_by(page_key=page_key).first()
        if not existing:
            db.session.add(SiteContent(page_key=page_key, title=values[0], body=values[1]))

    banner = SiteSetting.query.filter_by(setting_key="banner_image").first()
    if not banner:
        db.session.add(SiteSetting(setting_key="banner_image", setting_value="images/banner-5.png"))
    home_background = SiteSetting.query.filter_by(setting_key="home_background_image").first()
    if not home_background:
        db.session.add(SiteSetting(setting_key="home_background_image", setting_value=""))
    home_slider = SiteSetting.query.filter_by(setting_key="home_slider_ids").first()
    if not home_slider:
        db.session.add(SiteSetting(setting_key="home_slider_ids", setting_value=""))
    home_slider_mode = SiteSetting.query.filter_by(setting_key="home_slider_mode").first()
    if not home_slider_mode:
        db.session.add(SiteSetting(setting_key="home_slider_mode", setting_value="selected"))
    about_image = SiteSetting.query.filter_by(setting_key="about_image").first()
    if not about_image:
        db.session.add(SiteSetting(setting_key="about_image", setting_value=""))
    phone = SiteSetting.query.filter_by(setting_key="site_phone").first()
    if not phone:
        db.session.add(SiteSetting(setting_key="site_phone", setting_value="+1-949-468-2750"))
    email = SiteSetting.query.filter_by(setting_key="site_email").first()
    if not email:
        db.session.add(SiteSetting(setting_key="site_email", setting_value="cs50x@hotel.edu"))
    logo = SiteSetting.query.filter_by(setting_key="site_logo").first()
    if not logo:
        db.session.add(SiteSetting(setting_key="site_logo", setting_value="images/logo1.png"))

    db.session.commit()


def get_site_content(page_key):
    content = SiteContent.query.filter_by(page_key=page_key).first()
    if not content:
        return {"title": "", "body": ""}
    return {"title": content.title, "body": content.body}


@app.context_processor
def inject_site_banner():
    banner = SiteSetting.query.filter_by(setting_key="banner_image").first()
    home_background = SiteSetting.query.filter_by(setting_key="home_background_image").first()
    banner_path = banner.setting_value if banner else "images/banner-5.png"
    home_bg_path = home_background.setting_value if home_background else ""
    phone = SiteSetting.query.filter_by(setting_key="site_phone").first()
    email = SiteSetting.query.filter_by(setting_key="site_email").first()
    logo = SiteSetting.query.filter_by(setting_key="site_logo").first()
    context = {
        "site_phone": phone.setting_value if phone else "+1-949-468-2750",
        "site_email": email.setting_value if email else "cs50x@hotel.edu",
        "site_logo_path": logo.setting_value if logo else "images/logo1.png",
    }
    if request.path == "/" and home_bg_path:
        context["site_banner_path"] = home_bg_path
        return context
    context["site_banner_path"] = banner_path
    return context


def get_or_create_single_gite():
    room = Room.query.order_by(Room.id.asc()).first()
    if not room:
        room = Room(
            name="Gite Aqua Viva",
            max_guests=4,
            min_guests=1,
            max_adults=4,
            max_children=0,
            total_of_this_type=1,
            room_image="",
            room_description="Gite for up to 4 guests.",
        )
        db.session.add(room)
        db.session.commit()
    return room


def ensure_room_availability_rows(room, start_date, end_date):
    """Ensure listed_room and availability rows exist for each date."""
    day = timedelta(days=1)
    current = start_date
    while current <= end_date:
        listed_room = ListedRoom.query.filter_by(room_id=room.id, listed_date=current).first()
        if not listed_room:
            listed_room = ListedRoom(
                listed_date=current,
                quantity_per_date=1,
                rate_type_id=None,
                room_id=room.id,
            )
            db.session.add(listed_room)
            db.session.flush()
            db.session.add(
                RoomAvailability(
                    left_to_sell=1,
                    booked_quantity=0,
                    listed_room_id=listed_room.id,
                    is_it_available=1,
                )
            )
        current += day
    db.session.commit()


# Main index from where the client performs the search
@app.route("/", methods=["GET", "POST"])
def index():
    ensure_cms_defaults()
    gite = get_or_create_single_gite()

    if request.method == "POST":
            
        checkin = datetime.strptime(request.form.get("checkin"), "%d-%m-%Y")
        checkout = datetime.strptime(request.form.get("checkout"), "%d-%m-%Y")
        rooms_request = 1
        adults = int(request.form.get("adults"))
        children = "none"
        first_child = None
        second_child = None

        if adults < 1 or adults > 4:
            flash("This gite accepts 1 to 4 guests.")
            return redirect("/")

        day = timedelta(days=1)
        total_days = int((checkout - checkin).days)

        # Filter all listed rooms between checkin and checkout that have is_it_available status == True
        listed_rooms = ListedRoom.query.filter(ListedRoom.listed_date.between(checkin, checkout - day)).filter(ListedRoom.room_id == gite.id).join(RoomAvailability).filter(RoomAvailability.is_it_available == 1).all()

        # First we check if there is any listed room for the client dates
        if not listed_rooms:
            flash("No rooms available for the selected dates!")
            return redirect("/")
        
        if len(listed_rooms) < total_days:
            flash(f"Try different search, some dates are taken! Try from {listed_rooms[0].listed_date}")
            return redirect("/") 

        total_children = 0

        if children == "one":
            total_children = 1
        elif children == "two":
            total_children = 2

        all_rooms = [gite]

        # total guests selected by client
        total_guests = adults + total_children

        bookable_rooms = []

        for room in all_rooms:

            if (rooms_request == 1 and 
                        total_guests <= room.max_guests and 
                        adults <= room.max_adults and 
                        total_children <= room.max_children and 
                        total_guests >= room.min_guests or adults < room.min_guests):
                
                
                room_search = single_room_search(room, rooms_request, total_guests, adults, total_children, listed_rooms, checkin, checkout, first_child, second_child, children, total_days)
                
                if room_search:
                    bookable_rooms.append(room_search)

            elif rooms_request > 1 and total_children == 0:

                room_search = multiple_rooms_search_no_children(room, rooms_request, total_guests, adults, listed_rooms, checkin, checkout, total_days, first_child, second_child, total_children)  
        
                if room_search:
                    bookable_rooms.append(room_search)

            elif rooms_request > 1 and total_children > 0:

                room_search = multiple_rooms_search_children(room, rooms_request, total_guests, adults, total_children, listed_rooms, checkin, checkout, first_child, second_child, children, total_days)

                if room_search:
                    bookable_rooms.append(room_search)

        
        # Display under the cards with options random booked status
        booked_ago = ['2hrs', '5hrs', '1hr', '18hrs', '23hrs', '24hrs', '15hrs', '17hrs', '3hrs', '35min', '7hrs', '12hrs', '1day', '2days', '3days']
        if bookable_rooms:
            return render_template("offer_rooms.html", bookable_rooms=bookable_rooms, booked_ago=booked_ago)

        if not bookable_rooms:
            flash("No availability for the selected dates!")
            return redirect("/")
                                
        return redirect("/")
    else:
        slider_setting = SiteSetting.query.filter_by(setting_key="home_slider_ids").first()
        selected_ids = []
        if slider_setting and slider_setting.setting_value:
            for raw in slider_setting.setting_value.split(","):
                raw = raw.strip()
                if raw.isdigit():
                    selected_ids.append(int(raw))

        all_images = GalleryImage.query.order_by(GalleryImage.created_at.desc()).all()
        if selected_ids:
            selected_map = {img.id: img for img in all_images}
            ordered_selected = [selected_map[i] for i in selected_ids if i in selected_map]
            remaining = [img for img in all_images if img.id not in selected_ids]
            images = ordered_selected + remaining
        else:
            images = all_images
        return render_template("index.html", home_content=get_site_content("home"), hero_images=images)


@app.route("/gallery", methods=["GET"])
def gallery():
    ensure_cms_defaults()
    images = GalleryImage.query.order_by(GalleryImage.created_at.desc()).all()
    return render_template("gallery.html", gallery_content=get_site_content("gallery"), gallery_images=images)


@app.route("/prices", methods=["GET"])
def prices():
    ensure_cms_defaults()
    return render_template("prices.html", prices_content=get_site_content("prices"))


@app.route("/about", methods=["GET"])
def about():
    ensure_cms_defaults()
    about_image = SiteSetting.query.filter_by(setting_key="about_image").first()
    return render_template(
        "about.html",
        about_content=get_site_content("about"),
        about_image_path=about_image.setting_value if about_image else ""
    )


# Handle the client booking information, create client and reservation in db
@app.route("/booking_request", methods=["GET", "POST"])
def booking_request():

    if request.method == "POST":

        room_type = request.form.get("room_type")
        total_rooms = request.form.get("total_rooms")
        total_guests = request.form.get("total_guests")
        total_adults = request.form.get("total_adults")
        total_children = request.form.get("total_children")
        children_age = request.form.get("children_age")
        from_date = datetime.strptime(request.form.get("from_date"), '%d-%m-%Y')
        to_date = datetime.strptime(request.form.get("to_date"), '%d-%m-%Y')
        total_days = request.form.get("total_days")
        room_price_per_day = request.form.get("room_price_per_day")
        all_rooms_price_per_day = request.form.get("all_rooms_price_per_day")
        total_price = request.form.get("total_price")
        room_image = request.form.get("room_image")

        reservation = {
            'room_type': room_type,
            'total_rooms': total_rooms,
            'total_guests': total_guests,
            'total_adults': total_adults,
            'total_children': total_children,
            'children_age': children_age,
            'from_date': from_date,
            'to_date': to_date,
            'total_days': total_days,
            'room_price_per_day': room_price_per_day,
            'all_rooms_price_per_day': all_rooms_price_per_day,
            'total_price': total_price,
            'room_image': room_image
        }

        reservation_data = []

        reservation_data.append(reservation)

    
        return render_template("booking_form.html", reservation_data=reservation_data)
    

# Get the guest data and reservation data and create client and reservation objects linked together in bookings table       
@app.route("/booking_form", methods=["GET", "POST"])
def booking_form():
    
    if request.method == "POST":
        
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        email = request.form.get("email")
        phone = request.form.get("phone")

        room_type = request.form.get("room_type")
        total_rooms = int(request.form.get("total_rooms"))
        total_guests = request.form.get("total_guests")
        total_adults = request.form.get("total_adults")
        total_children = request.form.get("total_children")
        children_age = request.form.get("children_age")
        from_date = datetime.strptime(request.form.get("from_date"), '%d-%m-%Y')
        to_date = datetime.strptime(request.form.get("to_date"), '%d-%m-%Y')
        total_days = request.form.get("total_days")
        room_price_per_day = request.form.get("room_price_per_day")
        all_rooms_price_per_day = request.form.get("all_rooms_price_per_day")
        total_price = request.form.get("total_price")
        
        reservation_date = datetime.now().strftime('%Y%m%d%H%M%S')
        reservation_number = random.randint(1000, 9999) + int(reservation_date)

        room = Room.query.filter_by(name=room_type).first()
        listed_rooms = ListedRoom.query.filter(ListedRoom.listed_date.between(from_date, to_date - timedelta(days=1))).filter(ListedRoom.room_id == room.id).all()    

        client = Client(
            first_name = first_name,
            last_name = last_name,
            email = email,
            phone_number = phone
        )

        client_reservation = Reservation(
            reservation_number = reservation_number,
            check_in = from_date,
            check_out = to_date,
            total_days = total_days,
            total_rooms_reserved = total_rooms,
            total_guests = total_guests,
            total_adults = total_adults,
            total_children = total_children,
            children_age = children_age,
            room_price_day = room_price_per_day,
            all_rooms_price_day = all_rooms_price_per_day,
            total_price = total_price,
            room_id = room.id,

        )


        client.reservation.append(client_reservation)

        availability = []
        for listed_room in listed_rooms:

            # Query room availability 
            room_availability = RoomAvailability.query.filter(RoomAvailability.listed_room_id == listed_room.id).filter(Room.id == room.id).all()
            availability.append(room_availability)


        for date  in availability:
            for room in date:
                
                room.booked_quantity += total_rooms
                room.left_to_sell -= total_rooms

                if room.left_to_sell == 0:
                    room.is_it_available = 0

        db.session.add(client)
        db.session.commit()

        try:
            msg = Message('Hello', sender = 'cs50xhotel@gmail.com', recipients = [f'{client.email}'])
            msg.body = f"""Hello {client.first_name} {client.last_name}! Thank you for your reservation! The reservation number is {client_reservation.reservation_number} 
            with check-in date {client_reservation.check_in}. If you have any questions or information is needed you can always call us on - +1-949-468-2750.
            """
            mail.send(msg)
        except:
            return render_template("reservation_created.html")


        return render_template("reservation_created.html")
    
    else:
        return render_template("booking_form.html")


@app.route("/admin_login", methods=["GET", "POST"])
def admin_login():

    session.clear()

    if request.method == "POST":

        admin_name = request.form.get("admin")
        password = request.form.get("password")

        # query admin data by the given username
        admin = Admin.query.filter_by(admin=admin_name).first()
    
        if not admin or not check_password_hash(admin.password, password):
            flash("Admin username not match or wrong password!")
            return redirect("/")
        
        session['admin_id'] = admin.id

        flash("Login succesful!")
        return redirect('/admin_panel')

    else:

        return render_template("admin_login.html")

    
@app.route("/logout", methods=["GET", "POST"])
def logout():

    session.clear()
    flash("Loged out!")

    return redirect("/")

# This will be turned off from the html layout and navbar
@app.route("/admin_register", methods=["GET", "POST"])
def admin_register():

    if request.method == "POST":

        admin_name = request.form.get("admin")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        if password != confirm_password:
            flash("first password and confirm password not matching!")
            return render_template("/admin_register.html")
        
        password_hash = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)

        admin = Admin(
            admin = admin_name,
            password = password_hash,
        )
        db.session.add(admin)
        db.session.commit()

        return redirect("/admin_login")

    return render_template("admin_register.html")

# Only used to render the Reservations tab no other functionality for now
@app.route("/admin_panel", methods=["GET", "POST"])
@login_required
def admin_panel():

    if request.method == "POST":
        pass

    else:
        room = get_or_create_single_gite()
        month_param = request.args.get("month")
        today = datetime.now().date()
        if month_param:
            try:
                month_start = datetime.strptime(month_param, "%Y-%m").date().replace(day=1)
            except ValueError:
                month_start = today.replace(day=1)
        else:
            month_start = today.replace(day=1)

        if month_start.month == 12:
            next_month_start = month_start.replace(year=month_start.year + 1, month=1, day=1)
        else:
            next_month_start = month_start.replace(month=month_start.month + 1, day=1)
        month_end = next_month_start - timedelta(days=1)

        if month_start.month == 1:
            prev_month_start = month_start.replace(year=month_start.year - 1, month=12, day=1)
        else:
            prev_month_start = month_start.replace(month=month_start.month - 1, day=1)

        start_date = month_start
        end_date = month_end
        ensure_room_availability_rows(room, start_date, end_date)

        clients = Client.query.all()
        rooms = Room.query.all()
        dates = pd.date_range(start=start_date, end=end_date)
        listed_rooms = ListedRoom.query.filter(
            ListedRoom.listed_date.between(start_date, end_date),
            ListedRoom.room_id == room.id
        ).join(RoomAvailability).all()

        availability_map = {}
        for listed in listed_rooms:
            if listed.room_availability:
                availability_map[listed.listed_date.date()] = listed.room_availability[0]

        reservations = Reservation.query.filter(Reservation.room_id == room.id).all()
        checkin_map = {}
        checkout_map = {}
        occupied_dates = set()
        occupied_map = {}
        for res in reservations:
            check_in_date = res.check_in.date()
            check_out_date = res.check_out.date()
            checkin_map[check_in_date] = res
            checkout_map[check_out_date] = res
            current = check_in_date
            while current < check_out_date:
                occupied_dates.add(current)
                occupied_map[current] = res
                current += timedelta(days=1)

        cal = calendar.Calendar(firstweekday=0)
        month_weeks = cal.monthdatescalendar(month_start.year, month_start.month)

    
        return render_template(
            "admin_panel.html",
            clients=clients,
            rooms=rooms,
            room=room,
            dates=dates,
            availability_map=availability_map,
            today=today,
            month_label=month_start.strftime("%B %Y"),
            prev_month=prev_month_start.strftime("%Y-%m"),
            next_month=next_month_start.strftime("%Y-%m"),
            month_weeks=month_weeks,
            current_month=month_start.month,
            checkin_map=checkin_map,
            checkout_map=checkout_map,
            occupied_dates=occupied_dates,
            occupied_map=occupied_map,
            current_month_query=month_start.strftime("%Y-%m"),
        )


@app.route("/admin_manual_reservation", methods=["POST"])
@login_required
def admin_manual_reservation():
    room = get_or_create_single_gite()
    check_in = datetime.strptime(request.form.get("check_in"), "%d-%m-%Y")
    check_out_raw = request.form.get("check_out")
    if check_out_raw:
        check_out = datetime.strptime(check_out_raw, "%d-%m-%Y")
        nights = (check_out - check_in).days
    else:
        nights = int(request.form.get("nights") or 1)
        check_out = check_in + timedelta(days=nights)

    return_month = request.form.get("return_month", datetime.now().strftime("%Y-%m"))
    panel_redirect = f"/admin_panel?month={return_month}#reservations-anchor"

    if nights < 1 or check_out <= check_in:
        flash("Check-out must be after check-in.")
        return redirect(panel_redirect)
    listed_rooms = ListedRoom.query.filter(
        ListedRoom.listed_date.between(check_in, check_out - timedelta(days=1)),
        ListedRoom.room_id == room.id
    ).all()
    if len(listed_rooms) != nights:
        ensure_room_availability_rows(room, check_in.date(), (check_out - timedelta(days=1)).date())
        listed_rooms = ListedRoom.query.filter(
            ListedRoom.listed_date.between(check_in, check_out - timedelta(days=1)),
            ListedRoom.room_id == room.id
        ).all()

    for listed in listed_rooms:
        availability = RoomAvailability.query.filter_by(listed_room_id=listed.id).first()
        if not availability or availability.left_to_sell <= 0 or availability.is_it_available == 0:
            flash("Selected period is not available.")
            return redirect(panel_redirect)

    email = request.form.get("email")
    client = Client.query.filter_by(email=email).first()
    if not client:
        client = Client(
            first_name=request.form.get("first_name"),
            last_name=request.form.get("last_name"),
            email=email,
            phone_number=request.form.get("phone"),
        )
        db.session.add(client)
        db.session.flush()

    reservation_number = random.randint(1000, 9999) + int(datetime.now().strftime('%Y%m%d%H%M%S'))
    total_adults = int(request.form.get("adults") or 1)
    total_guests = total_adults
    room_price_day = int(request.form.get("price_per_day") or 0)
    total_price = room_price_day * nights

    reservation = Reservation(
        reservation_number=reservation_number,
        check_in=check_in,
        check_out=check_out,
        total_days=nights,
        total_rooms_reserved=1,
        total_guests=total_guests,
        total_adults=total_adults,
        total_children=0,
        children_age="",
        room_price_day=room_price_day,
        all_rooms_price_day=room_price_day,
        total_price=total_price,
        room_id=room.id,
    )
    client.reservation.append(reservation)

    for listed in listed_rooms:
        availability = RoomAvailability.query.filter_by(listed_room_id=listed.id).first()
        availability.booked_quantity = (availability.booked_quantity or 0) + 1
        availability.left_to_sell = max(0, availability.left_to_sell - 1)
        if availability.left_to_sell == 0:
            availability.is_it_available = 0

    db.session.commit()
    flash("Manual reservation added.")
    return redirect(panel_redirect)


@app.route("/cms", methods=["GET", "POST"])
@login_required
def cms():
    ensure_cms_defaults()

    if request.method == "POST":
        action = request.form.get("action")

        if action == "update_content":
            pages = ("home", "about", "prices", "gallery")
            for page_key in pages:
                page = SiteContent.query.filter_by(page_key=page_key).first()
                page.title = request.form.get(f"{page_key}_title", page.title)
                page.body = request.form.get(f"{page_key}_body", page.body)
            db.session.commit()
            flash("Site texts updated.")
            return redirect("/cms")

        if action == "update_contact":
            phone = SiteSetting.query.filter_by(setting_key="site_phone").first()
            email = SiteSetting.query.filter_by(setting_key="site_email").first()
            phone.setting_value = request.form.get("site_phone", phone.setting_value)
            email.setting_value = request.form.get("site_email", email.setting_value)
            db.session.commit()
            flash("Contact details updated.")
            return redirect("/cms")

        if action == "upload_banner":
            banner_image = request.files.get("banner_image")
            if banner_image and allowed_file(banner_image.filename):
                filename = secure_filename(banner_image.filename)
                if filename:
                    banner_image.save(os.path.join(basedir, app.config['UPLOAD_FOLDER'], filename))
                    setting = SiteSetting.query.filter_by(setting_key="banner_image").first()
                    setting.setting_value = f"uploads/{filename}"
                    db.session.commit()
                    flash("Banner updated.")
            else:
                flash("Unsupported banner file.")
            return redirect("/cms")

        if action == "upload_home_background":
            home_bg_image = request.files.get("home_bg_image")
            if home_bg_image and allowed_file(home_bg_image.filename):
                filename = secure_filename(home_bg_image.filename)
                if filename:
                    home_bg_image.save(os.path.join(basedir, app.config['UPLOAD_FOLDER'], filename))
                    setting = SiteSetting.query.filter_by(setting_key="home_background_image").first()
                    setting.setting_value = f"uploads/{filename}"
                    db.session.commit()
                    flash("Home background updated.")
            else:
                flash("Unsupported home background file.")
            return redirect("/cms")

        if action == "upload_about_image":
            about_image = request.files.get("about_image")
            if about_image and allowed_file(about_image.filename):
                filename = secure_filename(about_image.filename)
                if filename:
                    about_image.save(os.path.join(basedir, app.config['UPLOAD_FOLDER'], filename))
                    setting = SiteSetting.query.filter_by(setting_key="about_image").first()
                    setting.setting_value = f"uploads/{filename}"
                    db.session.commit()
                    flash("About image updated.")
            else:
                flash("Unsupported about image file.")
            return redirect("/cms")

        if action == "upload_logo":
            logo_image = request.files.get("site_logo")
            if logo_image and allowed_file(logo_image.filename):
                filename = secure_filename(logo_image.filename)
                if filename:
                    logo_image.save(os.path.join(basedir, app.config['UPLOAD_FOLDER'], filename))
                    setting = SiteSetting.query.filter_by(setting_key="site_logo").first()
                    setting.setting_value = f"uploads/{filename}"
                    db.session.commit()
                    flash("Logo updated.")
            else:
                flash("Unsupported logo file.")
            return redirect("/cms")

        if action == "upload_gallery":
            files = request.files.getlist("gallery_image")
            caption = request.form.get("caption")
            added = 0
            for gallery_image in files:
                if gallery_image and allowed_file(gallery_image.filename):
                    filename = secure_filename(gallery_image.filename)
                    if filename:
                        gallery_image.save(os.path.join(basedir, app.config['UPLOAD_FOLDER'], filename))
                        db.session.add(GalleryImage(image_file=f"uploads/{filename}", caption=caption))
                        added += 1
            if added > 0:
                db.session.commit()
                flash(f"{added} gallery image(s) uploaded.")
            else:
                flash("No supported gallery files selected.")
            return redirect("/cms")

        if action == "update_home_slider":
            ids = []
            selected_values = request.form.getlist("slider_image_ids")
            for value in selected_values:
                if value and value.isdigit() and int(value) not in ids:
                    ids.append(int(value))
            setting = SiteSetting.query.filter_by(setting_key="home_slider_ids").first()
            ids = ids[:3]
            setting.setting_value = ",".join(str(i) for i in ids)
            db.session.commit()
            flash("Home slider selection updated.")
            return redirect("/cms")

        if action == "delete_gallery":
            image_id = request.form.get("image_id")
            image = GalleryImage.query.filter_by(id=image_id).first()
            if image:
                db.session.delete(image)
                db.session.commit()
                flash("Gallery image removed.")
            return redirect("/cms")

    page_keys = ("home", "about", "prices", "gallery")
    contents = {k: SiteContent.query.filter_by(page_key=k).first() for k in page_keys}
    images = GalleryImage.query.order_by(GalleryImage.created_at.desc()).all()
    banner = SiteSetting.query.filter_by(setting_key="banner_image").first()
    home_bg = SiteSetting.query.filter_by(setting_key="home_background_image").first()
    about_image = SiteSetting.query.filter_by(setting_key="about_image").first()
    site_phone = SiteSetting.query.filter_by(setting_key="site_phone").first()
    site_email = SiteSetting.query.filter_by(setting_key="site_email").first()
    site_logo = SiteSetting.query.filter_by(setting_key="site_logo").first()
    slider_setting = SiteSetting.query.filter_by(setting_key="home_slider_ids").first()
    current_slider_ids = []
    if slider_setting and slider_setting.setting_value:
        current_slider_ids = [int(x) for x in slider_setting.setting_value.split(",") if x.strip().isdigit()]
    return render_template(
        "cms.html",
        contents=contents,
        gallery_images=images,
        banner_path=banner.setting_value,
        home_bg_path=home_bg.setting_value,
        about_image_path=about_image.setting_value,
        site_phone=site_phone.setting_value,
        site_email=site_email.setting_value,
        site_logo_path=site_logo.setting_value,
        current_slider_ids=current_slider_ids,
    )


# This route handles the room creation process
@app.route("/create_rooms", methods=["GET", "POST"])
@login_required
def create_rooms():
    room = get_or_create_single_gite()

    if request.method == "POST":
        room_name = request.form.get("room") or "Gite Aqua Viva"
        room_image = request.files.get("room_image")
        room_description = request.form.get("room_description")
        
        room_image_new = ''

        # Check if there is umg uploaded. Check if filename is supported and secure.
        # Here can be improved with using uuid for creating unique id for this room only or upload and use as cdn link
        if room_image and allowed_file(room_image.filename):
            filename = secure_filename(room_image.filename)
            if filename:
                room_image.save(os.path.join(basedir, app.config['UPLOAD_FOLDER'], filename))
                room_image_new = filename
                flash('succes!')
        
        room.name = room_name
        room.max_guests = 4
        room.min_guests = 1
        room.max_adults = 4
        room.max_children = 0
        room.total_of_this_type = 1
        if room_image_new:
            room.room_image = room_image_new
        room.room_description = room_description
        db.session.commit()

        return redirect("/create_rooms")
    else:
        room_info = [room]
        return render_template("create_rooms.html", room_info=room_info)

# Used to delete rooms
@app.route("/delete_rooms", methods=["GET", "POST"])
@login_required
def delete_rooms():
    
    if request.method == "POST":

        delete_room = int(request.form.get("delete_room"))
      

        if delete_room:
            Room.query.filter(Room.id == delete_room).delete()
            db.session.commit()
            return redirect("/create_rooms")

# This route handles rate plans creation
@app.route("/rate_plans", methods=["GET", "POST"])
@login_required
def rate_plans():

    if request.method == "POST":

        rate_plan_name = request.form.get("rate_plan_name")

        total_rate_plans = 2
        rate_plan2 = request.form.get("start_date_2")
        rate_plan3 = request.form.get("start_date_3")
        rate_plan4 = request.form.get("start_date_4")

        if rate_plan2:
            total_rate_plans += 1
        if rate_plan3:
            total_rate_plans += 1
        if rate_plan4:
            total_rate_plans += 1


        rate_plan = RateType(
            rate_name = rate_plan_name
        )

        db.session.add(rate_plan)
        db.session.flush()

        all_data_is_correct = True

        # Iterate over all rate plan periods, get the data and add it to the database
        for i in range(1, total_rate_plans):

            start_date = datetime.strptime(request.form.get("start_date" + "_" + str(i)), "%d-%m-%Y")
            end_date = datetime.strptime(request.form.get("end_date" + "_" + str(i)), "%d-%m-%Y")
            price_adult = request.form.get("price_per_day_adult" + "_" + str(i))
            price_single_adult = request.form.get("price_per_day_single_adult" + "_" + str(i))
            price_child_under_12_reg_bed = request.form.get("price_per_day_child_under_12_regular_bed" + "_" + str(i))
            price_child_12 = request.form.get("price_per_day_child_under_12" + "_" + str(i))
            price_child_7 = request.form.get("price_per_day_child_under_7" + "_" + str(i))
            price_child_2 = request.form.get("price_per_day_child_under_2" + "_" + str(i))

            # If something wrong all_data_is_correct will be set to False
            if (price_adult.isalpha() or
                    price_single_adult.isalpha() or
                    price_child_under_12_reg_bed.isalpha() or
                    price_child_12.isalpha() or
                    price_child_7.isalpha() or
                    price_child_2.isalpha()):
                        flash("Only digits supported for prices!")
                        all_data_is_correct = False
                        return redirect("/rate_plans")


            # Create rate plan object
            rate_plan_rates = RatePlan(
            adult = price_adult,
            single_adult = price_single_adult,
            child_under_12_rb = price_child_under_12_reg_bed,
            child_under_12_exb = price_child_12,
            child_under_7_exb = price_child_7,
            child_under_2_exb = price_child_2,
            from_date = start_date,
            to_date = end_date,
            rate_type_id = rate_plan.id
            )
                                            
            db.session.add(rate_plan_rates)

        # Commit only if its True
        if all_data_is_correct:
            db.session.commit()

        return redirect("/rate_plans")
    else:
        

        return render_template("rate_plans.html")
    
# Route to view the rate plans
@app.route("/view_rate_plans", methods=["GET", "POST"])
@login_required
def view_rate_plans():

    if request.method == "POST":

        delete_rate = request.form.get("delete")

        if delete_rate:
            RateType.query.filter(RateType.id == delete_rate).delete()
            RatePlan.query.filter(RatePlan.rate_type_id == delete_rate).delete()
            db.session.commit()


        return redirect("/view_rate_plans")

    else:

        rate_plans = RateType.query.all()

        headings = [
                    "Date period", 
                    "Starting date", 
                    "Ending date", 
                    "Adult", 
                    "Single adult", 
                    "Child 0-12 RB", 
                    "Child 12-17.99 Exb", 
                    "Child 7-11.99 Exb", 
                    "Child 2-6.99", 
                    "Child 0-1.99"
                ]
    
    return render_template("view_rate_plans.html", rate_plans=rate_plans, headings=headings, usd=usd)

# Availability route used to render availability calendar for selected room
@app.route("/availability", methods=["GET", "POST"])
@login_required
def availability():

    room = get_or_create_single_gite()
    all_rooms = [room]
    rate_types = RateType.query.all()

    if request.method == "POST":
    
        from_date = datetime.strptime(request.form.get("from_date"), "%d-%m-%Y")
        to_date = datetime.strptime(request.form.get("to_date"), "%d-%m-%Y")
        dates = pd.date_range(start=from_date, end=to_date)

        listed_rooms = ListedRoom.query.filter(ListedRoom.listed_date.between(from_date, to_date)).filter(ListedRoom.room_id == room.id).join(RoomAvailability).filter(RoomAvailability.listed_room_id == ListedRoom.id).all()
       
  
        return render_template("availability.html", all_rooms=all_rooms, room=room, dates=dates, listed_rooms=listed_rooms, rate_types=rate_types)

    else:

        return render_template("availability.html", all_rooms=all_rooms, rate_types=rate_types)

# Stop sale selected room for selected dates
@app.route("/stop_sale", methods=["GET", "POST"])
@login_required
def stop_sale():

    if request.method == "POST":

       
        stop_sale_start = datetime.strptime(request.form.get("start_stop_date"), "%d-%m-%Y")
        stop_sale_end = datetime.strptime(request.form.get("end_stop_date"),  "%d-%m-%Y")
        stop_sale_room = request.form.get("stop_sale_room_id")

            
        dates = pd.date_range(start=stop_sale_start, end=stop_sale_end)

        rooms = ListedRoom.query.filter(ListedRoom.listed_date.between(stop_sale_start, stop_sale_end)).filter_by(room_id=stop_sale_room).all()

        
        for room in rooms:

            rooms_availability = RoomAvailability.query.filter(RoomAvailability.listed_room_id == room.id)

            for each_room in rooms_availability:

                if request.form.get("stop_sale") == "STOP":
                    each_room.is_it_available = 0
                    print("Changed to FALSE")
                    db.session.commit()
                
                elif request.form.get("add_sale") == "ADD":
                    each_room.is_it_available = 1
                    print("Changed to TRUE")
                    db.session.commit()


        return redirect("/availability")



# Add room to availability
@app.route("/add_room", methods=["GET", "POST"])
@login_required
def add_room():

    if request.method == "POST":

        room = get_or_create_single_gite()
        room_type = room.id
        rate_name = request.form.get("rate_name")
        add_room_quantity = 1
        start_date = datetime.strptime(request.form.get("start_date"), "%d-%m-%Y")
        end_date = datetime.strptime(request.form.get("end_date"), "%d-%m-%Y")

        listed_rooms = ListedRoom.query.filter(ListedRoom.listed_date.between(start_date, end_date)).filter_by(room_id=room_type).all()

        if add_room_quantity > room.total_of_this_type:
            flash("Cannot add more than total amount!")
            return redirect("/availability")

        for listed_room in listed_rooms:

            check_dates = []
            if add_room_quantity + listed_room.quantity_per_date > room.total_of_this_type:
                check_dates.append(listed_room.listed_date)
            

            if len(check_dates) != 0:
                flash(f"Cannot add more rooms from total owned of this type {room.name} for the date {[date for date in check_dates]}") 
                return redirect("/availability")

     
        dates = pd.date_range(start=start_date, end=end_date)

        # If we have listed rooms for the selected dates
        if listed_rooms:
            
            # Update the quantity + the desired add
            for listed_room in listed_rooms:
                listed_room.quantity_per_date += add_room_quantity

            # Update room availability. Query all that == listed_room.id             
            available_rooms = []
            for listed_room in listed_rooms:
                room = RoomAvailability.query.filter(RoomAvailability.listed_room_id == listed_room.id).all()
                available_rooms.append(room) 

            # Loop and add the + new value
            for rooms in available_rooms:

                for available_room in rooms:
                    available_room.left_to_sell += add_room_quantity
                    available_room.is_it_available = 1

        # If we do not have listed rooms for the selected dates           
        if not listed_rooms:
            
            # Loop each day
            for date in dates:

                # Create listed_room obj
                listed_room = ListedRoom(
                    listed_date = date,
                    quantity_per_date = add_room_quantity,
                    rate_type_id = rate_name,
                    room_id = room_type,        
                )

                # Add and commit
                db.session.add(listed_room)
                db.session.commit()

                # Init room_availability with the created above obj.id
                available_room = RoomAvailability(
                    left_to_sell = add_room_quantity,
                    booked_quantity = 0,
                    listed_room_id = listed_room.id    
                )

                # Add it
                db.session.add(available_room)
                
        # Final commit and redirect
        db.session.commit()

        return redirect("/availability")

    else:
    
        return render_template("availability.html")

