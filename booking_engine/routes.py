from flask import flash, render_template, redirect, session, request, json, url_for
from flask_mail import Message
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from booking_engine import app, db, os, basedir, mail
from booking_engine.helpers import login_required, allowed_file
from booking_engine.room_search import single_room_search, multiple_rooms_search_no_children, multiple_rooms_search_children
from booking_engine.models import (
    Admin,
    Room,
    ListedRoom,
    RoomAvailability,
    Client,
    Reservation,
    SiteContent,
    SiteSetting,
    GalleryImage,
    Apartment,
    ApartmentImage,
    ApartmentReservation,
    ApartmentMonthlyRate,
    GuestbookEntry,
)
from booking_engine.i18n import (
    _,
    get_locale,
    set_locale,
    format_month_label,
    content_page_key,
    SUPPORTED_LANGS,
    LANG_META,
    MONTHS,
    DEFAULT_LANG,
)
from booking_engine.villa_info import (
    get_villa_info,
    VILLA_LOCATION,
    NEARBY,
    GOOD_SPOTS,
    nearby_list_to_text,
    text_to_nearby_list,
    spots_list_to_text,
    text_to_spots_list,
)
from datetime import datetime, timedelta
import calendar
import random
import uuid


CMS_DEFAULTS = {
    "home": {
        "fr": (
            "Villa Aqua Viva — Acqua Linda d'Orcino",
            "F3 dans une villa très calme, grande terrasse vue sur mer, plage à 5 minutes à pied. Idéal pour un séjour détente en couple, entre amis ou en famille.",
        ),
        "en": (
            "Villa Aqua Viva — Acqua Linda d'Orcino",
            "An F3 apartment in a very quiet villa, large sea-view terrace, beach a 5-minute walk away. Perfect for a relaxing stay as a couple, with friends or family.",
        ),
        "pt": (
            "Villa Aqua Viva — Acqua Linda d'Orcino",
            "Apartamento F3 numa villa muito calma, grande terraço com vista para o mar, praia a 5 minutos a pé. Ideal para umas férias a dois, com amigos ou em família.",
        ),
        "it": (
            "Villa Aqua Viva — Acqua Linda d'Orcino",
            "Appartamento F3 in una villa molto tranquilla, grande terrazza vista mare, spiaggia a 5 minuti a piedi. Ideale per una vacanza relax in coppia, con amici o in famiglia.",
        ),
    },
    "about": {
        "fr": (
            "Qui sommes-nous",
            "Bonjour ! Nous sommes une petite famille corse-brésilienne, avec deux enfants en bas âge. "
            "Je m’appelle Anaïs : j’ai grandi en Corse et passé tous les étés de mon enfance et de mon adolescence "
            "sur cette plage, avant de partir un peu explorer le monde. Aujourd’hui, professeure de physique, "
            "je suis extrêmement heureuse de vous faire partager une partie de mon histoire en vous accueillant "
            "dans cette grande maison — divisée en quelques appartements — construite à l’origine par mon grand-père. "
            "Mon mari Max, coach sportif de football, et moi sommes accros au sport, aux voyages et ouverts aux nouvelles rencontres.\n\n"
            "L’Acqua Linda d’Orcino offre une vue exceptionnelle sur la plage, idéale pour un séjour détente en couple, "
            "entre amis ou en famille. Le soir, après une journée sur le sable fin, profitez d’un magnifique coucher "
            "de soleil sur la grande terrasse.\n\n"
            "Nous parlons français, anglais, italien et portugais du Brésil. Nous serons ravis de vous accueillir et "
            "de vous donner nos meilleurs conseils : plages, randonnées, parapente, plongée, excursions en mer… "
            "ainsi que restaurants et bars des alentours.",
        ),
        "en": (
            "Who we are",
            "Hello! We are a small Corsican–Brazilian family with two young children. "
            "My name is Anaïs: I grew up in Corsica and spent every summer of my childhood and teenage years "
            "on this beach, before heading out to explore the world a little. Today, as a physics teacher, "
            "I am so happy to share part of my story by welcoming you into this large house — divided into a few "
            "apartments — originally built by my grandfather. My husband Max, a football coach, and I love sport, "
            "travel and meeting new people.\n\n"
            "Acqua Linda d’Orcino offers an exceptional view over the beach — perfect for a relaxing stay as a couple, "
            "with friends or family. In the evening, after a day on the fine sand, enjoy a magnificent sunset "
            "from the large terrace.\n\n"
            "We speak French, English, Italian and Brazilian Portuguese. We look forward to welcoming you and sharing "
            "our best tips: beaches, hiking, paragliding, diving, boat trips… as well as nearby restaurants and bars.",
        ),
        "pt": (
            "Quem somos",
            "Olá! Somos uma pequena família corso-brasileira, com duas crianças pequenas. "
            "Chamo-me Anaïs: cresci na Córsega e passei todos os verões da infância e da adolescência "
            "nesta praia, antes de partir um pouco a explorar o mundo. Hoje, professora de física, "
            "estou extremamente feliz por partilhar uma parte da minha história ao recebê-los nesta grande casa — "
            "dividida em alguns apartamentos — construída originalmente pelo meu avô. O meu marido Max, "
            "treinador de futebol, e eu somos apaixonados por desporto, viagens e novos encontros.\n\n"
            "A Acqua Linda d’Orcino oferece uma vista excepcional sobre a praia, ideal para umas férias a dois, "
            "com amigos ou em família. À noite, depois de um dia na areia fina, desfrute de um magnífico pôr do sol "
            "no grande terraço.\n\n"
            "Falamos francês, inglês, italiano e português do Brasil. Teremos todo o prazer em recebê-los e partilhar "
            "as nossas melhores dicas: praias, caminhadas, parapente, mergulho, passeios de barco… "
            "bem como restaurantes e bares da região.",
        ),
        "it": (
            "Chi siamo",
            "Buongiorno! Siamo una piccola famiglia corso-brasiliana, con due bambini piccoli. "
            "Mi chiamo Anaïs: sono cresciuta in Corsica e ho passato tutte le estati dell’infanzia e dell’adolescenza "
            "su questa spiaggia, prima di partire un po’ a esplorare il mondo. Oggi, insegnante di fisica, "
            "sono estremamente felice di condividere una parte della mia storia accogliendovi in questa grande casa — "
            "divisa in alcuni appartamenti — costruita in origine da mio nonno. Mio marito Max, "
            "allenatore di calcio, e io amiamo lo sport, i viaggi e i nuovi incontri.\n\n"
            "Acqua Linda d’Orcino offre una vista eccezionale sulla spiaggia, ideale per una vacanza relax in coppia, "
            "con amici o in famiglia. La sera, dopo una giornata sulla sabbia fine, godetevi un magnifico tramonto "
            "dalla grande terrazza.\n\n"
            "Parliamo francese, inglese, italiano e portoghese del Brasile. Saremo lieti di accogliervi e di darvi "
            "i nostri migliori consigli: spiagge, escursioni, parapendio, immersioni, gite in mare… "
            "nonché ristoranti e bar della zona.",
        ),
    },
    "prices": {
        "fr": ("Tarifs Aqua Viva", "Consultez nos tarifs et offres actuelles."),
        "en": ("Aqua Viva Prices", "Browse our prices and current offers."),
        "pt": ("Preços Aqua Viva", "Consulte os nossos preços e ofertas atuais."),
        "it": ("Prezzi Aqua Viva", "Consultate le nostre tariffe e le offerte attuali."),
    },
    "gallery": {
        "fr": ("Galerie Aqua Viva", "Explorez les espaces et l'ambiance de la villa."),
        "en": ("Aqua Viva Gallery", "Explore our spaces and atmosphere."),
        "pt": ("Galeria Aqua Viva", "Explore os espaços e o ambiente da villa."),
        "it": ("Galleria Aqua Viva", "Esplorate gli spazi e l’atmosfera della villa."),
    },
    "location": {
        lang: (loc["title"], f"{loc['place']}\n{loc['region']}\n{loc['summary']}")
        for lang, loc in VILLA_LOCATION.items()
    },
    "spots": {
        lang: (spots["title"], spots["intro"]) for lang, spots in GOOD_SPOTS.items()
    },
}


