"""projet_bddr URL Configuration
The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include,path

urlpatterns = [
    path('appli_covid19/', include('appli_covid19.urls')),
    path('appli_covid19/journaux/', include('appli_covid19.urls')),
    path('appli_covid19/studytypes/', include('appli_covid19.urls')),
    path('appli_covid19/journaux2/', include('appli_covid19.urls')),
    path('appli_covid19/journaux3/', include('appli_covid19.urls')),
    path('appli_covid19/articles/', include('appli_covid19.urls')),
    path('appli_covid19/articles2/', include('appli_covid19.urls')),
    path('appli_covid19/auteurs/', include('appli_covid19.urls')),
    path('appli_covid19/auteurs2/', include('appli_covid19.urls')),
    path('appli_covid19/histogram_annee/', include('appli_covid19.urls')),
    path('appli_covid19/histogram_date/', include('appli_covid19.urls')),
    path('appli_covid19/histogram_mois/', include('appli_covid19.urls')),
    path('appli_covid19/histogram_semaine/', include('appli_covid19.urls')),
    path('appli_covid19/affiliations/', include('appli_covid19.urls')),
    path('appli_covid19/affiliations2/', include('appli_covid19.urls')),
    path('appli_covid19/affiliations3/', include('appli_covid19.urls')),
    path('appli_covid19/affiliations/<name_affiliation>', include('appli_covid19.urls')),
    path('appli_covid19/theme/<name_theme>', include('appli_covid19.urls')),
    path('appli_covid19/journaux/<name_journal>', include('appli_covid19.urls')),
    path('appli_covid19/studytypes/<name_studytype>', include('appli_covid19.urls')),
    path('appli_covid19/articles/<name_article>', include('appli_covid19.urls')),
    path('appli_covid19/sous_theme/<name_sous_theme>', include('appli_covid19.urls')),
    path('appli_covid19/auteurs/<name_auteur>', include('appli_covid19.urls')),
    path('admin/', admin.site.urls),
]
