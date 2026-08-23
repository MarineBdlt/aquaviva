"""La Casa Rosa — shared location & amenities (Calcatoggio, Corse)."""

import copy
import json

from booking_engine.i18n import content_page_key, get_locale
from booking_engine.models import SiteContent, SiteSetting

VILLA_LOCATION = {
    "fr": {
        "title": "Localisation",
        "place": "Calcatoggio, Corse-du-Sud",
        "region": "Corse, France",
        "summary": (
            "L’Acqua Linda d’Orcino, à Calcatoggio : villa très calme, grande terrasse "
            "vue sur mer, plage à environ 5 minutes à pied."
        ),
        "map_label": "Voir la carte",
    },
    "en": {
        "title": "Location",
        "place": "Calcatoggio, South Corsica",
        "region": "Corsica, France",
        "summary": (
            "Acqua Linda d’Orcino in Calcatoggio: a peaceful villa, large sea-view "
            "terrace, beach about a 5-minute walk away."
        ),
        "map_label": "View map",
    },
    "pt": {
        "title": "Localização",
        "place": "Calcatoggio, Corsica do Sul",
        "region": "Córsega, França",
        "summary": (
            "Acqua Linda d’Orcino em Calcatoggio: villa muito calma, grande terraço "
            "com vista para o mar, praia a cerca de 5 minutos a pé."
        ),
        "map_label": "Ver mapa",
    },
    "it": {
        "title": "Posizione",
        "place": "Calcatoggio, Corsica del Sud",
        "region": "Corsica, Francia",
        "summary": (
            "Acqua Linda d’Orcino a Calcatoggio: villa molto tranquilla, grande terrazza "
            "con vista mare, spiaggia a circa 5 minuti a piedi."
        ),
        "map_label": "Vedi la mappa",
    },
}

# OpenStreetMap embed centered on Calcatoggio
VILLA_MAP_EMBED = (
    "https://www.openstreetmap.org/export/embed.html?"
    "bbox=8.74%2C42.00%2C8.80%2C42.05&layer=mapnik&marker=42.027%2C8.768"
)
VILLA_MAP_LINK = "https://www.openstreetmap.org/?mlat=42.027&mlon=8.768#map=14/42.027/8.768"