_CMS_READY = False
_SETTING_DEFAULTS = {
    "banner_image": "images/banner-5.png",
    "home_background_image": "",
    "home_slider_ids": "",
    "home_slider_mode": "selected",
    "about_image": "",
    "site_phone": "+55 11 94340-1825",
    "site_email": "anaisacquaviva@gmail.com",
    "site_logo": "images/villa-aqua-viva-postcard.png",
}


def get_settings(*keys):
    """Batch-load SiteSetting values with defaults."""
    if not keys:
        return {}
    rows = SiteSetting.query.filter(SiteSetting.setting_key.in_(keys)).all()
    found = {row.setting_key: row.setting_value for row in rows}
    return {key: found.get(key, _SETTING_DEFAULTS.get(key, "")) for key in keys}


def ensure_cms_defaults():
    global _CMS_READY
    if _CMS_READY:
        return
    db.create_all()

    existing_pages = {row.page_key for row in SiteContent.query.with_entities(SiteContent.page_key).all()}
    for page_base, lang_map in CMS_DEFAULTS.items():
        for lang, values in lang_map.items():
            page_key = content_page_key(page_base, lang)
            if page_key not in existing_pages:
                db.session.add(SiteContent(page_key=page_key, title=values[0], body=values[1]))
                existing_pages.add(page_key)
        if page_base not in existing_pages:
            en_vals = lang_map.get("en") or next(iter(lang_map.values()))
            db.session.add(SiteContent(page_key=page_base, title=en_vals[0], body=en_vals[1]))
            existing_pages.add(page_base)

    existing_settings = {
        row.setting_key
        for row in SiteSetting.query.filter(
            SiteSetting.setting_key.in_(list(_SETTING_DEFAULTS.keys()))
        ).all()
    }
    for key, value in _SETTING_DEFAULTS.items():
        if key not in existing_settings:
            db.session.add(SiteSetting(setting_key=key, setting_value=value))

    nearby_spots_keys = [f"nearby_list_{lang}" for lang in SUPPORTED_LANGS] + [
        f"spots_list_{lang}" for lang in SUPPORTED_LANGS
    ]
    existing_lists = {
        row.setting_key
        for row in SiteSetting.query.filter(SiteSetting.setting_key.in_(nearby_spots_keys)).all()
    }
    for lang in SUPPORTED_LANGS:
        nearby_key = f"nearby_list_{lang}"
        if nearby_key not in existing_lists:
            nearby = NEARBY.get(lang, NEARBY["fr"])
            db.session.add(
                SiteSetting(
                    setting_key=nearby_key,
                    setting_value=json.dumps(
                        {"title": nearby["title"], "list": nearby["list"]},
                        ensure_ascii=False,
                    ),
                )
            )
        spots_key = f"spots_list_{lang}"
        if spots_key not in existing_lists:
            spots = GOOD_SPOTS.get(lang, GOOD_SPOTS["fr"])
            db.session.add(
                SiteSetting(
                    setting_key=spots_key,
                    setting_value=json.dumps(spots["list"], ensure_ascii=False),
                )
            )

    db.session.commit()
    _CMS_READY = True


