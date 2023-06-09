#!/bin/env python3
from appli_covid19.models import Sous_Theme, Journal, StudyType, Articles, Article_Theme, StudyType_Articles
from django.db import IntegrityError
from datetime import datetime
import pandas as pd
import os
import unidecode
import re
"""
Création des listes pour peupler les tables articles, article_theme et studytype_articles.
"""
print("Ou se trouve vos fichiers/dossiers Kaggle, documents_parses et metadata.csv ?")
chemin_archive = input("Veuillez donner le chemin : chemin_archive (/users/2023/ds1/share/CORD-19)=") or "/users/2023/ds1/share/CORD-19"
echantillon=input("Quelle est la taille de l'echantillon que vous voulez lancer ? (max=1056660)  =")
n=int(echantillon)
chemin_tables=f'{chemin_archive}/Kaggle/target_tables'
elements = os.listdir(chemin_tables)
dossiers = [element for element in elements if os.path.isdir(os.path.join(chemin_tables, element))]

print("En train de charger le fichier metadata.csv")
DF=pd.read_csv(f'{chemin_archive}/metadata.csv')
print('Chargement termine')

#############################################  LISTE DES STUDYTYPE POUR CHAQUE ARTICLE DE METADATA.CSV  #############################################
print('Liste Study_types pour un article creation : debut')
'''
Création d'une liste de tuples : [ (son_studytype, un_article) ,  (...,...)  ,  ... ]
'''            
Articles0=[]  #liste d'articles qui ont au moins un studytype
Study_Article=[]
for dossier in dossiers[1:-1]:
    chemin = f'{chemin_tables}/{dossier}'
    elements = os.listdir(chemin)
    for element in elements :
        df=pd.read_csv(f'{chemin}/{element}')
        try :
            for i in range(len(df)):
                s=df['Study Type'][i]
                if type(s)==str and len(s)>2:
                    study_article=(re.sub("\!|\'|\?|-"," ",s.title()),df['Study'][i])
                    Articles0.append(df['Study'][i])
                    Study_Article.append(study_article)
        except:
            print(f"Le fichier {chemin}/{element} n'a pas de studytype !")
''' 
Création d'un dictionnaire tel que : { un_article = [ liste de ses studytype] , ...}
'''
Study_Articles2={}
for article in set(Articles0):
    types=[]
    for i in range(len(Study_Article)):
        if Study_Article[i][1]==article:
            types.append(Study_Article[i][0])
    Study_Articles2[article]=list(set(types))
'''
Création d'une liste telle que : pour chaque article/ligne du metadata.csv, on a la liste de ses studytypes
'''
Study_types=[]
for article_titre in DF['title'][:n]:
    etat=False
    if type(article_titre)==str:
        for key in Study_Articles2:
            if key.upper()==article_titre.upper():
                cle=key
                etat=True
    if etat:
        Study_types.append(Study_Articles2[cle])
    else:
        Study_types.append(None)

print('Liste Study_types pour un article creation : fin')
#############################################  LISTE DES SOUS_THEMES POUR CHAQUE ARTICLE DE METADATA.CSV  #############################################
print('Liste Sous_themes pour un article creation : debut')
''' 
Création d'un dictionnaire tel que : { un_sous_theme = [ liste des artciles de ce sous_themes] , ...}
'''
Sous_themes_articles={}
for dossier in dossiers[1:-1]:
        chemin = f'{chemin_tables}/{dossier}'
        elements = os.listdir(chemin)
        for element in elements :
            sous_theme = f'{element[:-4]}'
            da= pd.read_csv(f'{chemin}/{element}')
            Sous_themes_articles[sous_theme]=da['Study'].str.upper().unique()
'''
Création d'une liste telle que : pour chaque article/ligne du metadata.csv, on a ses sous_themes
'''
Sous_themes_articles2=[]
for article_title in DF['title'][:n]:
    k=[]
    if type(article_title)==str:
        for key in Sous_themes_articles:
            if article_title.upper() in Sous_themes_articles[key]:
                k.append(key)
    if len(k)!=0:
        Sous_themes_articles2.append(k)
    else:
        Sous_themes_articles2.append(None)
print('Liste Sous_themes pour un article creation : fin')
#############################################  PEUPLEMENT DES 3 TABLES  #############################################
print("\n ------ PEUPLEMENT DEBUT ------ \n")
for i in range(n):
    s=DF['journal'][i]
    if ("\\" in r"%r" % f"{s}" ):
        jo=unidecode.unidecode("".join(list(filter(str.isalpha,f"{s}"))))
    else:
        jo=s
    if i%100==0:
        print(f"Ligne {i}")
    try:
        un_article = Articles()
        un_article.id_article=i
        un_article.title = DF['title'][i]
        if type(DF['publish_time'][i])!=float:
            d=DF['publish_time'][i]
            try:
                d2 = datetime.strptime(d, '%Y-%m-%d')
                un_article.publish_time=d2.date()
                un_article.annee=str(d2.year)
            except:
                un_article.annee=str(d)
        if type(DF['abstract'][i])!=float:
            un_article.abstract = DF['abstract'][i]
        if type(DF['url'][i])!=float:
            un_article.studylink = DF['url'][i]
        if type(s)!=float:
            le_journal = Journal.objects.get(name = jo)
            un_article.journal = le_journal
        un_article.save()
    except IntegrityError:
        print("Cet article existe deja")
    except:
        print("!!! probleme à la ligne = ", i," !!!")
    ############################################
    STA=StudyType_Articles()
    liste_studytype = Study_types[i]
    try:
        if type(liste_studytype)==list:
            print(liste_studytype)
            for k in range(len(liste_studytype)):
                id_studytype=StudyType.objects.get(name = str(liste_studytype[k]))
                STA.studytype=id_studytype
                STA.article=un_article
                STA.save()
    except:
        print("!!! probleme à la ligne = ", i," !!!")
    ############################################
    AT=Article_Theme()
    liste_sousthemes = Sous_themes_articles2[i]
    try:
        if type(liste_sousthemes)==list:
            print(liste_sousthemes)
            for k in range(len(liste_sousthemes)):
                id_sous_theme=Sous_Theme.objects.get(name = str(liste_sousthemes[k]))
                AT.sous_theme=id_sous_theme
                AT.article=un_article
                AT.save()
    except:
        print("!!! probleme à la ligne = ", i," !!!")
print("\n ------ PEUPLEMENT FIN ------ \n")
