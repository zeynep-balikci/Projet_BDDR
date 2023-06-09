from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.db import models
from appli_covid19.models import Theme, Sous_Theme, Journal, Affiliation, Articles, Article_Theme, StudyType_Articles, StudyType, Author_Affiliation, Author_Article, Authors
from datetime import datetime
from django.db.models.functions import Length
from django.db.models import Count
from django.core.paginator import Paginator
import pandas as pd
from plotly.offline import plot
import plotly.express as px

def index(request):
    themes = Theme.objects.all().order_by('name')
    template = loader.get_template('acceuil.twig')
    context = {'themes': themes,}
    return HttpResponse(template.render(context, request))

############################ REQUETE 1 Liste d'articles par thématiques et sous-thématique ############################

def sous_themes(request, name_theme):
	themes = Theme.objects.all().order_by('name')
	t = Theme.objects.get(name=str(name_theme))
	sous_themes = Sous_Theme.objects.filter(theme=t).order_by('name')
	template = loader.get_template('sous_themes.twig')
	context = {'themes': themes, 'sous_themes': sous_themes, 'theme':name_theme,}
	return HttpResponse(template.render(context, request))

def articles(request, name_sous_theme):
	themes = Theme.objects.all().order_by('name')
	st = Sous_Theme.objects.get(name=str(name_sous_theme))
	t = st.theme
	articles_sous_themes = Article_Theme.objects.filter(sous_theme=st).all()
	template = loader.get_template('articles.twig')
	context = {'themes': themes,'sous_theme' : name_sous_theme, 'theme':t , 'articles_sous_themes': articles_sous_themes,}
	return HttpResponse(template.render(context, request))
	
############################ REQUETE 2 Histogramme d'articles publiés par date, semaine, et mois. ############################

def histogram_annee(request):
	themes = Theme.objects.all().order_by('name')
	liste_annee=Articles.objects.all().values('annee').exclude(annee__isnull=True).annotate(nb_articles_annee=Count('annee')).order_by('annee')
	data=[{'Annee' : a['annee'],'Nb_articles' : a['nb_articles_annee']} for a in liste_annee]
	df = pd.DataFrame(data)
	fig=px.histogram(df,x= 'Annee', y="Nb_articles", labels={'Annee': 'Année',"Nb_articles":"Nombre d'articles publiés"}, )
	fig.for_each_trace(lambda t: t.update(hovertemplate=t.hovertemplate.replace("sum of", "")))
	fig.for_each_yaxis(lambda a: a.update(title_text=a.title.text.replace("sum of", " ")))
	gantt_plot=plot(fig,output_type='div')
	template = loader.get_template('histogram_annee.twig')
	context = {'themes': themes,'liste_annee': liste_annee, 'plot_div':gantt_plot}
	return HttpResponse(template.render(context, request))

