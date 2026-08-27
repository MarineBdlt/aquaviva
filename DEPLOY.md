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

## 6. E-mails du formulaire « Réserver » (`/reserver`)
Sans SMTP configuré, le formulaire affiche une erreur et **aucun mail n’est envoyé**.

Sur PythonAnywhere (ou en local), dans `~/aquaviva/.env` :

```bash
MAIL_USERNAME=anais.acquaviva@gmail.com
MAIL_PASSWORD=xxxx xxxx xxxx xxxx
MAIL_DEFAULT_SENDER=anais.acquaviva@gmail.com
```

Créer le mot de passe d’application Gmail (pas le mot de passe du compte) :
1. Compte Google d’Anaïs → Sécurité → validation en 2 étapes (obligatoire)
2. https://myaccount.google.com/apppasswords → « Application » = Mail
3. Coller les 16 caractères dans `MAIL_PASSWORD`

Puis **Reload** l’app Web. Tester `/reserver`.  
Si le mail n’arrive pas : Spams + boîte « Promotions ». Le destinataire affiché sur le site se règle aussi dans le CMS (Contact).

## Mises à jour plus tard
```bash
cd ~/aquaviva
source venv/bin/activate
git pull
pip install -r requirements.txt
# puis Reload dans l’onglet Web
```
