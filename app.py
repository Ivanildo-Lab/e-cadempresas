import streamlit as st
import pandas as pd
import base64
from io import BytesIO
from reportlab.lib.pagesizes import letter, A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from datetime import datetime

# Caminhos para os arquivos CSV (assumindo que estão na pasta Dados/)
clientes_path = 'Dados/clientes.csv'
tabelas_path = 'Dados/tabelas.csv'

st.set_page_config(layout="wide", page_title="Lista de empresas cadastradas")
st.title('📋 Lista de empresas cadastradas')

# Carregar dados
try:
    df_clientes = pd.read_csv(clientes_path)
    df_tabelas = pd.read_csv(tabelas_path)
except FileNotFoundError:
    st.error("Arquivos CSV não encontrados. Certifique-se de que 'clientes.csv' e 'tabelas.csv' estão na pasta 'Dados/'.")
    st.stop()

# Encontrar colunas de relacionamento
join_key_clientes = None
join_key_tabelas = None

for col in df_clientes.columns:
    if 'situacaocadastro' in col.lower():
        join_key_clientes = col
        break

for col in df_tabelas.columns:
    if 'idtabela' in col.lower() or 'id_tabela' in col.lower() or 'codigo' in col.lower():
        join_key_tabelas = col
        break

if join_key_clientes and join_key_tabelas:
    df_merged = pd.merge(df_clientes, df_tabelas, left_on=join_key_clientes, right_on=join_key_tabelas, how='left', suffixes=('_clientes', '_tabelas'))
else:
    st.error(f"Não foi possível encontrar as colunas de relacionamento.")
    st.stop()

# ============ FILTROS ============
st.sidebar.header('🔍 Filtros')

# Filtro por Descrição da Tabela
desc_filter_col = None
for col in df_merged.columns:
    if 'descricaotabela' in col.lower():
        desc_filter_col = col
        break

if desc_filter_col:
    descricoes_lista = df_merged[desc_filter_col].dropna().unique()
    descricao_selecionada = st.sidebar.selectbox('Selecionar Descrição da Tabela', ['Todas'] + list(sorted(descricoes_lista)))
else:
    descricao_selecionada = 'Todas'
    st.sidebar.warning("Campo 'DescricaoTabela' não encontrado")

# Aplicar filtro
df_filtrado = df_merged.copy()
if descricao_selecionada != 'Todas':
    if desc_filter_col:
        df_filtrado = df_filtrado[df_filtrado[desc_filter_col] == descricao_selecionada]