def get_site_contents(*page_keys):
    """Load several CMS pages for the current locale in one query."""
    lang = get_locale()
    lookup_keys = []
    for page_key in page_keys:
        lookup_keys.append(content_page_key(page_key, lang))
        lookup_keys.append(page_key)
    rows = {
        row.page_key: row
        for row in SiteContent.query.filter(SiteContent.page_key.in_(lookup_keys)).all()
    }
    result = {}
    for page_key in page_keys:
        content = rows.get(content_page_key(page_key, lang)) or rows.get(page_key)
        result[page_key] = (
            {"title": content.title, "body": content.body}
            if content
            else {"title": "", "body": ""}
        )
    return result


def get_site_content(page_key):
    return get_site_contents(page_key)[page_key]


def _cms_save_uploaded_setting(file_field, setting_key, ok_msg, bad_msg):
    upload = request.files.get(file_field)
    if upload and allowed_file(upload.filename):
        filename = secure_filename(upload.filename)
        if filename:
            upload.save(os.path.join(basedir, app.config["UPLOAD_FOLDER"], filename))
            setting = SiteSetting.query.filter_by(setting_key=setting_key).first()
            if setting:
                setting.setting_value = f"uploads/{filename}"
                db.session.commit()
                flash(ok_msg)
            return redirect("/cms")
    flash(bad_msg)
    return redirect("/cms")


@app.context_processor
def inject_i18n():
    return {
        "_": _,
        "current_lang": get_locale(),
        "supported_langs": SUPPORTED_LANGS,
        "lang_meta": LANG_META,
    }


@app.route("/set_language/<lang>", methods=["GET"])
def set_language(lang):
    set_locale(lang)
    referrer = request.referrer
    if referrer and referrer.startswith(request.host_url):
        return redirect(referrer)
    return redirect("/")


@app.context_processor
def inject_site_banner():
    settings = get_settings("site_phone", "site_email", "site_logo", "banner_image")
    context = {
        "site_phone": settings["site_phone"],
        "site_email": settings["site_email"],
        "site_logo_path": settings["site_logo"],
        "site_whatsapp_url": "https://wa.me/5511943401825",
        "site_banner_path": "",
    }
    if request.path not in ("/", "/cms/preview"):
        context["site_banner_path"] = settings["banner_image"]
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


def parse_month_param(month_param):
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

    if month_start.month == 1:
        prev_month_start = month_start.replace(year=month_start.year - 1, month=12, day=1)
    else:
        prev_month_start = month_start.replace(month=month_start.month - 1, day=1)

    return today, month_start, prev_month_start, next_month_start


def build_apartment_calendar_maps(apartment, month_start, next_month_start=None):
    """Build occupancy maps for one apartment calendar month.

    When next_month_start is set, only overlapping reservations are loaded.
    """
    query = ApartmentReservation.query.filter_by(apartment_id=apartment.id)
    if next_month_start is not None:
        query = query.filter(
            ApartmentReservation.check_out > month_start,
            ApartmentReservation.check_in < next_month_start,
        )
    reservations = query.all()
    checkin_map = {}
    checkout_map = {}
    occupied_dates = set()
    occupied_map = {}

    for res in reservations:
        check_in_date = res.check_in.date() if hasattr(res.check_in, "date") else res.check_in
        check_out_date = res.check_out.date() if hasattr(res.check_out, "date") else res.check_out
        checkin_map[check_in_date] = res
        checkout_map[check_out_date] = res
        current = check_in_date
        while current < check_out_date:
            occupied_dates.add(current)
            occupied_map[current] = res
            current += timedelta(days=1)

    cal = calendar.Calendar(firstweekday=0)
    month_weeks = cal.monthdatescalendar(month_start.year, month_start.month)
    return {
        "month_weeks": month_weeks,
        "checkin_map": checkin_map,
        "checkout_map": checkout_map,
        "occupied_dates": occupied_dates,
        "occupied_map": occupied_map,
        "reservations": reservations,
    }


def apartment_period_is_free(apartment_id, check_in, check_out, exclude_id=None):
    """True if [check_in, check_out) does not overlap existing reservations."""
    query = ApartmentReservation.query.filter(
        ApartmentReservation.apartment_id == apartment_id,
        ApartmentReservation.check_in < check_out,
        ApartmentReservation.check_out > check_in,
    )
    if exclude_id:
        query = query.filter(ApartmentReservation.id != exclude_id)
    return query.first() is None


def get_apartment_rate_for_month(apartment, year, month, monthly_rates=None):
    """Effective nightly rate for a given month (monthly override or default)."""
    if monthly_rates is None:
        override = ApartmentMonthlyRate.query.filter_by(
            apartment_id=apartment.id, year=year, month=month
        ).first()
        if override:
            return override.rate, True
        return apartment.rate, False
    override = monthly_rates.get(month)
    if override is not None:
        return override, True
    return apartment.rate, False


def load_apartment_monthly_rates(apartment_id, year):
    rows = ApartmentMonthlyRate.query.filter_by(apartment_id=apartment_id, year=year).all()
    return {row.month: row.rate for row in rows}


def ensure_room_availability_rows(room, start_date, end_date):
    """Ensure listed_room and availability rows exist for each date."""
    existing = {
        lr.listed_date
        for lr in ListedRoom.query.filter(
            ListedRoom.room_id == room.id,
            ListedRoom.listed_date.between(start_date, end_date),
        ).all()
    }
    day = timedelta(days=1)
    current = start_date
    while current <= end_date:
        if current not in existing:
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