def histogram_date(request):
	themes = Theme.objects.all().order_by('name')
	max_date=Articles.objects.all().exclude(publish_time__isnull=True).latest('publish_time').publish_time
	min_date=Articles.objects.all().exclude(publish_time__isnull=True).earliest('publish_time').publish_time
	if request.method=="POST":
		debut=request.POST.get("debut")
		fin=request.POST.get("fin")
		if debut != None and debut != "" and fin != None and fin != "":
			debut=datetime.strptime(debut, '%Y-%m-%d')
			fin=datetime.strptime(fin, '%Y-%m-%d')
			liste_date=Articles.objects.all().exclude(publish_time__isnull=True).values('publish_time').filter(publish_time__range=(debut, fin)).annotate(nb_articles_date=Count('publish_time')).order_by('publish_time')
			data=[{'Date' : a['publish_time'],'Nb_articles' : a['nb_articles_date']} for a in liste_date]
			df = pd.DataFrame(data)
			fig=px.histogram(df,x= 'Date', y="Nb_articles",nbins=len(liste_date), labels={"Nb_articles":"Nombre d'articles publiés"}, )
		else:
			debut=None
			fin=None
			liste_date=Articles.objects.all().values('annee').exclude(annee__isnull=True).annotate(nb_articles_annee=Count('annee')).order_by('annee')
			data=[{'Annee' : a['annee'],'Nb_articles' : a['nb_articles_annee']} for a in liste_date]
			df = pd.DataFrame(data)
			fig=px.histogram(df,x= 'Annee', y="Nb_articles", labels={'Annee': 'Année',"Nb_articles":"Nombre d'articles publiés"}, )
	else:
		debut=None
		fin=None
		liste_date=Articles.objects.all().values('annee').exclude(annee__isnull=True).annotate(nb_articles_annee=Count('annee')).order_by('annee')
		data=[{'Annee' : a['annee'],'Nb_articles' : a['nb_articles_annee']} for a in liste_date]
		df = pd.DataFrame(data)
		fig=px.histogram(df,x= 'Annee', y="Nb_articles", labels={'Annee': 'Année',"Nb_articles":"Nombre d'articles publiés"}, )
	fig.for_each_trace(lambda t: t.update(hovertemplate=t.hovertemplate.replace("sum of", "")))
	fig.for_each_yaxis(lambda a: a.update(title_text=a.title.text.replace("sum of", " ")))
	gantt_plot=plot(fig,output_type='div')
	template = loader.get_template('histogram_date.twig')
	context = {'themes': themes,'liste_annee': liste_date, 'plot_div':gantt_plot,'max_date':max_date,'min_date':min_date,'debut':debut,'fin':fin}
	return HttpResponse(template.render(context, request))

def histogram_mois(request):
	themes = Theme.objects.all().order_by('name')
	max_year=Articles.objects.all().exclude(publish_time__isnull=True).latest('publish_time').publish_time.year
	min_year=Articles.objects.all().exclude(publish_time__isnull=True).earliest('publish_time').publish_time.year
	if request.method=="POST":
		username=request.POST.get("username")
		if username != None and username != "" and min_year<=int(username)<=max_year:
			liste_mois=Articles.objects.all().exclude(publish_time__isnull=True).filter(publish_time__year=username).values('publish_time__month').annotate(nb_articles_mois=Count('publish_time__month')).order_by('publish_time__month')
		else:
			username=None
			liste_mois=Articles.objects.all().exclude(publish_time__isnull=True).values('publish_time__month').annotate(nb_articles_mois=Count('publish_time__month')).order_by('publish_time__month')
	else:
		username=None
		liste_mois=Articles.objects.all().exclude(publish_time__isnull=True).values('publish_time__month').annotate(nb_articles_mois=Count('publish_time__month')).order_by('publish_time__month')
	data=[{'Mois' : a['publish_time__month'],'Nb_articles' : a['nb_articles_mois']} for a in liste_mois]
	df = pd.DataFrame(data)
	fig=px.histogram(df,x= 'Mois', y="Nb_articles" , nbins=len(liste_mois), labels={"Nb_articles":"Nombre d'articles publiés"},)
	fig.for_each_trace(lambda t: t.update(hovertemplate=t.hovertemplate.replace("sum of", "")))
	fig.for_each_yaxis(lambda a: a.update(title_text=a.title.text.replace("sum of", " ")))
	fig.update_layout(bargap=0.1)
	gantt_plot=plot(fig,output_type='div')
	template = loader.get_template('histogram_mois.twig')
	context = {'themes': themes,'liste_mois': liste_mois, 'plot_div':gantt_plot, 'username' : username,'max_year':max_year, 'min_year':min_year,}
	return HttpResponse(template.render(context, request))