# ============ FUNÇÃO PARA GERAR PDF ============
def gerar_pdf_relatorio(df, titulo, nome_arquivo):
    """Gera um PDF com os dados filtrados em formato paisagem"""
    output = BytesIO()
    page_size = landscape(A4)
    doc = SimpleDocTemplate(output, pagesize=page_size, rightMargin=0.4*inch, leftMargin=0.4*inch, 
                           topMargin=0.6*inch, bottomMargin=0.6*inch)
    
    elements = []
    styles = getSampleStyleSheet()
    
    # Título
    titulo_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor('#1f77b4'),
        spaceAfter=12,
        alignment=1
    )
    elements.append(Paragraph(titulo, titulo_style))
    
    # Data do relatório
    data_style = ParagraphStyle('DataStyle', parent=styles['Normal'], fontSize=9, textColor=colors.grey)
    elements.append(Paragraph(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}", data_style))
    elements.append(Spacer(1, 0.3*inch))
    
    # Info de filtros
    filtro_style = ParagraphStyle('FiltroStyle', parent=styles['Normal'], fontSize=10, textColor=colors.darkblue)
    elements.append(Paragraph(f"<b>Total de registros:</b> {len(df)}", filtro_style))
    elements.append(Spacer(1, 0.15*inch))
    
    # Preparar dados da tabela
    if len(df) > 0:
        # Selecionar apenas as 5 colunas principais solicitadas
        colunas_relatorio = []
        nomes_colunas = []
        
        # Mapa de colunas em ORDEM (lista de tuplas para manter ordem)
        mapa_colunas_ordenado = [
            ('Title', 'Nome'),
            ('Nomecliente', 'Nome'),
            ('EnderecoCliente', 'Endereço'),
            ('Fonecliente', 'Telefone'),
            ('CidadeCliente', 'Cidade'),
            ('EstadoCliente', 'UF'),
            ('CGCCliente', 'CNPJ'),
            ('INSCCliente', 'I.E.')  # Abreviado para "I.E."
        ]
        
        # Procurar as colunas exatas em ordem
        for col_orig, col_nome in mapa_colunas_ordenado:
            if col_orig in df.columns:
                colunas_relatorio.append(col_orig)
                nomes_colunas.append(col_nome)
        
        # Se não encontrar, usar defaults
        if not colunas_relatorio:
            colunas_relatorio = df.columns[:5].tolist()
            nomes_colunas = colunas_relatorio
        
        # Função para formatar valores (tratar NaN como vazio)
        def formatar_valor(valor, col_name=''):
            if pd.isna(valor):
                return ''
            if not isinstance(valor, str):
                valor = str(valor)
            
            # Remove o ".0" dos números formatados como string
            if valor.endswith('.0'):
                valor = valor[:-2]
            
            # Formatar CNPJ
            if 'cgc' in col_name.lower() or 'cnpj' in col_name.lower():
                # Remove caracteres não numéricos
                cnpj_limpo = ''.join(c for c in valor if c.isdigit())
                # Aplicar máscara XX.XXX.XXX/XXXX-XX
                if len(cnpj_limpo) == 14:
                    return f'{cnpj_limpo[:2]}.{cnpj_limpo[2:5]}.{cnpj_limpo[5:8]}/{cnpj_limpo[8:12]}-{cnpj_limpo[12:]}'
                return cnpj_limpo
            
            return valor
        
        # Criar dados da tabela com Paragraph para quebra de linha
        style_normal = ParagraphStyle('Normal', parent=styles['Normal'], fontSize=8, leading=10, wordWrap='CJK')
        dados_tabela = []
        
        # Header
        header_cells = []
        for col_nome in nomes_colunas:
            header_cells.append(Paragraph('<b>' + col_nome + '</b>', style_normal))
        dados_tabela.append(header_cells)
        
        # Dados
        for idx, row in df[colunas_relatorio].iterrows():
            linha = []
            for col_orig, val in zip(colunas_relatorio, row):
                valor_formatado = formatar_valor(val, col_orig)
                # Criar Paragraph para permitir quebra de linha
                paragraph = Paragraph(valor_formatado, style_normal)
                linha.append(paragraph)
            dados_tabela.append(linha)
        
        # Calcular larguras das colunas para paisagem
        col_widths = []
        for col_orig in colunas_relatorio:
            if 'title' in col_orig.lower() or 'nomecliente' in col_orig.lower():
                col_widths.append(1.6 * inch)  # Nome
            elif 'endereco' in col_orig.lower():
                col_widths.append(2.8 * inch)  # Endereço
            elif 'telefone' in col_orig.lower():
                col_widths.append(1.1 * inch)  # Telefone
            elif 'cidade' in col_orig.lower():
                col_widths.append(1.1 * inch)  # Cidade
            elif 'uf' in col_orig.lower() or 'estado' in col_orig.lower():
                col_widths.append(0.4 * inch)  # UF
            elif 'cnpj' in col_orig.lower() or 'cgc' in col_orig.lower():
                col_widths.append(1.3 * inch)  # CNPJ (aumentado em 0.2)
            elif 'inscri' in col_orig.lower():
                col_widths.append(0.9 * inch)  # I.E.
            else:
                col_widths.append(1.0 * inch)  # Outros
        
        # Criar tabela
        tabela = Table(dados_tabela, colWidths=col_widths)
        tabela.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f77b4')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 7),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),  # Alinhamento superior para quebra de linha
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 1), (-1, -1), 6),  # Padding superior para dados
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),  # Padding inferior para dados
        ]))
        elements.append(tabela)
    else:
        elements.append(Paragraph("<b>Nenhum registro encontrado com os filtros aplicados.</b>", styles['Normal']))
    
    # Gerar PDF
    doc.build(elements)
    output.seek(0)
    return output.getvalue()

# ============ EXIBIR DADOS ============
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("📊 Total de Clientes", len(df_filtrado))

with col2:
    if descricao_selecionada != 'Todas':
        st.metric("📌 Descrição Selecionada", descricao_selecionada)

with col3:
    pass

# Mostrar tabela
st.subheader('Clientes')
st.dataframe(df_filtrado, use_container_width=True)

# ============ DOWNLOADS ============
st.sidebar.header('📥 Exportar')

col1, col2, col3 = st.sidebar.columns(3)

with col1:
    if st.button('CSV'):
        csv = df_filtrado.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()
        href = f'<a href="data:file/csv;base64,{b64}" download="relatorio_clientes.csv">📥 CSV</a>'
        st.markdown(href, unsafe_allow_html=True)

with col2:
    if st.button('Excel'):
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_filtrado.to_excel(writer, sheet_name='Clientes', index=False)
        output.seek(0)
        b64 = base64.b64encode(output.getvalue()).decode()
        href = f'<a href="data:application/vnd.ms-excel;base64,{b64}" download="relatorio_clientes.xlsx">📊 Excel</a>'
        st.markdown(href, unsafe_allow_html=True)

with col3:
    if st.button('PDF'):
        pdf_bytes = gerar_pdf_relatorio(df_filtrado, f'Relatório de Clientes - {descricao_selecionada if descricao_selecionada != "Todas" else "Todas as Descrições"}', 'relatorio_clientes.pdf')
        b64 = base64.b64encode(pdf_bytes).decode()
        href = f'<a href="data:application/pdf;base64,{b64}" download="relatorio_clientes.pdf">📄 PDF</a>'
        st.markdown(href, unsafe_allow_html=True)