def _inclusive_dates(start_dt, end_dt):
    dates = []
    current = start_dt
    while current <= end_dt:
        dates.append(current)
        current += timedelta(days=1)
    return dates


# Main index from where the client performs the search
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        ensure_cms_defaults()
        gite = get_or_create_single_gite()
            
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
    return render_template("index.html", **_home_page_context())


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
    # Preserve language across login; session.clear() otherwise drops CMS locale.
    preserved_lang = session.get("lang")
    session.clear()
    if preserved_lang in SUPPORTED_LANGS:
        session["lang"] = preserved_lang

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
        host = (request.host or "").split(":")[0].lower()
        is_localhost = host in ("127.0.0.1", "localhost", "::1")
        return render_template("admin_login.html", is_localhost=is_localhost)

    
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

# Legacy reservations panel — redirected to apartment availability/rates
@app.route("/admin_panel", methods=["GET", "POST"])
@login_required
def admin_panel():
    return redirect("/availability")


@app.route("/admin_manual_reservation", methods=["POST"])
@login_required
def admin_manual_reservation():
    return redirect("/availability")


@app.route("/cms", methods=["GET", "POST"])
@login_required
def cms():
    ensure_cms_defaults()

    if request.method == "POST":
        action = request.form.get("action")

        if action == "update_content":
            lang = get_locale()
            pages = ("home", "about", "prices", "gallery")
            updated = []
            for page_key in pages:
                title = request.form.get(f"{page_key}_title")
                body = request.form.get(f"{page_key}_body")
                if title is None and body is None:
                    continue
                key = content_page_key(page_key, lang)
                page = SiteContent.query.filter_by(page_key=key).first()
                if not page:
                    page = SiteContent(page_key=key, title="", body="")
                    db.session.add(page)
                if title is not None:
                    page.title = title.strip()
                if body is not None:
                    page.body = body.strip()
                updated.append(page_key)
            db.session.commit()
            if updated:
                lang_label = LANG_META.get(lang, {}).get("label", lang)
                flash(f"Textes enregistrés ({', '.join(updated)}) — langue : {lang_label}.")
                anchor = {
                    "home": "#section-intro",
                    "about": "#section-about",
                    "prices": "#section-prices",
                }.get(updated[0], "")
                return redirect(f"/cms{anchor}")
            flash("Aucun texte à enregistrer.")
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
            return _cms_save_uploaded_setting(
                "banner_image", "banner_image", "Banner updated.", "Unsupported banner file."
            )

        if action == "upload_home_background":
            return _cms_save_uploaded_setting(
                "home_bg_image",
                "home_background_image",
                "Home background updated.",
                "Unsupported home background file.",
            )

        if action == "upload_about_image":
            return _cms_save_uploaded_setting(
                "about_image", "about_image", "About image updated.", "Unsupported about image file."
            )

        if action == "upload_logo":
            return _cms_save_uploaded_setting(
                "site_logo", "site_logo", "Logo updated.", "Unsupported logo file."
            )

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
            setting.setting_value = ",".join(str(i) for i in ids)
            db.session.commit()
            flash("Home slider selection updated.")
            return redirect("/cms#section-intro")

        if action == "delete_gallery":
            image_id = request.form.get("image_id")
            image = GalleryImage.query.filter_by(id=image_id).first()
            if image:
                db.session.delete(image)
                db.session.commit()
                flash("Gallery image removed.")
            return redirect("/cms")

        if action == "update_location_section":
            lang = get_locale()
            key = content_page_key("location", lang)
            page = SiteContent.query.filter_by(page_key=key).first()
            if not page:
                page = SiteContent(page_key=key, title="", body="")
                db.session.add(page)
            page.title = (request.form.get("location_title") or "").strip()
            place = (request.form.get("location_place") or "").strip()
            region = (request.form.get("location_region") or "").strip()
            summary = (request.form.get("location_summary") or "").strip()
            page.body = f"{place}\n{region}\n{summary}"

            nearby_title = (request.form.get("nearby_title") or "").strip()
            nearby_list = text_to_nearby_list(request.form.get("nearby_list_text"))
            nearby_key = f"nearby_list_{lang}"
            nearby_row = SiteSetting.query.filter_by(setting_key=nearby_key).first()
            payload = json.dumps(
                {"title": nearby_title or "À proximité", "list": nearby_list},
                ensure_ascii=False,
            )
            if not nearby_row:
                db.session.add(SiteSetting(setting_key=nearby_key, setting_value=payload))
            else:
                nearby_row.setting_value = payload
            db.session.commit()
            flash(f"Section Localisation enregistrée ({LANG_META.get(lang, {}).get('label', lang)}).")
            return redirect("/cms#section-localisation")

        if action == "update_spots_section":
            lang = get_locale()
            key = content_page_key("spots", lang)
            page = SiteContent.query.filter_by(page_key=key).first()
            if not page:
                page = SiteContent(page_key=key, title="", body="")
                db.session.add(page)
            page.title = (request.form.get("spots_title") or "").strip()
            page.body = (request.form.get("spots_intro") or "").strip()

            spots_list = text_to_spots_list(request.form.get("spots_list_text"))
            spots_key = f"spots_list_{lang}"
            spots_row = SiteSetting.query.filter_by(setting_key=spots_key).first()
            payload = json.dumps(spots_list, ensure_ascii=False)
            if not spots_row:
                db.session.add(SiteSetting(setting_key=spots_key, setting_value=payload))
            else:
                spots_row.setting_value = payload
            db.session.commit()
            flash(f"Section Bonnes adresses enregistrée ({LANG_META.get(lang, {}).get('label', lang)}).")
            return redirect("/cms#section-spots")

        if action == "approve_guestbook":
            entry_id = request.form.get("entry_id")
            entry = GuestbookEntry.query.filter_by(id=entry_id).first()
            if entry:
                entry.is_approved = True
                db.session.commit()
                flash("Message du livre d’or approuvé.")
            return redirect("/cms#section-guestbook")

        if action == "delete_guestbook":
            entry_id = request.form.get("entry_id")
            entry = GuestbookEntry.query.filter_by(id=entry_id).first()
            if entry:
                db.session.delete(entry)
                db.session.commit()
                flash("Message du livre d’or supprimé.")
            return redirect("/cms#section-guestbook")

    page_keys = ("home", "about", "prices", "gallery", "location", "spots")
    lang = get_locale()
    contents = {}
    for k in page_keys:
        page = SiteContent.query.filter_by(page_key=content_page_key(k, lang)).first()
        if not page:
            page = SiteContent.query.filter_by(page_key=k).first()
        contents[k] = page
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

    villa = get_villa_info()
    location_place = villa["location"].get("place", "")
    location_region = villa["location"].get("region", "")
    location_summary = villa["location"].get("summary", "")
    if contents.get("location") and contents["location"].body:
        parts = contents["location"].body.split("\n", 2)
        if len(parts) >= 1:
            location_place = parts[0]
        if len(parts) >= 2:
            location_region = parts[1]
        if len(parts) >= 3:
            location_summary = parts[2]

    guestbook_pending = (
        GuestbookEntry.query.filter_by(is_approved=False)
        .order_by(GuestbookEntry.created_at.desc())
        .all()
    )
    guestbook_approved = (
        GuestbookEntry.query.filter_by(is_approved=True)
        .order_by(GuestbookEntry.created_at.desc())
        .limit(30)
        .all()
    )

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
        nearby_title=villa["nearby"].get("title", ""),
        nearby_list_text=nearby_list_to_text(villa["nearby"]),
        spots_list_text=spots_list_to_text(villa["good_spots"]),
        location_place=location_place,
        location_region=location_region,
        location_summary=location_summary,
        preview_url=url_for("cms_preview_home"),
        guestbook_pending=guestbook_pending,
        guestbook_approved=guestbook_approved,
    )