NEARBY = {
    "fr": {
        "title": "À proximité",
        "list": [
            {"icon": "beach", "name": "Plage du Stagnone / Liscia", "detail": "5 min à pied · baignade"},
            {"icon": "tower", "name": "Tour génoise d’Ancône", "detail": "18 min à pied · 1,5 km"},
            {"icon": "paraglide", "name": "Parapente (mer & montagne)", "detail": "Plage de la Liscia · Corsic Adventure"},
            {"icon": "watersport", "name": "Sports nautiques", "detail": "Jet-ski, paddle, kayak, wakeboard"},
            {"icon": "dive", "name": "Plongée sous-marine", "detail": "Plage d’Orcino · Nautica Plongée"},
            {"icon": "boat", "name": "Excursions en mer", "detail": "Location bateau · calanques & côte"},
            {"icon": "town", "name": "Sagone", "detail": "environ 30 min · 20 km"},
            {"icon": "town", "name": "Ajaccio", "detail": "environ 45 min en voiture"},
            {"icon": "town", "name": "Calvi", "detail": "environ 2 h 30 · 135 km"},
        ],
    },
    "en": {
        "title": "Nearby",
        "list": [
            {"icon": "beach", "name": "Stagnone / Liscia Beach", "detail": "5 min walk · swimming"},
            {"icon": "tower", "name": "Genoese Tower of Ancône", "detail": "18 min walk · 1.5 km"},
            {"icon": "paraglide", "name": "Paragliding (sea & mountain)", "detail": "Liscia Beach · Corsic Adventure"},
            {"icon": "watersport", "name": "Water sports", "detail": "Jet ski, paddle, kayak, wakeboard"},
            {"icon": "dive", "name": "Scuba diving", "detail": "Orcino Beach · Nautica Plongée"},
            {"icon": "boat", "name": "Boat trips", "detail": "Boat rental · coves & coastline"},
            {"icon": "town", "name": "Sagone", "detail": "about 30 min · 20 km"},
            {"icon": "town", "name": "Ajaccio", "detail": "about 45 min drive"},
            {"icon": "town", "name": "Calvi", "detail": "about 2 h 30 · 135 km"},
        ],
    },
    "pt": {
        "title": "Nas proximidades",
        "list": [
            {"icon": "beach", "name": "Praia do Stagnone / Liscia", "detail": "5 min a pé · banho de mar"},
            {"icon": "tower", "name": "Torre genovesa d’Ancône", "detail": "18 min a pé · 1,5 km"},
            {"icon": "paraglide", "name": "Parapente (mar e montanha)", "detail": "Praia de Liscia · Corsic Adventure"},
            {"icon": "watersport", "name": "Desportos aquáticos", "detail": "Jet-ski, paddle, caiaque, wakeboard"},
            {"icon": "dive", "name": "Mergulho", "detail": "Praia de Orcino · Nautica Plongée"},
            {"icon": "boat", "name": "Passeios de barco", "detail": "Aluguer de barco · calas e costa"},
            {"icon": "town", "name": "Sagone", "detail": "cerca de 30 min · 20 km"},
            {"icon": "town", "name": "Ajaccio", "detail": "cerca de 45 min de carro"},
            {"icon": "town", "name": "Calvi", "detail": "cerca de 2 h 30 · 135 km"},
        ],
    },
    "it": {
        "title": "Nelle vicinanze",
        "list": [
            {"icon": "beach", "name": "Spiaggia dello Stagnone / Liscia", "detail": "5 min a piedi · balneazione"},
            {"icon": "tower", "name": "Torre genovese d’Ancône", "detail": "18 min a piedi · 1,5 km"},
            {"icon": "paraglide", "name": "Parapendio (mare e montagna)", "detail": "Spiaggia di Liscia · Corsic Adventure"},
            {"icon": "watersport", "name": "Sport acquatici", "detail": "Jet ski, paddle, kayak, wakeboard"},
            {"icon": "dive", "name": "Immersioni", "detail": "Spiaggia di Orcino · Nautica Plongée"},
            {"icon": "boat", "name": "Gite in mare", "detail": "Noleggio barca · calette e costa"},
            {"icon": "town", "name": "Sagone", "detail": "circa 30 min · 20 km"},
            {"icon": "town", "name": "Ajaccio", "detail": "circa 45 min in auto"},
            {"icon": "town", "name": "Calvi", "detail": "circa 2 h 30 · 135 km"},
        ],
    },
}