def histogram_semaine(request):
	themes = Theme.objects.all().order_by('name')
	max_year=Articles.objects.all().exclude(publish_time__isnull=True).latest('publish_time').publish_time.year
	min_year=Articles.objects.all().exclude(publish_time__isnull=True).earliest('publish_time').publish_time.year
	if request.method=="POST":
		username=request.POST.get("username")
		if username != None and username != "" and min_year<=int(username)<=max_year:
			liste_semaine=Articles.objects.all().exclude(publish_time__isnull=True).filter(publish_time__year=username).values('publish_time__week').annotate(nb_articles_semaine=Count('publish_time__week')).order_by('publish_time__week')
		else:
			username=None
			liste_semaine=Articles.objects.all().exclude(publish_time__isnull=True).values('publish_time__week').annotate(nb_articles_semaine=Count('publish_time__week')).order_by('publish_time__week')
	else:
		username=None
		liste_semaine=Articles.objects.all().exclude(publish_time__isnull=True).values('publish_time__week').annotate(nb_articles_semaine=Count('publish_time__week')).order_by('publish_time__week')
	data=[{'Semaine' : a['publish_time__week'],'Nb_articles' : a['nb_articles_semaine']} for a in liste_semaine]
	df = pd.DataFrame(data)
	fig=px.histogram(df,x= 'Semaine', y="Nb_articles" , nbins=len(liste_semaine), labels={"Nb_articles":"Nombre d'articles publiés"},)
	fig.for_each_trace(lambda t: t.update(hovertemplate=t.hovertemplate.replace("sum of", "")))
	fig.for_each_yaxis(lambda a: a.update(title_text=a.title.text.replace("sum of", " ")))
	fig.update_layout(bargap=0.1)
	gantt_plot=plot(fig,output_type='div')
	template = loader.get_template('histogram_semaine.twig')
	context = {'themes': themes,'liste_semaine': liste_semaine, 'plot_div':gantt_plot, 'username' : username,'max_year':max_year, 'min_year':min_year,}
	return HttpResponse(template.render(context, request))

############################ REQUETE 4 Nombre de publications par labo/institution. ############################

def affiliations2(request):
	themes = Theme.objects.all().order_by('name')
	liste_affiliations= Affiliation.objects.raw('''
	SELECT appli_covid19_affiliation.id, appli_covid19_affiliation.name, COUNT(DISTINCT appli_covid19_author_article.article_id) as nb_articles
	FROM appli_covid19_affiliation
	INNER JOIN appli_covid19_author_affiliation ON appli_covid19_affiliation.id=appli_covid19_author_affiliation.affiliation_id
	INNER JOIN appli_covid19_author_article ON appli_covid19_author_article.author_id=appli_covid19_author_affiliation.author_id
	GROUP BY appli_covid19_affiliation.id
	ORDER BY nb_articles DESC
	''')
	template = loader.get_template('affiliations2.twig')
	context = {'themes': themes,'liste_affiliations': liste_affiliations,}
	return HttpResponse(template.render(context, request))

############################ REQUETE 5 Liste de journaux par nombre et type de publications ############################

def journaux2(request):
	themes = Theme.objects.all().order_by('name')
	keys=StudyType.objects.all()
	dict_study_type={k : list(set([s.article.journal for s in StudyType_Articles.objects.filter(studytype=k)])) for k in keys }
	inv_dict_study_type= {}
	for k, v in dict_study_type.items():
		for j in v:
			if j not in inv_dict_study_type:
				inv_dict_study_type[j] = {'liste_study_types' : [k], 'nb_articles': Articles.objects.filter(journal=j).count()}
			else:
				inv_dict_study_type[j]['liste_study_types'].append(k)
	template = loader.get_template('journaux2.twig')
	context = {'themes': themes, 'dict_study_type': inv_dict_study_type , }
	return HttpResponse(template.render(context, request))

#################################### REQUETE 6 Liste d'articles/de jounaux/d'affiliations/de types de publications/des auteurs ####################################

