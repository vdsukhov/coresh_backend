"""
URL configuration for coresh_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from django.urls import path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path("submit-genes", views.submit_genes, name="submit_genes"),
    path('check-job', views.check_job_status, name="check_job"),
    path('create-final-tables', views.create_final_tables, name="create_final_tables"),
    path('get-ranking-result', views.get_ranking_result, name="get_ranking_result"),
    path('get-enriched-words', views.get_enriched_words, name="get_enriched_words"),
    path('check-result-files', views.check_result_files, name="check_result_files")
]
