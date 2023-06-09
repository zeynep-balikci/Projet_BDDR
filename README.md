# M1 Data Science - Projet BDDR (2022 - 2023)

## Binôme Zeynep BALIKCI et Mariama MBAYE


Le sujet se trouve dans "1_Sujet.pdf".

Le schéma (3_Schema.pdf) a été créé sur le site : https://dbdiagram.io/d grâce au script dans le fichier : "2_diagram_script.txt".

### Etapes pour le projet:

- Étape 0 : Créer une base de données sur pgAdmin ou utiliser une base de données déjà existante et installer les bibliothèques suivants:

```bash
pip install unidecode
pip install psycopg2
pip install plotly
pip install pandas
```

- Étape 1 : Télécharger l'ensemble du dossier disponible sur Git.

- Étape 2 : Modifier la section "DATABASES" du fichier "./projet_bddr/projet_bddr/settings.py" :
```bash
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'nom_de_la_base_de_donnees',
        'USER': 'nom_utilisateur',
        'PASSWORD': 'mot_de_passe',
        'HOST': 'hôte',
        'PORT': '5432',
    }
}
```
Note : Remplacez "nom_de_la_base_de_donnees", "nom_utilisateur", "mot_de_passe" et "hôte" par vos propres informations de base de données.

- Etape 3 : Commandes shell.
```bash
cd projet_bddr
```
```bash
python manage.py makemigrations appli_covid19
```
```bash
python manage.py migrate
```

- Étape 4 : Peupler la base de données :
- Étape 4.1 : Pour peupler les tables Theme, Sous_Theme, StudyType, Affiliation et Journal.

Exécuter le fichier Peuple1.py sur le terminal (pas besoin de changer quoi que soit dans le script du fichier).

! Attention ! sur Unic il faut rendre exécutable ce fichier avec : chmod +x Peuple1.py

Entrer les informations nécessaires demandé après l'exécution : chemin_archive, host, etc...

Exemples : chemin_archive = /users/2023/ds1/share/CORD-19

HOST = data

DB_NAME = zbalikci

USER_NAME = zbalikci 

PASSWORD = zbalikci

Le peuplement de ces tables est terminé au bout d'1 heure et 10 minutes environ.

- Étape 4.2 : Pour peupler les tables les tables Articles, Article_Theme et StudyType_Articles.

Exécuter le fichier Peuple2.py du dossier projet_bddr, pour cela vous devez utilisez le shell de DJANGO avec : (dans ./projet_bddr)

```bash
python manage.py shell
```
Linux :
```bash
run Peuple2.py
```
Windows Powershell:
```bash
exec(open('Peuple2.py').read())
```
Le peuplement de ces tables est terminé au bout d'1 heure et 30 minutes environ. Mais vous pouvez choisir un échantillon plus petit lors de l'exécution du fichier.

- Étape 4.3 : Pour peupler les tables les tables Authors, Author_Affiliation et Author_Article.

Exécuter le fichier Peuple3.py du dossier projet_bddr, pour cela vous devez utilisez le shell de DJANGO avec : (dans ./projet_bddr)
```bash
python manage.py shell
```
Linux :
```bash
run Peuple3.py
```
Windows Powershell:
```bash
exec(open('Peuple3.py').read())
```
Le peuplement de ces tables est terminé au bout de 6 heure et 45 minutes environ. Mais vous pouvez choisir un échantillon plus petit lors de l'exécution du fichier.

- Étape 5 : Pour lancer l'application web, exécutez la commande suivante dans un terminal : 
```bash
python manage.py runserver
```
L'application sera alors disponible à l'adresse http://localhost:8000/appli_covid19/ dans votre navigateur web.
