#!/bin/env python3
import pandas as pd
import json
import unidecode  
from appli_covid19.models import Affiliation, Authors, Articles, Author_Article, Author_Affiliation
from django.db import IntegrityError

"""
Pour peupler les tables auhtors, author_article et author_affiliation:
"""
print("Ou se trouve vos fichiers/dossiers Kaggle, documents_parses et metadata.csv ?")
chemin_archive = input("Veuillez donner le chemin : chemin_archive (/users/2023/ds1/share/CORD-19)=") or "/users/2023/ds1/share/CORD-19"
echantillon=input("Quelle est la taille de l'echantillon que vous voulez lancer ? (max=1056660)  =")
n=int(echantillon)

print("En train de charger le fichier metadata.csv")
DF1=pd.read_csv(f'{chemin_archive}/metadata.csv')
print('Chargement termine')

DF=DF1[:n]
######################   Récupération des données dans les pdf_json_files et comparaison   ######################
print("Recuperation des donnees dans les pdf_json_files et comparaison")
dict_authors={}
total=len(DF[DF['pdf_json_files'].notnull()]) + len(DF[DF['pmc_json_files'].notnull()])
ligne=0
list_pdf=DF[DF['pdf_json_files'].notnull()]['pdf_json_files'].index.tolist()
for k in list_pdf:
    ligne+=1
    if ligne%100==0:
        print(f"{ligne} lignes traites sur un total de {total}")
    files_pdf=DF['pdf_json_files'][k]
    try:
        auteurs_metadata=DF['authors'][k].split('; ')
    except:
        auteurs_metadata=[]
    liste_file=files_pdf.split('; ')
    for file in liste_file:
        try:
            with open(f"{chemin_archive}/{file}",'r') as f:
                data=json.load(f)
                L=data['metadata']['authors']
                if len(L)!=0:
                    for i in range(len(L)):
                        first="".join(list(filter(str.isalpha,L[i]['first'] )))
                        last="".join(list(filter(str.isalpha,L[i]['last'])))
                        name_pdf=unidecode.unidecode(last)+', '+unidecode.unidecode(first)
                        name_pdf_propre="".join(list(filter(str.isalpha,name_pdf ))).upper()
                        etat=False
                        for auteur in auteurs_metadata:
                            auteur_propre=unidecode.unidecode("".join(list(filter(str.isalpha,auteur )))).upper()
                            if (name_pdf_propre in auteur_propre) or (auteur_propre in name_pdf_propre):
                                name_final=auteur
                                etat=True
                        if etat:
                            name=name_final
                        else:
                            name=name_pdf
                        if type(L[i]['email'])==str and len(L[i]['email'])>5:
                            email=L[i]['email']
                        else:
                            email=None
                        liste_affiliations=[]
                        if L[i]['affiliation']!={} :
                            if len(L[i]['affiliation']['laboratory'])>2 and 'Complete List of Authors' not in L[i]['affiliation']['laboratory']:
                                name_labo = unidecode.unidecode(L[i]['affiliation']['laboratory'])
                                liste_affiliations.append(name_labo)
                            if len(L[i]['affiliation']['institution'])>2 and 'Complete List of Authors' not in L[i]['affiliation']['institution']:
                                name_inst = unidecode.unidecode(L[i]['affiliation']['institution'])
                                liste_affiliations.append(name_inst)
                        if name not in dict_authors:
                            dict_authors[name]={'email':email,'articles_id':[k],'affiliations':liste_affiliations}
                        else:
                            dict_authors[name]['articles_id'].append(k)
                            dict_authors[name]['articles_id']=list(set(dict_authors[name]['articles_id']))
                            if type(email)==str and len(email)>5:
                                dict_authors[name]['email']=email
                            if name_labo:
                                dict_authors[name]['affiliations'].append(name_labo)
                            if name_inst:
                                dict_authors[name]['affiliations'].append(name_inst)
        except:
            pass
    for auteur in auteurs_metadata:
        if auteur not in dict_authors:
            dict_authors[auteur]={'email':None,'articles_id':[k], 'affiliations':[]}
        else:
            dict_authors[auteur]['articles_id'].append(k)
            dict_authors[auteur]['articles_id']=list(set(dict_authors[auteur]['articles_id']))
 