def _home_page_context():
    """Shared context for public home and CMS preview."""
    ensure_cms_defaults()
    apartments = Apartment.query.order_by(Apartment.name.asc()).all()
    settings = get_settings("home_slider_ids", "about_image")
    selected_ids = []
    for raw in (settings["home_slider_ids"] or "").split(","):
        raw = raw.strip()
        if raw.isdigit():
            selected_ids.append(int(raw))
    all_images = GalleryImage.query.order_by(GalleryImage.created_at.desc()).all()
    if selected_ids:
        selected_map = {img.id: img for img in all_images}
        hero_images = [selected_map[i] for i in selected_ids if i in selected_map]
    else:
        hero_images = all_images
    guestbook_entries = (
        GuestbookEntry.query.filter_by(is_approved=True)
        .order_by(GuestbookEntry.created_at.desc())
        .limit(12)
        .all()
    )
    contents = get_site_contents("home", "about")
    return {
        "home_content": contents["home"],
        "about_content": contents["about"],
        "about_image_path": settings["about_image"],
        "apartments": apartments,
        "hero_images": hero_images,
        "villa": get_villa_info(),
        "guestbook_entries": guestbook_entries,
    }


@app.route("/cms/preview", methods=["GET"])
@login_required
def cms_preview_home():
    """Admin-only live preview of the public homepage."""
    ctx = _home_page_context()
    ctx["preview_mode"] = True
    return render_template("index.html", **ctx)


@app.route("/guestbook", methods=["POST"])
def guestbook_submit():
    name = (request.form.get("author_name") or "").strip()
    city = (request.form.get("author_city") or "").strip()
    message = (request.form.get("message") or "").strip()
    rating_raw = (request.form.get("rating") or "").strip()
    rating = int(rating_raw) if rating_raw.isdigit() and 1 <= int(rating_raw) <= 5 else None
    if not name or not message:
        flash(_("guestbook.required"))
        return redirect(url_for("index") + "#livre-dor")
    if len(message) > 800:
        message = message[:800]
    db.session.add(
        GuestbookEntry(
            author_name=name[:100],
            author_city=city[:100] if city else None,
            message=message,
            rating=rating,
            is_approved=False,
        )
    )
    db.session.commit()
    flash(_("guestbook.thanks"))
    return redirect(url_for("index") + "#livre-dor")


@app.route("/robots.txt")
def robots_txt():
    body = (
        "User-agent: *\n"
        "Allow: /\n"
        "Disallow: /admin_login\n"
        "Disallow: /admin_panel\n"
        "Disallow: /cms\n"
        "Disallow: /cms/preview\n"
        "Disallow: /manage_apartments\n"
        "Disallow: /availability\n"
        f"Sitemap: {url_for('sitemap_xml', _external=True)}\n"
    )
    return app.response_class(body, mimetype="text/plain")


@app.route("/sitemap.xml")
def sitemap_xml():
    pages = [
        url_for("index", _external=True),
        url_for("apartments_public", _external=True),
        url_for("prices", _external=True),
        url_for("about", _external=True),
    ]
    urls = "".join(
        f"<url><loc>{page}</loc><changefreq>weekly</changefreq><priority>0.8</priority></url>"
        for page in pages
    )
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        f"{urls}</urlset>"
    )
    return app.response_class(xml, mimetype="application/xml")


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


