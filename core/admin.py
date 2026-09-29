from django.contrib import admin
from .models import Empresa, Socio, CategoriaTabela

class SocioInline(admin.TabularInline):
    model = Socio
    extra = 0

@admin.register(CategoriaTabela)
class CategoriaTabelaAdmin(admin.ModelAdmin):
    list_display = ('id_legado', 'tipo', 'codigo', 'descricao')
    list_filter = ('tipo',)
    search_fields = ('descricao', 'codigo')

# ... (imports e SocioInline iguais)

@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ('razao_social', 'cnpj', 'inscricao_estadual', 'regime_tributacao', 'situacao_cadastro', 'ativo')
    search_fields = ('razao_social', 'cnpj', 'nire', 'inscricao_estadual', 'inscricao_municipal', 'cidade', 'email')
    list_filter = ('regime_tributacao', 'situacao_cadastro', 'ativo')
    
    fieldsets = (
        ('Identificação', {'fields': ('razao_social', 'cnpj', 'nire', 'inscricao_estadual', 'inscricao_municipal', 'inicio_atividade', 'capital_social', 'ativo')}),
        ('Endereço e Contato', {'fields': ('endereco', 'bairro', 'cidade', 'estado', 'cep', 'telefone', 'email')}),
        ('Classificação Contábil', {'fields': ('cnae_principal', 'tipo_empresa', 'regime_tributacao', 'situacao_cadastro')}),
        ('Notas', {'fields': ('observacoes',)}),
    )
    inlines = [SocioInline]