# Highly rated local spots (activities + food) — with optional image & link
GOOD_SPOTS = {
    "fr": {
        "title": "Bonnes adresses",
        "intro": "Plongée, nature, balades et tables — nos coups de cœur autour de La Casa Rosa.",
        "list": [
            {
                "icon": "dive",
                "name": "Nautica Plongée",
                "kind": "Centre de plongée · Orcino",
                "rating": "★ 4,9",
                "detail": "Baptêmes et explorations sous-marines depuis la plage d’Orcino.",
                "url": "https://www.nauticaplongee.com/",
                "image": "https://images.unsplash.com/photo-1544551763-46a013bb70d5?auto=format&fit=crop&w=800&q=80",
            },
            {
                "icon": "tower",
                "name": "Calanques de Piana",
                "kind": "Site UNESCO · nature",
                "rating": "★ 4,9",
                "detail": "Falaises de granite rose classées — excursion mythique à ~1 h de route.",
                "url": "https://www.visit-corsica.com/fr/decouvrir/sites-naturels/les-calanche-de-piana",
                "image": "https://images.unsplash.com/photo-1559827260-dc66d52bef19?auto=format&fit=crop&w=800&q=80",
            },
            {
                "icon": "paraglide",
                "name": "Corsic Adventure",
                "kind": "Parapente · Liscia",
                "rating": "★ 4,8",
                "detail": "Vols biplace mer & montagne au-dessus de la plage de la Liscia.",
                "url": "https://www.corsic-adventure.com/",
                "image": "https://images.unsplash.com/photo-1473862170180-84427c485aca?auto=format&fit=crop&w=800&q=80",
            },
            {
                "icon": "tower",
                "name": "Tour génoise d’Ancône",
                "kind": "Patrimoine · balade",
                "rating": "★ 4,7",
                "detail": "Promenade d’environ 18 min jusqu’à la tour, vue mer spectaculaire.",
                "url": "https://www.openstreetmap.org/?mlat=42.03&mlon=8.76#map=15/42.03/8.76",
                "image": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?auto=format&fit=crop&w=800&q=80",
            },
            {
                "icon": "pizza",
                "name": "U Fornu",
                "kind": "Pizzeria · village",
                "rating": "★ 4,8",
                "detail": "Pizzas au feu de bois, produits corses, vue sur la baie de la Liscia.",
                "url": "https://www.google.com/maps/search/?api=1&query=U+Fornu+Calcatoggio",
                "image": "https://images.unsplash.com/photo-1513104890138-7c749659a591?auto=format&fit=crop&w=800&q=80",
            },
            {
                "icon": "auberge",
                "name": "Auberge d’Ancône",
                "kind": "Cuisine corse",
                "rating": "★ 4,8",
                "detail": "Plats traditionnels faits maison, terrasse vue mer près de la tour.",
                "url": "https://www.google.com/maps/search/?api=1&query=Auberge+d%27Ancone+Calcatoggio",
                "image": "https://images.unsplash.com/photo-1414235077428-338989a2e8c0?auto=format&fit=crop&w=800&q=80",
            },
            {
                "icon": "foodtruck",
                "name": "Orcino Food Truck",
                "kind": "Burgers & pizza · plage",
                "rating": "★ 4,8",
                "detail": "Spot décontracté sur la plage d’Orcino, idéal au coucher du soleil.",
                "url": "https://www.google.com/maps/search/?api=1&query=Orcino+Food+Truck+Calcatoggio",
                "image": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=800&q=80",
            },
            {
                "icon": "seaside",
                "name": "Les Tamaris",
                "kind": "Italien · bord de mer",
                "rating": "★ 4,5",
                "detail": "Restaurant de plage à Orcino — pizzas et cuisine italienne pieds dans le sable.",
                "url": "https://www.google.com/maps/search/?api=1&query=Les+Tamaris+Orcino+Calcatoggio",
                "image": "https://images.unsplash.com/photo-1473093295043-cdd812d0e601?auto=format&fit=crop&w=800&q=80",
            },
        ],
    },
    "en": {
        "title": "Good places nearby",
        "intro": "Diving, nature, walks and tables — our favourites around La Casa Rosa.",
        "list": [
            {
                "icon": "dive",
                "name": "Nautica Plongée",
                "kind": "Dive centre · Orcino",
                "rating": "★ 4.9",
                "detail": "Try dives and reef explorations from Orcino beach.",
                "url": "https://www.nauticaplongee.com/",
                "image": "https://images.unsplash.com/photo-1544551763-46a013bb70d5?auto=format&fit=crop&w=800&q=80",
            },
            {
                "icon": "tower",
                "name": "Calanques de Piana",
                "kind": "UNESCO · nature",
                "rating": "★ 4.9",
                "detail": "Pink granite cliffs — a legendary day trip about 1 hour away.",
                "url": "https://www.visit-corsica.com/en/discover/natural-sites/the-calanche-of-piana",
                "image": "https://images.unsplash.com/photo-1559827260-dc66d52bef19?auto=format&fit=crop&w=800&q=80",
            },
            {
                "icon": "paraglide",
                "name": "Corsic Adventure",
                "kind": "Paragliding · Liscia",
                "rating": "★ 4.8",
                "detail": "Tandem flights over sea and mountains above Liscia beach.",
                "url": "https://www.corsic-adventure.com/",
                "image": "https://images.unsplash.com/photo-1473862170180-84427c485aca?auto=format&fit=crop&w=800&q=80",
            },
            {
                "icon": "tower",
                "name": "Genoese Tower of Ancône",
                "kind": "Heritage · walk",
                "rating": "★ 4.7",
                "detail": "About an 18-minute walk to the tower and spectacular sea views.",
                "url": "https://www.openstreetmap.org/?mlat=42.03&mlon=8.76#map=15/42.03/8.76",
                "image": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?auto=format&fit=crop&w=800&q=80",
            },
            {
                "icon": "pizza",
                "name": "U Fornu",
                "kind": "Pizzeria · village",
                "rating": "★ 4.8",
                "detail": "Wood-fired pizzas, Corsican products, view over Liscia bay.",
                "url": "https://www.google.com/maps/search/?api=1&query=U+Fornu+Calcatoggio",
                "image": "https://images.unsplash.com/photo-1513104890138-7c749659a591?auto=format&fit=crop&w=800&q=80",
            },
            {
                "icon": "auberge",
                "name": "Auberge d’Ancône",
                "kind": "Corsican cuisine",
                "rating": "★ 4.8",
                "detail": "Homemade traditional dishes, sea-view terrace near the tower.",
                "url": "https://www.google.com/maps/search/?api=1&query=Auberge+d%27Ancone+Calcatoggio",
                "image": "https://images.unsplash.com/photo-1414235077428-338989a2e8c0?auto=format&fit=crop&w=800&q=80",
            },
            {
                "icon": "foodtruck",
                "name": "Orcino Food Truck",
                "kind": "Burgers & pizza · beach",
                "rating": "★ 4.8",
                "detail": "Casual spot on Orcino beach — perfect at sunset.",
                "url": "https://www.google.com/maps/search/?api=1&query=Orcino+Food+Truck+Calcatoggio",
                "image": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=800&q=80",
            },
            {
                "icon": "seaside",
                "name": "Les Tamaris",
                "kind": "Italian · beachfront",
                "rating": "★ 4.5",
                "detail": "Beach restaurant at Orcino — pizzas and Italian food by the sand.",
                "url": "https://www.google.com/maps/search/?api=1&query=Les+Tamaris+Orcino+Calcatoggio",
                "image": "https://images.unsplash.com/photo-1473093295043-cdd812d0e601?auto=format&fit=crop&w=800&q=80",
            },
        ],
    },
    "pt": {
        "title": "Boas moradas",
        "intro": "Mergulho, natureza, passeios e mesas — os nossos favoritos perto de La Casa Rosa.",
        "list": [
            {
                "icon": "dive",
                "name": "Nautica Plongée",
                "kind": "Centro de mergulho · Orcino",
                "rating": "★ 4,9",
                "detail": "Batismos e explorações submarinas a partir da praia de Orcino.",
                "url": "https://www.nauticaplongee.com/",
                "image": "https://images.unsplash.com/photo-1544551763-46a013bb70d5?auto=format&fit=crop&w=800&q=80",
            },
            {
                "icon": "tower",
                "name": "Calanques de Piana",
                "kind": "Património UNESCO · natureza",
                "rating": "★ 4,9",
                "detail": "Falésias de granito rosa — passeio mítico a cerca de 1 h de carro.",
                "url": "https://www.visit-corsica.com/fr/decouvrir/sites-naturels/les-calanche-de-piana",
                "image": "https://images.unsplash.com/photo-1559827260-dc66d52bef19?auto=format&fit=crop&w=800&q=80",
            },
            {
                "icon": "paraglide",
                "name": "Corsic Adventure",
                "kind": "Parapente · Liscia",
                "rating": "★ 4,8",
                "detail": "Voos tandem mar e montanha sobre a praia de Liscia.",
                "url": "https://www.corsic-adventure.com/",
                "image": "https://images.unsplash.com/photo-1473862170180-84427c485aca?auto=format&fit=crop&w=800&q=80",
            },
            {
                "icon": "tower",
                "name": "Torre genovesa d’Ancône",
                "kind": "Património · passeio",
                "rating": "★ 4,7",
                "detail": "Cerca de 18 min a pé até à torre, vista mar espetacular.",
                "url": "https://www.openstreetmap.org/?mlat=42.03&mlon=8.76#map=15/42.03/8.76",
                "image": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?auto=format&fit=crop&w=800&q=80",
            },
            {
                "icon": "pizza",
                "name": "U Fornu",
                "kind": "Pizzaria · aldeia",
                "rating": "★ 4,8",
                "detail": "Pizzas no forno a lenha, produtos corsos, vista sobre a baía de Liscia.",
                "url": "https://www.google.com/maps/search/?api=1&query=U+Fornu+Calcatoggio",
                "image": "https://images.unsplash.com/photo-1513104890138-7c749659a591?auto=format&fit=crop&w=800&q=80",
            },
            {
                "icon": "auberge",
                "name": "Auberge d’Ancône",
                "kind": "Cozinha corsa",
                "rating": "★ 4,8",
                "detail": "Pratos tradicionais caseiros, terraço com vista para o mar.",
                "url": "https://www.google.com/maps/search/?api=1&query=Auberge+d%27Ancone+Calcatoggio",
                "image": "https://images.unsplash.com/photo-1414235077428-338989a2e8c0?auto=format&fit=crop&w=800&q=80",
            },
            {
                "icon": "foodtruck",
                "name": "Orcino Food Truck",
                "kind": "Burgers e pizza · praia",
                "rating": "★ 4,8",
                "detail": "Spot descontraído na praia de Orcino, ideal ao pôr do sol.",
                "url": "https://www.google.com/maps/search/?api=1&query=Orcino+Food+Truck+Calcatoggio",
                "image": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=800&q=80",
            },
            {
                "icon": "seaside",
                "name": "Les Tamaris",
                "kind": "Italiano · beira-mar",
                "rating": "★ 4,5",
                "detail": "Restaurante de praia em Orcino — pizzas e cozinha italiana na areia.",
                "url": "https://www.google.com/maps/search/?api=1&query=Les+Tamaris+Orcino+Calcatoggio",
                "image": "https://images.unsplash.com/photo-1473093295043-cdd812d0e601?auto=format&fit=crop&w=800&q=80",
            },
        ],
    },
    "it": {
        "title": "Buoni indirizzi",
        "intro": "Immersioni, natura, passeggiate e tavole — i nostri preferiti intorno a La Casa Rosa.",
        "list": [
            {
                "icon": "dive",
                "name": "Nautica Plongée",
                "kind": "Centro immersioni · Orcino",
                "rating": "★ 4,9",
                "detail": "Battesimi ed esplorazioni subacquee dalla spiaggia di Orcino.",
                "url": "https://www.nauticaplongee.com/",
                "image": "https://images.unsplash.com/photo-1544551763-46a013bb70d5?auto=format&fit=crop&w=800&q=80",
            },
            {
                "icon": "tower",
                "name": "Calanche di Piana",
                "kind": "UNESCO · natura",
                "rating": "★ 4,9",
                "detail": "Falesie di granito rosa — gita leggendaria a circa 1 h di auto.",
                "url": "https://www.visit-corsica.com/it/scoprire/siti-naturali/le-calanche-di-piana",
                "image": "https://images.unsplash.com/photo-1559827260-dc66d52bef19?auto=format&fit=crop&w=800&q=80",
            },
            {
                "icon": "paraglide",
                "name": "Corsic Adventure",
                "kind": "Parapendio · Liscia",
                "rating": "★ 4,8",
                "detail": "Voli tandem mare e montagna sopra la spiaggia di Liscia.",
                "url": "https://www.corsic-adventure.com/",
                "image": "https://images.unsplash.com/photo-1473862170180-84427c485aca?auto=format&fit=crop&w=800&q=80",
            },
            {
                "icon": "tower",
                "name": "Torre genovese d’Ancône",
                "kind": "Patrimonio · passeggiata",
                "rating": "★ 4,7",
                "detail": "Circa 18 min a piedi fino alla torre, vista mare spettacolare.",
                "url": "https://www.openstreetmap.org/?mlat=42.03&mlon=8.76#map=15/42.03/8.76",
                "image": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?auto=format&fit=crop&w=800&q=80",
            },
            {
                "icon": "pizza",
                "name": "U Fornu",
                "kind": "Pizzeria · paese",
                "rating": "★ 4,8",
                "detail": "Pizze al forno a legna, prodotti corsi, vista sulla baia di Liscia.",
                "url": "https://www.google.com/maps/search/?api=1&query=U+Fornu+Calcatoggio",
                "image": "https://images.unsplash.com/photo-1513104890138-7c749659a591?auto=format&fit=crop&w=800&q=80",
            },
            {
                "icon": "auberge",
                "name": "Auberge d’Ancône",
                "kind": "Cucina corsa",
                "rating": "★ 4,8",
                "detail": "Piatti tradizionali fatti in casa, terrazza vista mare vicino alla torre.",
                "url": "https://www.google.com/maps/search/?api=1&query=Auberge+d%27Ancone+Calcatoggio",
                "image": "https://images.unsplash.com/photo-1414235077428-338989a2e8c0?auto=format&fit=crop&w=800&q=80",
            },
            {
                "icon": "foodtruck",
                "name": "Orcino Food Truck",
                "kind": "Burger e pizza · spiaggia",
                "rating": "★ 4,8",
                "detail": "Posto informale sulla spiaggia di Orcino, ideale al tramonto.",
                "url": "https://www.google.com/maps/search/?api=1&query=Orcino+Food+Truck+Calcatoggio",
                "image": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=800&q=80",
            },
            {
                "icon": "seaside",
                "name": "Les Tamaris",
                "kind": "Italiano · mare",
                "rating": "★ 4,5",
                "detail": "Ristorante sulla spiaggia di Orcino — pizze e cucina italiana sulla sabbia.",
                "url": "https://www.google.com/maps/search/?api=1&query=Les+Tamaris+Orcino+Calcatoggio",
                "image": "https://images.unsplash.com/photo-1473093295043-cdd812d0e601?auto=format&fit=crop&w=800&q=80",
            },
        ],
    },
}

