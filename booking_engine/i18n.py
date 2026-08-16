"""Simple session-based i18n (French, English, Portuguese, Italian)."""

from flask import session

SUPPORTED_LANGS = ("fr", "en", "pt", "it")
DEFAULT_LANG = "fr"

LANG_META = {
    "fr": {"label": "Français", "flag": "🇫🇷"},
    "en": {"label": "English", "flag": "🇬🇧"},
    "pt": {"label": "Português", "flag": "🇵🇹"},
    "it": {"label": "Italiano", "flag": "🇮🇹"},
}

MONTHS = {
    "fr": [
        "janvier", "février", "mars", "avril", "mai", "juin",
        "juillet", "août", "septembre", "octobre", "novembre", "décembre",
    ],
    "en": [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December",
    ],
    "pt": [
        "janeiro", "fevereiro", "março", "abril", "maio", "junho",
        "julho", "agosto", "setembro", "outubro", "novembro", "dezembro",
    ],
    "it": [
        "gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno",
        "luglio", "agosto", "settembre", "ottobre", "novembre", "dicembre",
    ],
}

# UI strings: key -> {lang: text}
TRANSLATIONS = {
    "nav.home": {"fr": "Accueil", "en": "Home", "pt": "Início", "it": "Home"},
    "nav.apartments": {"fr": "Appartements", "en": "Apartments", "pt": "Apartamentos", "it": "Appartamenti"},
    "nav.prices": {"fr": "Tarifs", "en": "Prices", "pt": "Preços", "it": "Prezzi"},
    "nav.about": {"fr": "Qui sommes-nous", "en": "Who we are", "pt": "Quem somos", "it": "Chi siamo"},
    "nav.login": {"fr": "Connexion", "en": "Login", "pt": "Entrar", "it": "Accedi"},
    "nav.logout": {"fr": "Déconnexion", "en": "Log out", "pt": "Sair", "it": "Esci"},
    "nav.reservations": {"fr": "Réservations", "en": "Reservations", "pt": "Reservas", "it": "Prenotazioni"},
    "nav.cms": {"fr": "CMS", "en": "CMS", "pt": "CMS", "it": "CMS"},
    "nav.rate_plans": {"fr": "Tarifs plans", "en": "Rate Plans", "pt": "Planos de tarifas", "it": "Piani tariffari"},
    "nav.create_rate": {"fr": "Créer un tarif", "en": "Create Rate Plans", "pt": "Criar tarifas", "it": "Crea tariffe"},
    "nav.view_rate": {"fr": "Voir les tarifs", "en": "View Rate plans", "pt": "Ver tarifas", "it": "Vedi tariffe"},
    "nav.availability": {
        "fr": "Disponibilité et Tarifs",
        "en": "Availability & Rates",
        "pt": "Disponibilidade e Preços",
        "it": "Disponibilità e Tariffe",
    },

    "title.home": {"fr": "Accueil", "en": "Home", "pt": "Início", "it": "Home"},
    "title.apartments": {"fr": "Appartements", "en": "Apartments", "pt": "Apartamentos", "it": "Appartamenti"},
    "title.prices": {"fr": "Tarifs", "en": "Prices", "pt": "Preços", "it": "Prezzi"},
    "title.about": {"fr": "Qui sommes-nous", "en": "Who we are", "pt": "Quem somos", "it": "Chi siamo"},
    "title.login": {"fr": "Connexion admin", "en": "Admin Login", "pt": "Login admin", "it": "Login admin"},
    "title.availability": {
        "fr": "Disponibilité et Tarifs",
        "en": "Availability & Rates",
        "pt": "Disponibilidade e Preços",
        "it": "Disponibilità e Tariffe",
    },

    "home.shortcut_about": {
        "fr": "Qui sommes-nous",
        "en": "Who we are",
        "pt": "Quem somos",
        "it": "Chi siamo",
    },
    "home.shortcut_location": {
        "fr": "Localisation",
        "en": "Location",
        "pt": "Localização",
        "it": "Posizione",
    },
    "home.shortcut_spots": {
        "fr": "Bonnes adresses",
        "en": "Good places",
        "pt": "Boas moradas",
        "it": "Buoni indirizzi",
    },
    "home.shortcut_guestbook": {
        "fr": "Livre d’or",
        "en": "Guestbook",
        "pt": "Livro de visitas",
        "it": "Libro degli ospiti",
    },
    "home.shortcut_apartments": {
        "fr": "Appartements",
        "en": "Apartments",
        "pt": "Apartamentos",
        "it": "Appartamenti",
    },
    "guestbook.heading": {
        "fr": "Livre d’or",
        "en": "Guestbook",
        "pt": "Livro de visitas",
        "it": "Libro degli ospiti",
    },
    "guestbook.intro": {
        "fr": "Les messages de nos hôtes — partagez votre séjour à la villa.",
        "en": "Messages from our guests — share your stay at the villa.",
        "pt": "Mensagens dos nossos hóspedes — partilhe a sua estadia.",
        "it": "Messaggi dei nostri ospiti — condividete il soggiorno.",
    },
    "guestbook.name": {"fr": "Votre prénom", "en": "Your first name", "pt": "O seu nome", "it": "Il tuo nome"},
    "guestbook.city": {"fr": "Ville (optionnel)", "en": "City (optional)", "pt": "Cidade (opcional)", "it": "Città (opzionale)"},
    "guestbook.message": {"fr": "Votre message", "en": "Your message", "pt": "A sua mensagem", "it": "Il tuo messaggio"},
    "guestbook.rating": {"fr": "Note", "en": "Rating", "pt": "Nota", "it": "Voto"},
    "guestbook.submit": {"fr": "Envoyer", "en": "Send", "pt": "Enviar", "it": "Invia"},
    "guestbook.thanks": {
        "fr": "Merci ! Votre message sera publié après validation.",
        "en": "Thank you! Your message will appear after approval.",
        "pt": "Obrigado! A mensagem será publicada após validação.",
        "it": "Grazie! Il messaggio sarà pubblicato dopo l’approvazione.",
    },
    "guestbook.required": {
        "fr": "Merci de remplir votre prénom et votre message.",
        "en": "Please fill in your first name and message.",
        "pt": "Por favor, preencha o seu nome e a mensagem.",
        "it": "Compila il tuo nome e il messaggio.",
    },
    "guestbook.empty": {
        "fr": "Soyez les premiers à laisser un mot.",
        "en": "Be the first to leave a note.",
        "pt": "Seja o primeiro a deixar uma mensagem.",
        "it": "Siate i primi a lasciare un messaggio.",
    },
    "nav.guestbook": {
        "fr": "Livre d’or",
        "en": "Guestbook",
        "pt": "Livro de visitas",
        "it": "Libro degli ospiti",
    },
    "footer.explore": {
        "fr": "Explorer",
        "en": "Explore",
        "pt": "Explorar",
        "it": "Esplora",
    },
    "footer.useful": {
        "fr": "Liens utiles",
        "en": "Useful links",
        "pt": "Links úteis",
        "it": "Link utili",
    },
    "footer.abritel": {
        "fr": "Annonce Abritel",
        "en": "Abritel listing",
        "pt": "Anúncio Abritel",
        "it": "Annuncio Abritel",
    },
    "footer.map": {
        "fr": "Carte OpenStreetMap",
        "en": "OpenStreetMap",
        "pt": "Mapa OpenStreetMap",
        "it": "Mappa OpenStreetMap",
    },
    "menu.open": {
        "fr": "Menu",
        "en": "Menu",
        "pt": "Menu",
        "it": "Menu",
    },
    "nav.calendars": {
        "fr": "Calendriers",
        "en": "Calendars",
        "pt": "Calendários",
        "it": "Calendari",
    },
    "nav.preview": {
        "fr": "Aperçu",
        "en": "Preview",
        "pt": "Pré-visualização",
        "it": "Anteprima",
    },
    "meta.default_description": {
        "fr": "Villa Aqua Viva à Calcatoggio, Corse — appartement vue mer, plage à 5 min, parapente, plongée et bonnes adresses.",
        "en": "Villa Aqua Viva in Calcatoggio, Corsica — sea-view apartment, beach 5 minutes away, paragliding, diving and local tips.",
        "pt": "Villa Aqua Viva em Calcatoggio, Córsega — apartamento com vista para o mar, praia a 5 min, parapente, mergulho e boas moradas.",
        "it": "Villa Aqua Viva a Calcatoggio, Corsica — appartamento vista mare, spiaggia a 5 min, parapendio, immersioni e buoni indirizzi.",
    },
    "meta.default_og_title": {
        "fr": "Villa Aqua Viva — Calcatoggio, Corse",
        "en": "Villa Aqua Viva — Calcatoggio, Corsica",
        "pt": "Villa Aqua Viva — Calcatoggio, Córsega",
        "it": "Villa Aqua Viva — Calcatoggio, Corsica",
    },
    "meta.apartments_description": {
        "fr": "Calendriers de disponibilité des appartements Villa Aqua Viva à Calcatoggio, Corse — vue mer, plage à proximité.",
        "en": "Availability calendars for Villa Aqua Viva apartments in Calcatoggio, Corsica — sea view, beach nearby.",
        "pt": "Calendários de disponibilidade dos apartamentos Villa Aqua Viva em Calcatoggio, Córsega — vista mar, praia perto.",
        "it": "Calendari di disponibilità degli appartamenti Villa Aqua Viva a Calcatoggio, Corsica — vista mare, spiaggia vicina.",
    },
    "aria.main_nav": {
        "fr": "Navigation principale",
        "en": "Main navigation",
        "pt": "Navegação principal",
        "it": "Navigazione principale",
    },
    "aria.quick_nav": {
        "fr": "Navigation rapide",
        "en": "Quick navigation",
        "pt": "Navegação rápida",
        "it": "Navigazione rapida",
    },
    "aria.back_to_top": {
        "fr": "Haut de page",
        "en": "Back to top",
        "pt": "Topo da página",
        "it": "Torna su",
    },
    "logo.alt": {
        "fr": "Villa Aqua Viva — logo carte postale",
        "en": "Villa Aqua Viva — postcard logo",
        "pt": "Villa Aqua Viva — logótipo postal",
        "it": "Villa Aqua Viva — logo cartolina",
    },
    "footer.place": {
        "fr": "Calcatoggio · Corse-du-Sud · France",
        "en": "Calcatoggio · Southern Corsica · France",
        "pt": "Calcatoggio · Córsega-do-Sul · França",
        "it": "Calcatoggio · Corsica del Sud · Francia",
    },
    "preview.banner": {
        "fr": "Mode prévisualisation admin — les visiteurs voient la même page sur l’accueil public.",
        "en": "Admin preview mode — visitors see the same page on the public home.",
        "pt": "Modo de pré-visualização admin — os visitantes veem a mesma página no início público.",
        "it": "Modalità anteprima admin — i visitatori vedono la stessa pagina nella home pubblica.",
    },
    "preview.back": {
        "fr": "← Retour au CMS",
        "en": "← Back to CMS",
        "pt": "← Voltar ao CMS",
        "it": "← Torna al CMS",
    },
    "preview.suffix": {
        "fr": " — Aperçu",
        "en": " — Preview",
        "pt": " — Pré-visualização",
        "it": " — Anteprima",
    },
    "map.iframe_title": {
        "fr": "Carte",
        "en": "Map",
        "pt": "Mapa",
        "it": "Mappa",
    },
    "about.family_alt": {
        "fr": "Famille Aqua Viva — hôtes à Calcatoggio",
        "en": "Aqua Viva family — hosts in Calcatoggio",
        "pt": "Família Aqua Viva — anfitriões em Calcatoggio",
        "it": "Famiglia Aqua Viva — host a Calcatoggio",
    },
    "seo.amenity_sea_view": {
        "fr": "Vue mer",
        "en": "Sea view",
        "pt": "Vista para o mar",
        "it": "Vista mare",
    },
    "seo.amenity_beach": {
        "fr": "Plage à proximité",
        "en": "Beach nearby",
        "pt": "Praia por perto",
        "it": "Spiaggia nelle vicinanze",
    },
    "home.read_more": {
        "fr": "Lire la suite →",
        "en": "Read more →",
        "pt": "Ler mais →",
        "it": "Leggi di più →",
    },
    "home.nearby_heading": {
        "fr": "Activités à proximité",
        "en": "Nearby activities",
        "pt": "Atividades próximas",
        "it": "Attività nelle vicinanze",
    },
    "apt.amenities": {"fr": "Équipements", "en": "Amenities", "pt": "Equipamentos", "it": "Servizi"},
    "home.apartments_heading": {
        "fr": "Nos appartements",
        "en": "Our apartments",
        "pt": "Os nossos apartamentos",
        "it": "I nostri appartamenti",
    },
    "home.no_apartments": {
        "fr": "Aucun appartement pour le moment.",
        "en": "No apartments available yet.",
        "pt": "Nenhum apartamento disponível no momento.",
        "it": "Nessun appartamento disponibile al momento.",
    },
    "home.see_calendar": {
        "fr": "Voir le calendrier →",
        "en": "See calendar →",
        "pt": "Ver calendário →",
        "it": "Vedi il calendario →",
    },
    "home.bedroom": {"fr": "chambre", "en": "bedroom", "pt": "quarto", "it": "camera"},
    "home.bedrooms": {"fr": "chambres", "en": "bedrooms", "pt": "quartos", "it": "camere"},
    "home.per_night": {"fr": "/ nuit", "en": "/ night", "pt": "/ noite", "it": "/ notte"},

    "apt.heading": {
        "fr": "Appartements à louer",
        "en": "Apartments for rent",
        "pt": "Apartamentos para alugar",
        "it": "Appartamenti in affitto",
    },
    "apt.intro": {
        "fr": "Découvrez les appartements de la villa Aqua Viva et consultez les disponibilités.",
        "en": "Discover the apartments at Villa Aqua Viva and check availability.",
        "pt": "Descubra os apartamentos da villa Aqua Viva e consulte a disponibilidade.",
        "it": "Scoprite gli appartamenti della villa Aqua Viva e consultate le disponibilità.",
    },
    "apt.prev_month": {
        "fr": "← Mois précédent",
        "en": "← Previous month",
        "pt": "← Mês anterior",
        "it": "← Mese precedente",
    },
    "apt.next_month": {
        "fr": "Mois suivant →",
        "en": "Next month →",
        "pt": "Próximo mês →",
        "it": "Mese successivo →",
    },
    "apt.free": {"fr": "Libre", "en": "Available", "pt": "Livre", "it": "Libero"},
    "apt.reserved": {"fr": "Réservé", "en": "Booked", "pt": "Reservado", "it": "Prenotato"},
    "apt.checkin": {"fr": "Entrée", "en": "Check-in", "pt": "Entrada", "it": "Check-in"},
    "apt.checkout": {"fr": "Sortie", "en": "Check-out", "pt": "Saída", "it": "Check-out"},
    "apt.calendar": {"fr": "Calendrier", "en": "Calendar", "pt": "Calendário", "it": "Calendario"},
    "apt.none": {
        "fr": "Aucun appartement n'est disponible pour le moment.",
        "en": "No apartments are available at the moment.",
        "pt": "Nenhum apartamento disponível no momento.",
        "it": "Nessun appartamento disponibile al momento.",
    },
    "apt.mon": {"fr": "Lun", "en": "Mon", "pt": "Seg", "it": "Lun"},
    "apt.tue": {"fr": "Mar", "en": "Tue", "pt": "Ter", "it": "Mar"},
    "apt.wed": {"fr": "Mer", "en": "Wed", "pt": "Qua", "it": "Mer"},
    "apt.thu": {"fr": "Jeu", "en": "Thu", "pt": "Qui", "it": "Gio"},
    "apt.fri": {"fr": "Ven", "en": "Fri", "pt": "Sex", "it": "Ven"},
    "apt.sat": {"fr": "Sam", "en": "Sat", "pt": "Sáb", "it": "Sab"},
    "apt.sun": {"fr": "Dim", "en": "Sun", "pt": "Dom", "it": "Dom"},

    "login.admin": {"fr": "Admin", "en": "Admin", "pt": "Admin", "it": "Admin"},
    "login.password": {
        "fr": "Mot de passe",
        "en": "Password",
        "pt": "Palavra-passe",
        "it": "Password",
    },
    "login.submit": {"fr": "Se connecter", "en": "Log In", "pt": "Entrar", "it": "Accedi"},

    "cms.lang_hint": {
        "fr": "Vous modifiez le contenu pour la langue :",
        "en": "You are editing content for language:",
        "pt": "Está a editar o conteúdo para o idioma:",
        "it": "Stai modificando il contenuto per la lingua:",
    },
    "footer.developed": {
        "fr": "Site développé par",
        "en": "Website developed by",
        "pt": "Site desenvolvido por",
        "it": "Sito sviluppato da",
    },
    "footer.whatsapp": {"fr": "WhatsApp", "en": "WhatsApp", "pt": "WhatsApp", "it": "WhatsApp"},
}


def get_locale():
    try:
        from flask import has_request_context, request
        if has_request_context():
            qlang = request.args.get("lang")
            if qlang in SUPPORTED_LANGS:
                session["lang"] = qlang
                return qlang
    except RuntimeError:
        pass
    lang = session.get("lang")
    if lang in SUPPORTED_LANGS:
        return lang
    return DEFAULT_LANG


def set_locale(lang):
    if lang in SUPPORTED_LANGS:
        session["lang"] = lang


def _(key, **kwargs):
    lang = get_locale()
    entry = TRANSLATIONS.get(key, {})
    text = entry.get(lang) or entry.get(DEFAULT_LANG) or key
    if kwargs:
        try:
            return text.format(**kwargs)
        except (KeyError, ValueError):
            return text
    return text


def format_month_label(date_obj):
    lang = get_locale()
    months = MONTHS.get(lang, MONTHS[DEFAULT_LANG])
    return f"{months[date_obj.month - 1].capitalize()} {date_obj.year}"


def content_page_key(base_key, lang=None):
    lang = lang or get_locale()
    return f"{base_key}_{lang}"