def _save_apartment_photos(apartment, files, caption=None):
    """Save uploaded files and attach them to an apartment. Returns count saved."""
    added = 0
    for photo in files:
        if not photo or not allowed_file(photo.filename):
            continue
        original = secure_filename(photo.filename)
        if not original:
            continue
        filename = f"{uuid.uuid4().hex}_{original}"
        photo.save(os.path.join(basedir, app.config["UPLOAD_FOLDER"], filename))
        db.session.add(
            ApartmentImage(
                apartment_id=apartment.id,
                image_file=f"uploads/{filename}",
                caption=caption,
            )
        )
        added += 1
    return added


@app.route("/apartments", methods=["GET"])
def apartments_public():
    ensure_cms_defaults()
    apartments = Apartment.query.order_by(Apartment.name.asc()).all()
    today, month_start, prev_month_start, next_month_start = parse_month_param(
        request.args.get("month")
    )
    calendars = []
    for apartment in apartments:
        maps = build_apartment_calendar_maps(apartment, month_start, next_month_start)
        month_rates = load_apartment_monthly_rates(apartment.id, month_start.year)
        effective_rate, is_monthly_override = get_apartment_rate_for_month(
            apartment, month_start.year, month_start.month, month_rates
        )
        calendars.append(
            {
                "apartment": apartment,
                "month_weeks": maps["month_weeks"],
                "checkin_map": maps["checkin_map"],
                "checkout_map": maps["checkout_map"],
                "occupied_dates": maps["occupied_dates"],
                "occupied_map": maps["occupied_map"],
                "effective_rate": effective_rate,
                "is_monthly_override": is_monthly_override,
            }
        )
    return render_template(
        "apartments_public.html",
        apartments=apartments,
        calendars=calendars,
        today=today,
        month_label=format_month_label(month_start),
        prev_month=prev_month_start.strftime("%Y-%m"),
        next_month=next_month_start.strftime("%Y-%m"),
        current_month=month_start.month,
        villa=get_villa_info(),
    )


@app.route("/manage_apartments", methods=["GET", "POST"])
@login_required
def manage_apartments():
    ensure_cms_defaults()

    if request.method == "POST":
        action = request.form.get("action")

        if action == "create":
            name = (request.form.get("name") or "").strip()
            bedrooms_raw = request.form.get("bedrooms")
            rate_raw = request.form.get("rate")
            description = (request.form.get("description") or "").strip()

            if not name:
                flash("Le nom de l'appartement est requis.")
                return redirect("/manage_apartments")
            if Apartment.query.filter_by(name=name).first():
                flash("Un appartement avec ce nom existe déjà.")
                return redirect("/manage_apartments")
            try:
                bedrooms = int(bedrooms_raw)
                rate = int(rate_raw)
            except (TypeError, ValueError):
                flash("Nombre de chambres et tarif doivent être des nombres entiers.")
                return redirect("/manage_apartments")
            if bedrooms < 1 or rate < 0:
                flash("Vérifiez le nombre de chambres et le tarif.")
                return redirect("/manage_apartments")

            apartment = Apartment(
                name=name,
                bedrooms=bedrooms,
                rate=rate,
                description=description or None,
            )
            db.session.add(apartment)
            db.session.flush()
            added = _save_apartment_photos(
                apartment,
                request.files.getlist("photos"),
                caption=request.form.get("photo_caption"),
            )
            db.session.commit()
            flash(
                f"Appartement « {name} » créé"
                + (f" avec {added} photo(s)." if added else ".")
            )
            return redirect("/manage_apartments")

        if action == "update":
            apartment_id = request.form.get("apartment_id")
            apartment = Apartment.query.filter_by(id=apartment_id).first()
            if not apartment:
                flash("Appartement introuvable.")
                return redirect("/manage_apartments")

            name = (request.form.get("name") or "").strip()
            bedrooms_raw = request.form.get("bedrooms")
            rate_raw = request.form.get("rate")
            description = (request.form.get("description") or "").strip()

            if not name:
                flash("Le nom de l'appartement est requis.")
                return redirect("/manage_apartments")
            duplicate = Apartment.query.filter(
                Apartment.name == name, Apartment.id != apartment.id
            ).first()
            if duplicate:
                flash("Un autre appartement utilise déjà ce nom.")
                return redirect("/manage_apartments")
            try:
                bedrooms = int(bedrooms_raw)
                rate = int(rate_raw)
            except (TypeError, ValueError):
                flash("Nombre de chambres et tarif doivent être des nombres entiers.")
                return redirect("/manage_apartments")
            if bedrooms < 1 or rate < 0:
                flash("Vérifiez le nombre de chambres et le tarif.")
                return redirect("/manage_apartments")

            apartment.name = name
            apartment.bedrooms = bedrooms
            apartment.rate = rate
            apartment.description = description or None
            db.session.commit()
            flash(f"Appartement « {name} » mis à jour.")
            return redirect("/manage_apartments")

        if action == "add_photos":
            apartment_id = request.form.get("apartment_id")
            apartment = Apartment.query.filter_by(id=apartment_id).first()
            if not apartment:
                flash("Appartement introuvable.")
                return redirect("/manage_apartments")
            added = _save_apartment_photos(
                apartment,
                request.files.getlist("photos"),
                caption=request.form.get("photo_caption"),
            )
            if added:
                db.session.commit()
                flash(f"{added} photo(s) ajoutée(s) à « {apartment.name} ».")
            else:
                flash("Aucune photo valide sélectionnée.")
            return redirect("/manage_apartments")

        if action == "delete_photo":
            image_id = request.form.get("image_id")
            image = ApartmentImage.query.filter_by(id=image_id).first()
            if image:
                db.session.delete(image)
                db.session.commit()
                flash("Photo supprimée.")
            return redirect("/manage_apartments")

        if action == "delete":
            apartment_id = request.form.get("apartment_id")
            apartment = Apartment.query.filter_by(id=apartment_id).first()
            if apartment:
                name = apartment.name
                db.session.delete(apartment)
                db.session.commit()
                flash(f"Appartement « {name} » supprimé.")
            return redirect("/manage_apartments")

    apartments = Apartment.query.order_by(Apartment.name.asc()).all()
    return render_template("manage_apartments.html", apartments=apartments)


