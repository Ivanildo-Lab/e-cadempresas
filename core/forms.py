# core/forms.py 
from django import forms
from django.forms import inlineformset_factory
from .models import Empresa, Socio, CategoriaTabela

class EmpresaForm(forms.ModelForm):
    class Meta:
        model = Empresa
        fields = '__all__'
        widgets = {
            'razao_social': forms.TextInput(attrs={'class': 'form-control'}),
            'cnpj': forms.TextInput(attrs={'class': 'form-control', 'data-mask': '00.000.000/0000-00'}),
            'nire': forms.TextInput(attrs={'class': 'form-control'}),
            'inicio_atividade': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'capital_social': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'endereco': forms.TextInput(attrs={'class': 'form-control'}),
            'bairro': forms.TextInput(attrs={'class': 'form-control'}),
            'cidade': forms.TextInput(attrs={'class': 'form-control'}),
            'estado': forms.TextInput(attrs={'class': 'form-control'}),
            'cep': forms.TextInput(attrs={'class': 'form-control', 'data-mask': '00000-000'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'cnae_principal': forms.Select(attrs={'class': 'form-control select2'}),
            'tipo_empresa': forms.Select(attrs={'class': 'form-control'}),
            'regime_tributacao': forms.Select(attrs={'class': 'form-control'}),
            'situacao_cadastro': forms.Select(attrs={'class': 'form-control'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super(EmpresaForm, self).__init__(*args, **kwargs)
        # Filtros para que cada campo mostre apenas as categorias corretas
        self.fields['cnae_principal'].queryset = CategoriaTabela.objects.filter(tipo='CNAE').order_by('descricao')
        self.fields['tipo_empresa'].queryset = CategoriaTabela.objects.filter(tipo='TIPOEMPRESA').order_by('descricao')
        self.fields['regime_tributacao'].queryset = CategoriaTabela.objects.filter(tipo='REGIMEPAGAMENTO').order_by('descricao')
        self.fields['situacao_cadastro'].queryset = CategoriaTabela.objects.filter(tipo='SITUACAOCADASTRO').order_by('descricao')

# Criando o Formset para Sócios (Mestre/Detalhe)
SocioFormSet = inlineformset_factory(
    Empresa, Socio, 
    fields=('nome', 'cpf', 'valor_participacao'),
    extra=1, # Quantos formulários em branco aparecem no início
    can_delete=True,
    widgets={
        'nome': forms.TextInput(attrs={'class': 'form-control'}),
        'cpf': forms.TextInput(attrs={'class': 'form-control', 'data-mask': '000.000.000-00'}),
        'valor_participacao': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
    }
)

class CategoriaTabelaForm(forms.ModelForm):
    class Meta:
        model = CategoriaTabela
        fields = ['tipo', 'codigo', 'descricao']
        widgets = {
            'tipo': forms.HiddenInput(), # Fica escondido pois já sabemos o tipo pelo menu
            'codigo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 6920601'}),
            'descricao': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Descrição detalhada'}),
        }