# Shared villa amenities shown on every apartment
AMENITIES = {
    "fr": {
        "title": "Équipements",
        "list": [
            {"icon": "wifi", "label": "Wi-Fi gratuit"},
            {"icon": "parking", "label": "Parking sur place"},
            {"icon": "kitchen", "label": "Cuisine privée"},
            {"icon": "laundry", "label": "Lave-linge"},
            {"icon": "balcony", "label": "Balcon / terrasse"},
            {"icon": "sea", "label": "Vue sur mer"},
            {"icon": "beach", "label": "Plage à 5 min à pied"},
            {"icon": "pets", "label": "Animaux acceptés"},
            {"icon": "pingpong", "label": "Table de ping-pong sur place"},
            {"icon": "home", "label": "Enceinte de la villa"},
        ],
    },
    "en": {
        "title": "Amenities",
        "list": [
            {"icon": "wifi", "label": "Free Wi-Fi"},
            {"icon": "parking", "label": "On-site parking"},
            {"icon": "kitchen", "label": "Private kitchen"},
            {"icon": "laundry", "label": "Washing machine"},
            {"icon": "balcony", "label": "Balcony / terrace"},
            {"icon": "sea", "label": "Sea view"},
            {"icon": "beach", "label": "Beach 5 min walk"},
            {"icon": "pets", "label": "Pets allowed"},
            {"icon": "pingpong", "label": "On-site ping-pong table"},
            {"icon": "home", "label": "Gated villa grounds"},
        ],
    },
    "pt": {
        "title": "Equipamentos",
        "list": [
            {"icon": "wifi", "label": "Wi-Fi grátis"},
            {"icon": "parking", "label": "Estacionamento no local"},
            {"icon": "kitchen", "label": "Cozinha privada"},
            {"icon": "laundry", "label": "Máquina de lavar"},
            {"icon": "balcony", "label": "Varanda / terraço"},
            {"icon": "sea", "label": "Vista para o mar"},
            {"icon": "beach", "label": "Praia a 5 min a pé"},
            {"icon": "pets", "label": "Animais permitidos"},
            {"icon": "pingpong", "label": "Mesa de pingue-pongue no local"},
            {"icon": "home", "label": "Recinto da villa"},
        ],
    },
    "it": {
        "title": "Servizi",
        "list": [
            {"icon": "wifi", "label": "Wi-Fi gratuito"},
            {"icon": "parking", "label": "Parcheggio in loco"},
            {"icon": "kitchen", "label": "Cucina privata"},
            {"icon": "laundry", "label": "Lavatrice"},
            {"icon": "balcony", "label": "Balcone / terrazza"},
            {"icon": "sea", "label": "Vista mare"},
            {"icon": "beach", "label": "Spiaggia a 5 min a piedi"},
            {"icon": "pets", "label": "Animali ammessi"},
            {"icon": "pingpong", "label": "Tavolo da ping-pong in loco"},
            {"icon": "home", "label": "Recinto della villa"},
        ],
    },
}