# This route handles rate plans creation
@app.route("/rate_plans", methods=["GET", "POST"])
@login_required
def rate_plans():
    return redirect("/availability")


@app.route("/view_rate_plans", methods=["GET", "POST"])
@login_required
def view_rate_plans():
    return redirect("/availability")


# Availability: one calendar per apartment + admin booking entry
@app.route("/availability", methods=["GET", "POST"])
@login_required
def availability():
    ensure_cms_defaults()
    apartments = Apartment.query.order_by(Apartment.name.asc()).all()
    today, month_start, prev_month_start, next_month_start = parse_month_param(
        request.args.get("month")
    )

    rates_year = month_start.year
    year_param = request.args.get("year")
    if year_param and year_param.isdigit():
        rates_year = int(year_param)

    month_names = MONTHS.get(get_locale(), MONTHS[DEFAULT_LANG])

    calendars = []
    for apartment in apartments:
        maps = build_apartment_calendar_maps(apartment, month_start)
        monthly_rates = load_apartment_monthly_rates(apartment.id, rates_year)
        month_rates = (
            monthly_rates
            if rates_year == month_start.year
            else load_apartment_monthly_rates(apartment.id, month_start.year)
        )
        effective_rate, is_monthly_override = get_apartment_rate_for_month(
            apartment, month_start.year, month_start.month, month_rates
        )
        year_rates = []
        for m in range(1, 13):
            rate, is_override = get_apartment_rate_for_month(
                apartment, rates_year, m, monthly_rates
            )
            year_rates.append(
                {
                    "month": m,
                    "name": month_names[m - 1].capitalize(),
                    "rate": rate,
                    "is_override": is_override,
                    "override_rate": rate if is_override else "",
                }
            )
        calendars.append(
            {
                "apartment": apartment,
                "month_weeks": maps["month_weeks"],
                "checkin_map": maps["checkin_map"],
                "checkout_map": maps["checkout_map"],
                "occupied_dates": maps["occupied_dates"],
                "occupied_map": maps["occupied_map"],
                "reservations": sorted(
                    maps["reservations"],
                    key=lambda r: r.check_in,
                    reverse=True,
                ),
                "effective_rate": effective_rate,
                "is_monthly_override": is_monthly_override,
                "year_rates": year_rates,
            }
        )

    return render_template(
        "availability.html",
        calendars=calendars,
        apartments=apartments,
        today=today,
        month_label=format_month_label(month_start),
        prev_month=prev_month_start.strftime("%Y-%m"),
        next_month=next_month_start.strftime("%Y-%m"),
        current_month=month_start.month,
        current_year=month_start.year,
        current_month_query=month_start.strftime("%Y-%m"),
        rates_year=rates_year,
        prev_rates_year=rates_year - 1,
        next_rates_year=rates_year + 1,
    )


@app.route("/apartment_rates", methods=["POST"])
@login_required
def apartment_rates():
    ensure_cms_defaults()
    return_month = request.form.get("return_month") or datetime.now().strftime("%Y-%m")
    rates_year = request.form.get("rates_year")
    redirect_url = f"/availability?month={return_month}"
    if rates_year and str(rates_year).isdigit():
        redirect_url += f"&year={rates_year}"

    apartment_id = request.form.get("apartment_id")
    apartment = Apartment.query.filter_by(id=apartment_id).first()
    if not apartment:
        flash("Appartement introuvable.")
        return redirect(redirect_url)

    action = request.form.get("action")

    if action == "update_default_rate":
        try:
            rate = int(request.form.get("default_rate"))
        except (TypeError, ValueError):
            flash("Tarif par défaut invalide.")
            return redirect(f"{redirect_url}#apt-{apartment.id}")
        if rate < 0:
            flash("Le tarif ne peut pas être négatif.")
            return redirect(f"{redirect_url}#apt-{apartment.id}")
        apartment.rate = rate
        db.session.commit()
        flash(f"Tarif par défaut mis à jour pour « {apartment.name} ».")
        return redirect(f"{redirect_url}#apt-{apartment.id}")

    if action == "update_year_rates":
        try:
            year = int(request.form.get("year"))
        except (TypeError, ValueError):
            flash("Année invalide.")
            return redirect(f"{redirect_url}#apt-{apartment.id}")

        updated = 0
        cleared = 0
        for m in range(1, 13):
            raw = (request.form.get(f"rate_{m}") or "").strip()
            override = ApartmentMonthlyRate.query.filter_by(
                apartment_id=apartment.id, year=year, month=m
            ).first()
            if raw == "":
                if override:
                    db.session.delete(override)
                    cleared += 1
                continue
            try:
                rate = int(raw)
            except ValueError:
                flash(f"Tarif invalide pour le mois {m}.")
                return redirect(f"{redirect_url}#apt-{apartment.id}")
            if rate < 0:
                flash(f"Tarif négatif pour le mois {m}.")
                return redirect(f"{redirect_url}#apt-{apartment.id}")
            if override:
                override.rate = rate
            else:
                db.session.add(
                    ApartmentMonthlyRate(
                        apartment_id=apartment.id,
                        year=year,
                        month=m,
                        rate=rate,
                    )
                )
            updated += 1

        db.session.commit()
        flash(
            f"Tarifs {year} enregistrés pour « {apartment.name} » "
            f"({updated} mois définis, {cleared} remis au défaut)."
        )
        return redirect(f"{redirect_url}#apt-{apartment.id}")

    if action == "update_monthly_rate":
        try:
            year = int(request.form.get("year"))
            month = int(request.form.get("month"))
            rate = int(request.form.get("monthly_rate"))
        except (TypeError, ValueError):
            flash("Tarif mensuel invalide.")
            return redirect(f"{redirect_url}#apt-{apartment.id}")
        if month < 1 or month > 12 or rate < 0:
            flash("Vérifiez le mois et le tarif.")
            return redirect(f"{redirect_url}#apt-{apartment.id}")

        override = ApartmentMonthlyRate.query.filter_by(
            apartment_id=apartment.id, year=year, month=month
        ).first()
        if override:
            override.rate = rate
        else:
            db.session.add(
                ApartmentMonthlyRate(
                    apartment_id=apartment.id,
                    year=year,
                    month=month,
                    rate=rate,
                )
            )
        db.session.commit()
        flash(f"Tarif de {month:02d}/{year} mis à jour pour « {apartment.name} ».")
        return redirect(f"{redirect_url}#apt-{apartment.id}")

    if action == "clear_monthly_rate":
        try:
            year = int(request.form.get("year"))
            month = int(request.form.get("month"))
        except (TypeError, ValueError):
            flash("Mois invalide.")
            return redirect(f"{redirect_url}#apt-{apartment.id}")
        override = ApartmentMonthlyRate.query.filter_by(
            apartment_id=apartment.id, year=year, month=month
        ).first()
        if override:
            db.session.delete(override)
            db.session.commit()
            flash(f"Tarif mensuel retiré — retour au tarif par défaut pour « {apartment.name} ».")
        return redirect(f"{redirect_url}#apt-{apartment.id}")

    return redirect(redirect_url)


