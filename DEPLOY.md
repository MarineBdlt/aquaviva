# Déploiement PythonAnywhere (Aqua Viva)

## 1. Sur GitHub
Le code est sur : https://github.com/MarineBdlt/aquaviva

## 2. Compte PythonAnywhere
1. Crée un compte sur https://www.pythonanywhere.com
2. Note ton **username** (ex. `marinebdlt`)

## 3. Consoles → Bash
```bash
cd ~
git clone https://github.com/MarineBdlt/aquaviva.git
cd aquaviva
python3.10 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Édite .env : SECRET_KEY + éventuels mails
nano .env
```

## 4. Web → Add a new web app
- Manual configuration
- Python 3.10

Réglages :
- **Source code** : `/home/USERNAME/aquaviva`
- **Working directory** : `/home/USERNAME/aquaviva`
- **Virtualenv** : `/home/USERNAME/aquaviva/venv`
- **WSGI file** : ouvre le fichier WSGI proposé et remplace tout par le contenu de `wsgi.py` (en mettant ton vrai `USERNAME`)

Static files :
| URL | Directory |
|-----|-----------|
| `/static/` | `/home/USERNAME/aquaviva/booking_engine/static` |

## 5. Reload
Clique **Reload** → ouvre `https://USERNAME.pythonanywhere.com`

## 6. Formulaire « Réserver » (`/reserver`)
Le formulaire envoie les demandes à **anais.acquaviva@gmail.com** via [FormSubmit](https://formsubmit.co) :
Anaïs **reçoit** seulement — aucun mot de passe Gmail à créer.

**Une seule action la première fois :** après le premier envoi de test, elle clique le lien de confirmation reçu par e-mail (vérifier aussi Spams). Ensuite chaque demande arrive normalement.

L’adresse se change dans le CMS (Contact) si besoin.

## Mises à jour plus tard
```bash
cd ~/aquaviva
source venv/bin/activate
git pull
pip install -r requirements.txt
# puis Reload dans l’onglet Web
```