def get_villa_info():
    """Return villa blocks, preferring CMS overrides when present."""
    lang = get_locale()
    location = copy.deepcopy(VILLA_LOCATION.get(lang, VILLA_LOCATION["fr"]))
    nearby = copy.deepcopy(NEARBY.get(lang, NEARBY["fr"]))
    good_spots = copy.deepcopy(GOOD_SPOTS.get(lang, GOOD_SPOTS["fr"]))

    try:
        loc_key = content_page_key("location", lang)
        spots_key = content_page_key("spots", lang)
        nearby_key = f"nearby_list_{lang}"
        spots_list_key = f"spots_list_{lang}"

        contents = {
            row.page_key: row
            for row in SiteContent.query.filter(
                SiteContent.page_key.in_([loc_key, spots_key])
            ).all()
        }
        settings = {
            row.setting_key: row
            for row in SiteSetting.query.filter(
                SiteSetting.setting_key.in_([nearby_key, spots_list_key])
            ).all()
        }

        loc = contents.get(loc_key)
        if loc:
            if loc.title:
                location["title"] = loc.title
            if loc.body:
                # body format: place\nregion\nsummary (summary may be multi-line)
                parts = loc.body.split("\n", 2)
                if len(parts) >= 1 and parts[0].strip():
                    location["place"] = parts[0].strip()
                if len(parts) >= 2 and parts[1].strip():
                    location["region"] = parts[1].strip()
                if len(parts) >= 3 and parts[2].strip():
                    location["summary"] = parts[2].strip()

        nearby_row = settings.get(nearby_key)
        if nearby_row and nearby_row.setting_value:
            data = json.loads(nearby_row.setting_value)
            if isinstance(data, dict):
                if data.get("title"):
                    nearby["title"] = data["title"]
                if isinstance(data.get("list"), list) and data["list"]:
                    nearby["list"] = data["list"]

        spots_meta = contents.get(spots_key)
        if spots_meta:
            if spots_meta.title:
                good_spots["title"] = spots_meta.title
            if spots_meta.body:
                good_spots["intro"] = spots_meta.body

        spots_row = settings.get(spots_list_key)
        if spots_row and spots_row.setting_value:
            data = json.loads(spots_row.setting_value)
            if isinstance(data, list) and data:
                good_spots["list"] = data
    except Exception:
        pass

    return {
        "location": location,
        "nearby": nearby,
        "good_spots": good_spots,
        "amenities": AMENITIES.get(lang, AMENITIES["fr"]),
        "map_embed": VILLA_MAP_EMBED,
        "map_link": VILLA_MAP_LINK,
    }


