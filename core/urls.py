from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    
    # Empresas
    path('empresas/', views.empresa_list, name='empresa_list'),
    path('empresas/novo/', views.empresa_create, name='empresa_create'),
    path('empresas/<int:pk>/editar/', views.empresa_edit, name='empresa_edit'),
    path('empresas/relatorio/', views.empresa_report_pdf, name='empresa_report_pdf'),
    
    # Sócios
    path('socios/', views.socio_list, name='socio_list'),
    path('socios/novo/', views.socio_create, name='socio_create'),
    
    # Tabelas Auxiliares
    path('tabelas/', views.tabela_list, name='tabela_list'),
    path('tabelas/novo/', views.tabela_create, name='tabela_create'),
    path('tabelas/<int:pk>/editar/', views.tabela_edit, name='tabela_edit'),
    path('tabelas/<int:pk>/excluir/', views.tabela_delete, name='tabela_delete'),
    ]