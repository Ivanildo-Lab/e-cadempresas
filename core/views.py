from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.http import HttpResponse
from django.template.loader import get_template
from django.utils import timezone
from xhtml2pdf import pisa
import io
from .forms import EmpresaForm, SocioFormSet, CategoriaTabelaForm 
from django.contrib.auth.decorators import login_required 
from django.contrib.auth import logout 
from django.contrib import messages




from .models import Empresa, Socio, CategoriaTabela
from .forms import EmpresaForm, SocioFormSet 

# --- DASHBOARD ---
@login_required
def dashboard(request):
    total_empresas = Empresa.objects.count()
    ativas = Empresa.objects.filter(ativo=True).count()
    inativas = total_empresas - ativas
    regimes = Empresa.objects.values('regime_tributacao__descricao').annotate(total=Count('id'))
    ultimas_empresas = Empresa.objects.order_by('-id')[:5]

    context = {
        'total_empresas': total_empresas,
        'ativas': ativas,
        'inativas': inativas,
        'regimes': regimes,
        'ultimas_empresas': ultimas_empresas,
    }
    return render(request, 'core/dashboard.html', context)

# --- LISTAGEM ---
@login_required
def empresa_list(request):
    empresa_list = Empresa.objects.all().order_by('razao_social')
    q = request.GET.get('q')
    if q:
        empresa_list = empresa_list.filter(
            Q(razao_social__icontains=q) | Q(cnpj__icontains=q) | Q(nire__icontains=q)
        )
    status = request.GET.get('status')
    if status == 'ativos':
        empresa_list = empresa_list.filter(ativo=True)
    elif status == 'inativos':
        empresa_list = empresa_list.filter(ativo=False)

    sit_cad = request.GET.get('sit_cad')
    if sit_cad:
        empresa_list = empresa_list.filter(situacao_cadastro_id=sit_cad)

    situacoes_cadastro = CategoriaTabela.objects.filter(tipo='SITUACAOCADASTRO')
    paginator = Paginator(empresa_list, 10)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'core/empresa_list.html', {
        'page_obj': page_obj,
        'situacoes_cadastro': situacoes_cadastro
    })

# --- CRUD ---
@login_required
def empresa_create(request):
    if request.method == 'POST':
        form = EmpresaForm(request.POST)
        formset = SocioFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            empresa = form.save()
            formset.instance = empresa
            formset.save()
            return redirect('empresa_list')
    else:
        form = EmpresaForm()
        formset = SocioFormSet()
    return render(request, 'core/empresa_form.html', {'form': form, 'formset': formset, 'titulo': 'Nova Empresa'})

@login_required
def empresa_edit(request, pk):
    empresa = get_object_or_404(Empresa, pk=pk)
    if request.method == 'POST':
        form = EmpresaForm(request.POST, instance=empresa)
        formset = SocioFormSet(request.POST, instance=empresa)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            return redirect('empresa_list')
    else:
        form = EmpresaForm(instance=empresa)
        formset = SocioFormSet(instance=empresa)
    return render(request, 'core/empresa_form.html', {'form': form, 'formset': formset, 'titulo': 'Editar Empresa'})

@login_required
def empresa_delete(request, pk):
    empresa = get_object_or_404(Empresa, pk=pk)
    if request.method == 'POST':
        empresa.delete()
        return redirect('empresa_list')
    # Como você quer Modal, essa view agora só processa o POST da exclusão
    return redirect('empresa_list')

# --- PDF ---
@login_required
def empresa_report_pdf(request):
    # 1. Filtros (Mesma lógica da listagem)
    empresas = Empresa.objects.all().order_by('razao_social')
    q = request.GET.get('q')
    if q:
        empresas = empresas.filter(Q(razao_social__icontains=q) | Q(cnpj__icontains=q))
    
    sit_cad = request.GET.get('sit_cad')
    if sit_cad:
        empresas = empresas.filter(situacao_cadastro_id=sit_cad)

    # 2. Contexto
    context = {
        'empresas': empresas,
        'data_emissao': timezone.now(),
        'filtros': {
            'busca': q,
            'situacao': CategoriaTabela.objects.filter(id=sit_cad).first() if sit_cad else 'TODAS'
        }
    }

    # 3. Gerar PDF
    template = get_template('core/empresa_report_pdf.html')
    html = template.render(context)
    result = io.BytesIO()
    
    # O segredo da codificação está no encoding='utf-8' dentro do pisa
    pdf = pisa.pisaDocument(io.BytesIO(html.encode("utf-8")), result, encoding='utf-8')
    
    if not pdf.err:
        response = HttpResponse(result.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = 'filename="relatorio_empresas.pdf"'
        return response
    
    return HttpResponse("Erro ao gerar PDF", status=400)

@login_required
def tabela_list(request):
    tipo = request.GET.get('tipo', 'CNAE')
    q_tab = request.GET.get('q_tab', '') # Captura o termo de busca
    
    # Filtra pelo tipo selecionado no menu (CNAE, REGIME, etc)
    itens = CategoriaTabela.objects.filter(tipo=tipo)
    
    # Se houver busca, filtra por código OU descrição
    if q_tab:
        itens = itens.filter(
            Q(codigo__icontains=q_tab) | Q(descricao__icontains=q_tab)
        )
    
    itens = itens.order_by('descricao')
    
    # Paginação (15 por página)
    paginator = Paginator(itens, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'core/tabela_list.html', {
        'page_obj': page_obj,
        'tipo': tipo,
        'q_tab': q_tab
    })

@login_required
def tabela_create(request):
    tipo = request.GET.get('tipo', 'CNAE')
    if request.method == 'POST':
        form = CategoriaTabelaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(f'/tabelas/?tipo={tipo}')
    else:
        form = CategoriaTabelaForm(initial={'tipo': tipo})
    
    return render(request, 'core/tabela_form.html', {'form': form, 'tipo': tipo, 'titulo': 'Novo Registro'})

@login_required
def tabela_edit(request, pk):
    item = get_object_or_404(CategoriaTabela, pk=pk)
    tipo = item.tipo
    if request.method == 'POST':
        form = CategoriaTabelaForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect(f'/tabelas/?tipo={tipo}')
    else:
        form = CategoriaTabelaForm(instance=item)
    
    return render(request, 'core/tabela_form.html', {'form': form, 'tipo': tipo, 'titulo': 'Editar Registro'})

@login_required
def tabela_delete(request, pk):
    item = get_object_or_404(CategoriaTabela, pk=pk)
    tipo = item.tipo
    item.delete()
    return redirect(f'/tabelas/?tipo={tipo}')


def custom_logout(request):
    logout(request)
    # Opcional: Adicionar uma mensagem que aparecerá na tela de login
    messages.info(request, "Você saiu do sistema com segurança.")
    return redirect('login')