@app.route("/apartment_reservation", methods=["POST"])
@login_required
def apartment_reservation():
    ensure_cms_defaults()
    return_month = request.form.get("return_month") or datetime.now().strftime("%Y-%m")
    redirect_url = f"/availability?month={return_month}"

    apartment_id = request.form.get("apartment_id")
    apartment = Apartment.query.filter_by(id=apartment_id).first()
    if not apartment:
        flash("Appartement introuvable.")
        return redirect(redirect_url)

    try:
        check_in = datetime.strptime(request.form.get("check_in"), "%d-%m-%Y")
        check_out = datetime.strptime(request.form.get("check_out"), "%d-%m-%Y")
    except (TypeError, ValueError):
        flash("Dates invalides. Utilisez le format jj-mm-aaaa.")
        return redirect(redirect_url)

    if check_out <= check_in:
        flash("La date de sortie doit être après la date d'entrée.")
        return redirect(redirect_url)

    if not apartment_period_is_free(apartment.id, check_in, check_out):
        flash(f"Période déjà réservée pour « {apartment.name} ».")
        return redirect(redirect_url)

    guest_name = (request.form.get("guest_name") or "").strip()
    if not guest_name:
        flash("Le nom du client est requis.")
        return redirect(redirect_url)

    reservation = ApartmentReservation(
        apartment_id=apartment.id,
        check_in=check_in,
        check_out=check_out,
        guest_name=guest_name,
        guest_email=(request.form.get("guest_email") or "").strip() or None,
        guest_phone=(request.form.get("guest_phone") or "").strip() or None,
        notes=(request.form.get("notes") or "").strip() or None,
    )
    db.session.add(reservation)
    db.session.commit()
    flash(f"Réservation ajoutée pour « {apartment.name} ».")
    return redirect(f"{redirect_url}#apt-{apartment.id}")


@app.route("/delete_apartment_reservation", methods=["POST"])
@login_required
def delete_apartment_reservation():
    return_month = request.form.get("return_month") or datetime.now().strftime("%Y-%m")
    reservation_id = request.form.get("reservation_id")
    reservation = ApartmentReservation.query.filter_by(id=reservation_id).first()
    apartment_id = reservation.apartment_id if reservation else None
    if reservation:
        db.session.delete(reservation)
        db.session.commit()
        flash("Réservation supprimée.")
    redirect_url = f"/availability?month={return_month}"
    if apartment_id:
        redirect_url += f"#apt-{apartment_id}"
    return redirect(redirect_url)


# Stop sale selected room for selected dates
@app.route("/stop_sale", methods=["GET", "POST"])
@login_required
def stop_sale():

    if request.method == "POST":

       
        stop_sale_start = datetime.strptime(request.form.get("start_stop_date"), "%d-%m-%Y")
        stop_sale_end = datetime.strptime(request.form.get("end_stop_date"),  "%d-%m-%Y")
        stop_sale_room = request.form.get("stop_sale_room_id")

        rooms = ListedRoom.query.filter(ListedRoom.listed_date.between(stop_sale_start, stop_sale_end)).filter_by(room_id=stop_sale_room).all()

        for room in rooms:
            rooms_availability = RoomAvailability.query.filter(RoomAvailability.listed_room_id == room.id)
            for each_room in rooms_availability:
                if request.form.get("stop_sale") == "STOP":
                    each_room.is_it_available = 0
                    db.session.commit()
                elif request.form.get("add_sale") == "ADD":
                    each_room.is_it_available = 1
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

     
        dates = _inclusive_dates(start_date, end_date)

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