######################   Récupération des données dans les pmc_json_files et comparaison   ######################
print("Recuperation des donnees dans les pmc_json_files et comparaison")
list_pmc=DF[DF['pmc_json_files'].notnull()]['pmc_json_files'].index.tolist()
for k in list_pmc:
    ligne+=1
    if ligne%100==0:
        print(f"Lignes {ligne} traites sur {total}")
    try:
        auteurs_metadata=DF['authors'][k].split('; ')
    except:
        auteurs_metadata=[]
    with open(f"{chemin_archive}/{DF['pmc_json_files'][k]}",'r') as f:
        data=json.load(f)
        L=data['metadata']['authors']
        if len(L)!=0:
            for i in range(len(L)):
                first="".join(list(filter(str.isalpha,L[i]['first'] )))
                last="".join(list(filter(str.isalpha,L[i]['last'])))
                name_pmc=unidecode.unidecode(last)+', '+unidecode.unidecode(first)
                name_pmc_propre="".join(list(filter(str.isalpha,name_pmc ))).upper()
                etat=False
                for auteur in auteurs_metadata:
                    auteur_propre=unidecode.unidecode("".join(list(filter(str.isalpha,auteur )))).upper()
                    if (name_pmc_propre in auteur_propre) or (auteur_propre in name_pmc_propre):
                        name_final=auteur
                        etat=True
                if etat:
                    name=name_final
                else:
                    name=name_pmc
                if name not in dict_authors:
                    dict_authors[name]={'email':L[i]['email'],'articles_id':[k]}
                else:
                    dict_authors[name]['articles_id'].append(k)
                    dict_authors[name]['articles_id']=list(set(dict_authors[name]['articles_id']))
                    if type(L[i]['email'])==str and len(L[i]['email'])>5:
                        dict_authors[name]['email']=L[i]['email']
    for auteur in auteurs_metadata:
        if auteur not in dict_authors:
            dict_authors[auteur]={'email':None,'articles_id':[k]}
        else:
            dict_authors[auteur]['articles_id'].append(k)
            dict_authors[auteur]['articles_id']=list(set(dict_authors[auteur]['articles_id']))
#############################################  PEUPLEMENT DES 3 TABLES  #############################################
print("\n ------ PEUPLEMENT DEBUT ------ \n")
df3=pd.DataFrame.from_dict(dict_authors, orient='index')
df3.reset_index(inplace=True)
total=len(df3)
ligne=0
p=0
for k in range(len(df3)):
    ligne+=1
    if ligne%100==0:
        print(f"{ligne} lignes traites (du dataframe cree) sur un total de {total}")
    try:
        un_auteur=Authors()
        un_auteur.name=df3['index'][k]
    except IntegrityError:
        un_auteur=Authors.objects.get(name=df3['index'][k])
    except:
        p+=1
        un_auteur=Authors()
        un_auteur.name=f"probleme{p}"
        print(f"----  !!! Probleme à la ligne {k} du fichier dataframe cree !!! ----")
        print(df3['index'][k])
    if type(df3['email'][k])==str:
        un_auteur.email=df3['email'][k]
    un_auteur.save()
    if type(df3['affiliations'][k])==list and len(df3['affiliations'][k])!=0:
        liste_affiliations=list(set(df3['affiliations'][k]))
        for un_affiliation in liste_affiliations:
            try:
                aff=Affiliation.objects.get(name=un_affiliation)
                AAff=Author_Affiliation()
                AAff.affiliation=aff
                AAff.author=un_auteur
                AAff.save()
            except:
                print('Affiliation non trouvé')
    for i in df3['articles_id'][k]:
        try:
            un_article=Articles.objects.get(id_article=i)
            AA=Author_Article()
            AA.article=un_article
            AA.author=un_auteur
            AA.save()
        except:
            print('Article non trouvé')
############################   Récupération des auteurs restants dans metadata.csv   ############################
print("Recuperation des auteurs restants dans le fichier metadata.csv")
total=len(DF[DF['pmc_json_files'].isnull() & DF['pdf_json_files'].isnull() & DF['authors'].notnull()])
ligne=0
liste_auteurs_restants=DF[DF['pmc_json_files'].isnull() & DF['pdf_json_files'].isnull() & DF['authors'].notnull()]['authors'].index.tolist()
for k in liste_auteurs_restants:
    ligne+=1
    if ligne%100==0:
        print(f"{ligne} lignes traites du metadata.csv restants sur un total de {total}")
    authors_liste=DF['authors'][k].split('; ')
    for author in authors_liste:
        try:
            un_auteur=Authors()
            un_auteur.name=author
            un_auteur.save()
        except IntegrityError:
            un_auteur=Authors.objects.get(name=author)
        except:
            p+=1
            un_auteur=Authors()
            un_auteur.name=f"probleme{p}"
            un_auteur.save()
            print(f"----  !!! Probleme à la ligne {k} du fichier metadata.csv !!! ----")
        try:
            AA=Author_Article()
            un_article=Articles.objects.get(id_article=k)
            AA.article=un_article
            AA.author=un_auteur
            AA.save()
        except:
            print('Article non trouvé')
print("\n ------ PEUPLEMENT DEBUT ------ \n")
