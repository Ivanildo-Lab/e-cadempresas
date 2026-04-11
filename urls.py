from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views # Importe as views de autenticação
from core import views


urlpatterns = [
    path('admin/', admin.site.urls),
    
    # LOGIN E LOGOUT
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', views.custom_logout, name='logout'),    
    
    path('', views.dashboard, name='dashboard'),
    
    # Rotas de Empresas (Clientes)
    path('empresas/', views.empresa_list, name='empresa_list'),
    path('empresas/novo/', views.empresa_create, name='empresa_create'),
    path('empresas/<int:pk>/editar/', views.empresa_edit, name='empresa_edit'),
    path('empresas/<int:pk>/excluir/', views.empresa_delete, name='empresa_delete'),
    path('empresas/relatorio/', views.empresa_report_pdf, name='empresa_report_pdf'),
    
    # Rotas de Tabelas Auxiliares (CNAE, Regimes, etc)
    path('tabelas/', views.tabela_list, name='tabela_list'),
    path('tabelas/novo/', views.tabela_create, name='tabela_create'),
    path('tabelas/<int:pk>/editar/', views.tabela_edit, name='tabela_edit'),
    path('tabelas/<int:pk>/excluir/', views.tabela_delete, name='tabela_delete'),
]