def des_articles(request):
	themes = Theme.objects.all().order_by('name')
	nb_articles=Articles.objects.count()
	liste_articles = Articles.objects.all().order_by('id_article')
	paginator = Paginator(liste_articles, 25)
	page = request.GET.get('page')
	liste_articles2 = paginator.get_page(page)
	template = loader.get_template('des_articles.twig')
	context = {'themes': themes, 'liste_articles': liste_articles2, 'nb_articles': nb_articles,}
	return HttpResponse(template.render(context, request))

def affiliations(request):
	themes = Theme.objects.all().order_by('name')
	liste_affiliations=Affiliation.objects.all().order_by('id')
	paginator = Paginator(liste_affiliations, 25) 
	page = request.GET.get('page')
	liste_affiliations2 = paginator.get_page(page)
	nb_total_affiliations=Affiliation.objects.count()
	template = loader.get_template('affiliations.twig')
	context = {'themes': themes, 'liste_affiliations': liste_affiliations2, 'nb_total_affiliations':nb_total_affiliations,}
	return HttpResponse(template.render(context, request))

def journaux(request):
	themes = Theme.objects.all().order_by('name')
	journaux = Journal.objects.all().order_by('id_journal')
	paginator = Paginator(journaux, 25)
	page = request.GET.get('page')
	journaux2 = paginator.get_page(page)
	nb_total_journaux=Journal.objects.count()
	template = loader.get_template('journaux.twig')
	context = {'themes': themes, 'journaux': journaux2 , 'nb_total_journaux':nb_total_journaux,}
	return HttpResponse(template.render(context, request))

def studytypes(request):
	themes = Theme.objects.all().order_by('name')
	liste = StudyType.objects.all().order_by('name')
	nb_articles=StudyType_Articles.objects.distinct('article').count()
	paginator = Paginator(liste, 25)
	page = request.GET.get('page')
	liste2 = paginator.get_page(page)
	template = loader.get_template('studytypes.twig')
	context = {'themes': themes, 'liste': liste2, 'nb_articles': nb_articles,}
	return HttpResponse(template.render(context, request))

def auteurs(request):
	themes = Theme.objects.all().order_by('name')
	liste = Authors.objects.all().order_by('id')
	paginator = Paginator(liste, 25)
	page = request.GET.get('page')
	liste2 = paginator.get_page(page)
	nb_auteurs=Authors.objects.all().count()
	template = loader.get_template('auteurs.twig')
	context = {'themes': themes, 'liste': liste2, 'nb_auteurs' : nb_auteurs,}
	return HttpResponse(template.render(context, request))

#################################### REQUETE 7 Recherche par nom article/journal/affiliation/auteur ####################################

def des_articles2(request):
	themes = Theme.objects.all().order_by('name')
	if request.method=="POST":
		username=request.POST.get("username")
		u=username.upper()
		liste_articles=Articles.objects.filter(title__icontains=u).values().order_by('id_article')
	else:
		username=None
		liste_articles = Articles.objects.all()
	template = loader.get_template('des_articles2.twig')
	context = {'themes': themes,'liste_articles': liste_articles, 'username': username, }
	return HttpResponse(template.render(context, request))

def affiliations3(request):
	themes = Theme.objects.all().order_by('name')
	if request.method=="POST":
		username=request.POST.get("username")
		u=username.upper()
		liste_affiliations=Affiliation.objects.filter(name__icontains=u).values().order_by('id')
	else:
		username=None
		liste_affiliations = Affiliation.objects.all()
	template = loader.get_template('affiliations3.twig')
	context = {'themes': themes,'liste_affiliations': liste_affiliations, 'username':username}
	return HttpResponse(template.render(context, request))

def journaux3(request):
	themes = Theme.objects.all().order_by('name')
	if request.method=="POST":
		username=request.POST.get("username")
		u=username.upper()
		journaux=Journal.objects.filter(name__icontains=u).values().order_by('id_journal')
	else:
		username=None
		journaux = Journal.objects.all()
	template = loader.get_template('journaux3.twig')
	context = {'themes': themes,'journaux': journaux, 'username':username,}
	return HttpResponse(template.render(context, request))

