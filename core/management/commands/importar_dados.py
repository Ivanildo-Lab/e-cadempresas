import csv
import os
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils.dateparse import parse_datetime
from core.models import Empresa, Socio, CategoriaTabela

class Command(BaseCommand):
    help = 'Importa dados completos dos CSVs legados'

    def handle(self, *args, **options):
        pasta_dados = os.path.join(settings.BASE_DIR, 'dados_legados')
        
        # 1. IMPORTAR TODAS AS TABELAS AUXILIARES
        self.stdout.write("Importando Tabelas Auxiliares (CNAEs, Regimes, etc)...")
        with open(os.path.join(pasta_dados, 'Tbl_Tabelas.csv'), 'r', encoding='utf-8-sig') as f:
            next(f)
            reader = csv.DictReader(f)
            for row in reader:
                CategoriaTabela.objects.update_or_create(
                    id_legado=int(row['IdTabela']),
                    defaults={
                        'tipo': row['SelecaoTabela'],
                        'codigo': row['Grupo'] if row['Grupo'] else row['Codigo'],
                        'descricao': row['DescricaoTabela']
                    }
                )

        # 2. IMPORTAR EMPRESAS
        self.stdout.write("Importando Empresas com relacionamentos...")
        empresa_map = {}
        with open(os.path.join(pasta_dados, 'Tbl_Clientes.csv'), 'r', encoding='utf-8-sig') as f:
            next(f)
            reader = csv.DictReader(f)
            for row in reader:
                cnpj_limpo = row['CGCCliente'].replace('.', '').replace('/', '').replace('-', '').strip()
                if not cnpj_limpo: continue

                # Converter Capital Social
                valor_str = row['CapitaDaEmpresa'].replace(',', '').strip() if row['CapitaDaEmpresa'] else "0"
                
                # Converter Data (Formato: 2001-09-03T07:00:00Z)
                data_inicio = None
                if row['InicioDeAtividade']:
                    dt = parse_datetime(row['InicioDeAtividade'])
                    if dt: data_inicio = dt.date()

                # Buscar Objetos Relacionados pelos IDs do CSV
                def get_tab(field_name):
                    val = row.get(field_name)
                    if val and val.isdigit():
                        return CategoriaTabela.objects.filter(id_legado=int(val)).first()
                    return None

                empresa, created = Empresa.objects.update_or_create(
                    cnpj=cnpj_limpo,
                    defaults={
                        'razao_social': row['Nomecliente'],
                        'nire': row['NIRE'], # Adicionado importação do NIRE
                        'endereco': row['EnderecoCliente'],
                        'bairro': row['BairroCliente'],
                        'cidade': row['CidadeCliente'],
                        'estado': row['EstadoCliente'],
                        'cep': row['Cepcliente'],
                        'telefone': row['Fonecliente'],
                        'email': row['Email'],
                        'observacoes': row['Obs'],
                        'capital_social': Decimal(valor_str),
                        'inicio_atividade': data_inicio,
                        'ativo': True if row['Ativo'].lower() == 'true' else False,
                        'cnae_principal': get_tab('CNAE'),
                        'tipo_empresa': get_tab('CodTipoDeempresa'),
                        'regime_tributacao': get_tab('RegimeDePagamento'),
                        'situacao_cadastro': get_tab('SituacaoCadastro'),
                        # situacao_empresa removido daqui
                    }
                )
                empresa_map[row['Codcliente']] = empresa

        # 3. IMPORTAR SÓCIOS
        self.stdout.write("Importando Sócios...")
        with open(os.path.join(pasta_dados, 'Tbl_Socios.csv'), 'r', encoding='utf-8-sig') as f:
            next(f)
            reader = csv.DictReader(f)
            for row in reader:
                empresa_instancia = empresa_map.get(row['CodCliente'])
                if empresa_instancia:
                    v_part = row['ValorDaPaticipacao'].replace(',', '').strip() if row['ValorDaPaticipacao'] else "0"
                    Socio.objects.get_or_create(
                        empresa=empresa_instancia,
                        nome=row['NomeSocio'],
                        cpf=row['CPFSocio'].replace('.', '').replace('-', '').strip(),
                        defaults={'valor_participacao': Decimal(v_part)}
                    )

        self.stdout.write(self.style.SUCCESS('Migração completa concluída!'))