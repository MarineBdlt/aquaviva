"""Simple session-based i18n (French, English, Portuguese, Italian)."""

from flask import session

SUPPORTED_LANGS = ("fr", "en", "pt", "it")
DEFAULT_LANG = "fr"

LANG_META = {
    "fr": {"label": "Français", "flag": "🇫🇷"},
    "en": {"label": "English", "flag": "🇬🇧"},
    "pt": {"label": "Português (BR)", "flag": "🇧🇷"},
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
        "fr": "Calendriers & réservations",
        "en": "Calendars & bookings",
        "pt": "Calendários e reservas",
        "it": "Calendari e prenotazioni",
    },
    "nav.admin_apartments": {
        "fr": "Appartements",
        "en": "Apartments",
        "pt": "Apartamentos",
        "it": "Appartamenti",
    },
    "title.home": {
        "fr": "Location vacances Corse",
        "en": "Corsica holiday rental",
        "pt": "Aluguel de férias Córsega",
        "it": "Affitto vacanze Corsica",
    },
    "title.apartments": {"fr": "Appartements", "en": "Apartments", "pt": "Apartamentos", "it": "Appartamenti"},
    "title.about": {"fr": "Qui sommes-nous", "en": "Who we are", "pt": "Quem somos", "it": "Chi siamo"},
    "title.login": {"fr": "Connexion admin", "en": "Admin Login", "pt": "Login admin", "it": "Login admin"},
    "title.availability": {
        "fr": "Calendriers & réservations",
        "en": "Calendars & bookings",
        "pt": "Calendários e reservas",
        "it": "Calendari e prenotazioni",
    },
    "spot.visit": {
        "fr": "Voir le site",
        "en": "Visit website",
        "pt": "Ver o site",
        "it": "Visita il sito",
    },
    "brand.name": {
        "fr": "La Casa Rosa",
        "en": "La Casa Rosa",
        "pt": "La Casa Rosa",
        "it": "La Casa Rosa",
    },
    "brand.tagline": {
        "fr": "Acqua Linda d'Orcino · Calcatoggio",
        "en": "Acqua Linda d'Orcino · Calcatoggio",
        "pt": "Acqua Linda d'Orcino · Calcatoggio",
        "it": "Acqua Linda d'Orcino · Calcatoggio",
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
        "fr": "Les messages de nos hôtes — partagez votre séjour à La Casa Rosa.",
        "en": "Messages from our guests — share your stay at La Casa Rosa.",
        "pt": "Mensagens dos nossos hóspedes — compartilhe sua estadia na La Casa Rosa.",
        "it": "Messaggi dei nostri ospiti — condividete il soggiorno a La Casa Rosa.",
    },
    "guestbook.name": {"fr": "Votre prénom", "en": "Your first name", "pt": "Seu nome", "it": "Il tuo nome"},
    "guestbook.city": {"fr": "Ville (optionnel)", "en": "City (optional)", "pt": "Cidade (opcional)", "it": "Città (opzionale)"},
    "guestbook.message": {"fr": "Votre message", "en": "Your message", "pt": "Sua mensagem", "it": "Il tuo messaggio"},
    "guestbook.rating": {"fr": "Note", "en": "Rating", "pt": "Nota", "it": "Voto"},
    "guestbook.submit": {"fr": "Envoyer", "en": "Send", "pt": "Enviar", "it": "Invia"},
    "guestbook.thanks": {
        "fr": "Merci ! Votre message sera publié après validation.",
        "en": "Thank you! Your message will appear after approval.",
        "pt": "Obrigado! Sua mensagem será publicada após validação.",
        "it": "Grazie! Il messaggio sarà pubblicato dopo l’approvazione.",
    },
    "guestbook.required": {
        "fr": "Merci de remplir votre prénom et votre message.",
        "en": "Please fill in your first name and message.",
        "pt": "Por favor, preencha seu nome e a mensagem.",
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
    "footer.airbnb": {
        "fr": "Réserver sur Airbnb",
        "en": "Book on Airbnb",
        "pt": "Reservar no Airbnb",
        "it": "Prenota su Airbnb",
    },
    "cta.book_airbnb": {
        "fr": "Réserver sur Airbnb",
        "en": "Book on Airbnb",
        "pt": "Reservar no Airbnb",
        "it": "Prenota su Airbnb",
    },
    "cta.book_online": {
        "fr": "Réserver en ligne",
        "en": "Book online",
        "pt": "Reservar online",
        "it": "Prenota online",
    },
    "cta.book_hint": {
        "fr": "Laissez-nous un message — nous vous répondons rapidement.",
        "en": "Leave us a message — we reply quickly.",
        "pt": "Deixe-nos uma mensagem — respondemos rápido.",
        "it": "Lasciateci un messaggio — rispondiamo in fretta.",
    },
    "book.title": {
        "fr": "Réserver en ligne",
        "en": "Book online",
        "pt": "Reservar online",
        "it": "Prenota online",
    },
    "book.intro": {
        "fr": "Envoyez votre demande de séjour. Vous pouvez aussi nous appeler directement.",
        "en": "Send your stay enquiry. You can also call us directly.",
        "pt": "Envie seu pedido de estadia. Você também pode nos ligar diretamente.",
        "it": "Inviate la richiesta di soggiorno. Potete anche chiamarci direttamente.",
    },
    "book.call": {
        "fr": "Appeler",
        "en": "Call",
        "pt": "Ligar",
        "it": "Chiama",
    },
    "book.name": {"fr": "Votre nom", "en": "Your name", "pt": "Seu nome", "it": "Il tuo nome"},
    "book.email": {"fr": "E-mail", "en": "Email", "pt": "E-mail", "it": "Email"},
    "book.phone": {"fr": "Téléphone", "en": "Phone", "pt": "Telefone", "it": "Telefono"},
    "book.apartment": {
        "fr": "Appartement souhaité",
        "en": "Preferred apartment",
        "pt": "Apartamento desejado",
        "it": "Appartamento desiderato",
    },
    "book.apartment_any": {
        "fr": "Pas encore choisi",
        "en": "Not chosen yet",
        "pt": "Ainda não escolhido",
        "it": "Non ancora scelto",
    },
    "book.check_in": {"fr": "Arrivée", "en": "Check-in", "pt": "Chegada", "it": "Arrivo"},
    "book.check_out": {"fr": "Départ", "en": "Check-out", "pt": "Partida", "it": "Partenza"},
    "book.message": {"fr": "Votre message", "en": "Your message", "pt": "Sua mensagem", "it": "Il tuo messaggio"},
    "book.submit": {"fr": "Envoyer la demande", "en": "Send enquiry", "pt": "Enviar pedido", "it": "Invia richiesta"},
    "book.required": {
        "fr": "Nom, e-mail et message sont requis.",
        "en": "Name, email and message are required.",
        "pt": "Nome, e-mail e mensagem são obrigatórios.",
        "it": "Nome, email e messaggio sono obbligatori.",
    },
    "book.thanks": {
        "fr": "Merci ! Votre demande a bien été envoyée.",
        "en": "Thank you! Your enquiry has been sent.",
        "pt": "Obrigado! Seu pedido foi enviado.",
        "it": "Grazie! La richiesta è stata inviata.",
    },
    "book.no_email": {
        "fr": "Adresse e-mail du site non configurée. Contactez-nous par téléphone.",
        "en": "Site email is not configured. Please call us.",
        "pt": "E-mail do site não configurado. Ligue-nos.",
        "it": "Email del sito non configurata. Chiamateci.",
    },
    "book.mail_error": {
        "fr": "L’envoi a échoué. Réessayez ou appelez-nous.",
        "en": "Sending failed. Please try again or call us.",
        "pt": "O envio falhou. Tente de novo ou ligue-nos.",
        "it": "Invio non riuscito. Riprovate o chiamateci.",
    },
    "book.mail_not_configured": {
        "fr": "L’envoi d’e-mail n’est pas encore configuré sur le serveur. Contactez-nous par téléphone ou WhatsApp.",
        "en": "Email sending is not configured on the server yet. Please call or WhatsApp us.",
        "pt": "O envio de e-mail ainda não está configurado no servidor. Ligue ou use o WhatsApp.",
        "it": "L’invio email non è ancora configurato sul server. Chiamateci o scrivete su WhatsApp.",
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
        "fr": "Location vacances Corse à Calcatoggio : La Casa Rosa — appartements vue mer, plage à 5 min, terrasse, famille. Réservez votre séjour en Corse-du-Sud.",
        "en": "Holiday rental in Corsica at Calcatoggio: La Casa Rosa — sea-view apartments, beach 5 min away, terrace, family stay. Book your Corsica vacation.",
        "pt": "Aluguel de férias na Córsega em Calcatoggio: La Casa Rosa — apartamentos vista mar, praia a 5 min, terraço, família. Reserve suas férias na Córsega.",
        "it": "Affitto vacanze in Corsica a Calcatoggio: La Casa Rosa — appartamenti vista mare, spiaggia a 5 min, terrazza, famiglia. Prenotate la vostra vacanza in Corsica.",
    },
    "meta.default_og_title": {
        "fr": "La Casa Rosa — Location vacances Calcatoggio, Corse",
        "en": "La Casa Rosa — Holiday rental Calcatoggio, Corsica",
        "pt": "La Casa Rosa — Aluguel de férias Calcatoggio, Córsega",
        "it": "La Casa Rosa — Affitto vacanze Calcatoggio, Corsica",
    },
    "meta.title_suffix": {
        "fr": "La Casa Rosa — Location vacances Calcatoggio, Corse",
        "en": "La Casa Rosa — Holiday rental Calcatoggio, Corsica",
        "pt": "La Casa Rosa — Aluguel de férias Calcatoggio, Córsega",
        "it": "La Casa Rosa — Affitto vacanze Calcatoggio, Corsica",
    },
    "meta.keywords": {
        "fr": "location vacances Corse, location Calcatoggio, appartement vue mer Corse, villa Corse-du-Sud, Acqua Linda d'Orcino, plage Liscia, séjour Corse famille, location saisonnière Corse, vacances Ajaccio, gîte Corse",
        "en": "Corsica holiday rental, Calcatoggio apartment, sea view Corsica, Southern Corsica villa, Acqua Linda d'Orcino, Liscia beach, family vacation Corsica, self catering Corsica, Ajaccio holidays, Corsica rental",
        "pt": "aluguel de férias Córsega, apartamento Calcatoggio, vista mar Córsega, villa Córsega do Sul, Acqua Linda d'Orcino, praia Liscia, férias em família Córsega, Ajaccio, aluguel temporada Córsega",
        "it": "affitto vacanze Corsica, appartamento Calcatoggio, vista mare Corsica, villa Corsica del Sud, Acqua Linda d'Orcino, spiaggia Liscia, vacanze famiglia Corsica, Ajaccio, affitto stagionale Corsica",
    },
    "meta.apartments_description": {
        "fr": "Appartements en location à Calcatoggio, Corse — calendriers de disponibilité La Casa Rosa, vue mer, plage à pied. Réservez vos vacances en Corse.",
        "en": "Apartments for rent in Calcatoggio, Corsica — La Casa Rosa availability calendars, sea view, beach nearby. Book your Corsica holiday.",
        "pt": "Apartamentos para alugar em Calcatoggio, Córsega — calendários La Casa Rosa, vista mar, praia a pé. Reserve suas férias na Córsega.",
        "it": "Appartamenti in affitto a Calcatoggio, Corsica — calendari La Casa Rosa, vista mare, spiaggia a piedi. Prenotate le vacanze in Corsica.",
    },
    "meta.about_description": {
        "fr": "Hôtes à Calcatoggio : famille corse-brésilienne accueille à La Casa Rosa — location vacances vue mer en Corse-du-Sud.",
        "en": "Hosts in Calcatoggio: Corsican-Brazilian family welcomes you at La Casa Rosa — sea-view holiday rental in Southern Corsica.",
        "pt": "Anfitriões em Calcatoggio: família corso-brasileira recebe na La Casa Rosa — aluguel de férias vista mar na Córsega do Sul.",
        "it": "Host a Calcatoggio: famiglia corso-brasiliana vi accoglie a La Casa Rosa — affitto vacanze vista mare in Corsica del Sud.",
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
        "fr": "La Casa Rosa — logo",
        "en": "La Casa Rosa — logo",
        "pt": "La Casa Rosa — logotipo",
        "it": "La Casa Rosa — logo",
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
        "fr": "Famille La Casa Rosa — hôtes à Calcatoggio",
        "en": "La Casa Rosa family — hosts in Calcatoggio",
        "pt": "Família La Casa Rosa — anfitriões em Calcatoggio",
        "it": "Famiglia La Casa Rosa — host a Calcatoggio",
    },
    "seo.amenity_sea_view": {
        "fr": "Vue mer",
        "en": "Sea view",
        "pt": "Vista para o mar",
        "it": "Vista mare",
    },
    "seo.amenity_beach": {
        "fr": "Plage à 5 minutes à pied",
        "en": "Beach a 5-minute walk away",
        "pt": "Praia a 5 minutos a pé",
        "it": "Spiaggia a 5 minuti a piedi",
    },
    "seo.amenity_terrace": {
        "fr": "Grande terrasse",
        "en": "Large terrace",
        "pt": "Grande terraço",
        "it": "Grande terrazza",
    },
    "seo.amenity_parking": {
        "fr": "Parking",
        "en": "Parking",
        "pt": "Estacionamento",
        "it": "Parcheggio",
    },
    "seo.amenity_quiet": {
        "fr": "Cadre calme",
        "en": "Quiet setting",
        "pt": "Ambiente calmo",
        "it": "Ambiente tranquillo",
    },
    "seo.knows_about": {
        "fr": "Location vacances Corse, appartement Calcatoggio, séjour vue mer Corse-du-Sud",
        "en": "Corsica holiday rental, Calcatoggio apartment, sea-view stay Southern Corsica",
        "pt": "Aluguel de férias Córsega, apartamento Calcatoggio, estadia vista mar Córsega do Sul",
        "it": "Affitto vacanze Corsica, appartamento Calcatoggio, soggiorno vista mare Corsica del Sud",
    },
    "home.read_more": {
        "fr": "Lire la suite",
        "en": "Read more",
        "pt": "Ler mais",
        "it": "Leggi di più",
    },
    "home.see_calendar": {
        "fr": "Voir le calendrier",
        "en": "See calendar",
        "pt": "Ver calendário",
        "it": "Vedi il calendario",
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
        "pt": "Nossos apartamentos",
        "it": "I nostri appartamenti",
    },
    "home.no_apartments": {
        "fr": "Aucun appartement pour le moment.",
        "en": "No apartments available yet.",
        "pt": "Nenhum apartamento disponível no momento.",
        "it": "Nessun appartamento disponibile al momento.",
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
        "fr": "Découvrez les appartements de La Casa Rosa et consultez les disponibilités.",
        "en": "Discover the apartments at La Casa Rosa and check availability.",
        "pt": "Descubra os apartamentos da La Casa Rosa e consulte a disponibilidade.",
        "it": "Scoprite gli appartamenti di La Casa Rosa e consultate le disponibilità.",
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
        "pt": "Senha",
        "it": "Password",
    },
    "login.submit": {"fr": "Se connecter", "en": "Log In", "pt": "Entrar", "it": "Accedi"},

    "cms.lang_hint": {
        "fr": "Vous modifiez le contenu pour la langue :",
        "en": "You are editing content for language:",
        "pt": "Você está editando o conteúdo para o idioma:",
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