def nearby_list_to_text(nearby):
    lines = []
    for item in nearby.get("list", []):
        lines.append(f"{item.get('icon', 'town')}|{item.get('name', '')}|{item.get('detail', '')}")
    return "\n".join(lines)


def text_to_nearby_list(text):
    items = []
    for raw in (text or "").splitlines():
        line = raw.strip()
        if not line:
            continue
        parts = [p.strip() for p in line.split("|")]
        if len(parts) == 2:
            items.append({"icon": "town", "name": parts[0], "detail": parts[1]})
        elif len(parts) >= 3:
            items.append({"icon": parts[0] or "town", "name": parts[1], "detail": parts[2]})
    return items


def spots_list_to_text(spots):
    lines = []
    for item in spots.get("list", []):
        lines.append(
            f"{item.get('icon', 'seaside')}|{item.get('name', '')}|{item.get('kind', '')}|"
            f"{item.get('rating', '')}|{item.get('detail', '')}|"
            f"{item.get('url', '')}|{item.get('image', '')}"
        )
    return "\n".join(lines)


def text_to_spots_list(text):
    items = []
    for raw in (text or "").splitlines():
        line = raw.strip()
        if not line:
            continue
        parts = [p.strip() for p in line.split("|")]
        if len(parts) >= 5:
            item = {
                "icon": parts[0] or "seaside",
                "name": parts[1],
                "kind": parts[2],
                "rating": parts[3],
                "detail": parts[4],
            }
            if len(parts) >= 6 and parts[5]:
                item["url"] = parts[5]
            if len(parts) >= 7 and parts[6]:
                item["image"] = parts[6]
            items.append(item)
        elif len(parts) == 4:
            items.append(
                {
                    "icon": "seaside",
                    "name": parts[0],
                    "kind": parts[1],
                    "rating": parts[2],
                    "detail": parts[3],
                }
            )
    return items