def auteurs2(request):
	themes = Theme.objects.all().order_by('name')
	if request.method=="POST":
		username=request.POST.get("username")
		u=username.upper()
		liste_auteurs=Authors.objects.filter(name__icontains=u).values().order_by('id')
	else:
		username=None
		liste_auteurs = Authors.objects.all()
	template = loader.get_template('auteurs2.twig')
	context = {'themes': themes,'liste_auteurs': liste_auteurs, 'username': username, }
	return HttpResponse(template.render(context, request))

#################################### REQUETE 8 Données sur un article/journal/affiliation/type de publication/auteur ####################################

def un_article(request, name_article):
	themes = Theme.objects.all().order_by('name')
	le_article=Articles.objects.get(id_article=name_article)
	l=Author_Article.objects.filter(article=le_article)
	sous_theme=Article_Theme.objects.filter(article=le_article)
	study_types=StudyType_Articles.objects.filter(article=le_article)
	template = loader.get_template('un_article.twig')
	context = {'themes': themes ,'sous_theme' : sous_theme, 'study_types':study_types , 'le_article': le_article, 'liste_auteurs':l,}
	return HttpResponse(template.render(context, request))

def affiliation(request,name_affiliation):
	themes = Theme.objects.all().order_by('name')
	un_affiliation=Affiliation.objects.get(name=name_affiliation)
	le_type=un_affiliation.type
	le_country=un_affiliation.country
	l=Author_Affiliation.objects.filter(affiliation=un_affiliation).values('author')
	nb_articles=Author_Article.objects.filter(author__in=l).distinct('article').count()
	liste_articles=Author_Article.objects.filter(author__in=l).distinct('article').order_by('article_id')
	paginator = Paginator(liste_articles, 25)
	page = request.GET.get('page')
	liste_articles2 = paginator.get_page(page)
	template = loader.get_template('affiliation.twig')
	context = {
		'name_affiliation': name_affiliation, 'le_type': le_type, 'le_country':le_country,
		'liste_articles' : liste_articles2, 'nb_articles':nb_articles, 'themes': themes,
		}
	return HttpResponse(template.render(context, request))

def journal(request,name_journal):
	themes = Theme.objects.all().order_by('name')
	un_journal=Journal.objects.get(name=name_journal)
	nb_articles=Articles.objects.filter(journal_id=un_journal.id_journal).count()
	liste_articles=Articles.objects.filter(journal_id=un_journal.id_journal).order_by('id_article')
	paginator = Paginator(liste_articles, 25)
	page = request.GET.get('page')
	liste_articles2 = paginator.get_page(page)
	template = loader.get_template('journal.twig')
	context = {'themes': themes, 'nb_articles': nb_articles, 'liste_articles':liste_articles2, 'name_journal':name_journal, }
	return HttpResponse(template.render(context, request))

def studytype(request,name_studytype):
	themes = Theme.objects.all().order_by('name')
	un_study=StudyType.objects.get(name=name_studytype)
	nb_articles=StudyType_Articles.objects.filter(studytype=un_study).count()
	liste_articles=StudyType_Articles.objects.filter(studytype=un_study)
	template = loader.get_template('studytype.twig')
	context = {'themes': themes, 'nb_articles': nb_articles, 'liste_articles':liste_articles, 'name_study':name_studytype, }
	return HttpResponse(template.render(context, request))

def un_auteur(request,name_auteur):
	themes = Theme.objects.all().order_by('name')
	a=Authors.objects.get(name=name_auteur)
	liste_articles=Author_Article.objects.filter(author=a).distinct('article').order_by('article_id')
	nb_articles=len(liste_articles)
	aff=Author_Affiliation.objects.filter(author=a)
	context = {'themes': themes, 'nb_articles': nb_articles, 'liste_articles':liste_articles, 'auteur':a, 'liste_affiliations':aff, }
	template = loader.get_template('un_auteur.twig')
	return HttpResponse(template.render(context, request))
