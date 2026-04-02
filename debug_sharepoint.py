from office365.runtime.auth.user_credential import UserCredential
from office365.sharepoint.client_context import ClientContext
import pandas as pd
import json

# Configurações do SharePoint
site_url = "https://76tfdt.sharepoint.com/sites/AliancaContabilidade"
username = "geficogestor@76tfdt.onmicrosoft.com"
password = "gefico@1234"

try:
    print("Tentando conectar ao SharePoint...")
    credentials = UserCredential(username, password)
    ctx = ClientContext(site_url).with_credentials(credentials)
    
    # Testar conexão carregando o web
    web = ctx.web.get().execute_query()
    print(f"✓ Conexão ao SharePoint bem-sucedida! Site: {web.properties['Title']}")
    
    # Carregar campos da lista TClientes
    print("\n=== TClientes - Estrutura de Campos ===")
    list_clientes = ctx.web.lists.get_by_title("TClientes")
    fields = list_clientes.fields.get().execute_query()
    print("Campos disponíveis:")
    for field in fields:
        if hasattr(field, 'properties'):
            print(f"  - {field.properties.get('InternalName', 'N/A')}: {field.properties.get('Title', 'N/A')}")
    
    # Carregar dados da lista TClientes
    print("\n=== TClientes - Dados ===")
    items_clientes = list_clientes.items.get().execute_query()
    print(f"Total de itens: {len(items_clientes)}")
    if len(items_clientes) > 0:
        print("\nPrimeiro item:")
        primeiro = items_clientes[0]
        for key in sorted(primeiro.properties.keys())[:20]:  # Mostrar primeiras 20 propriedades
            valor = primeiro.properties[key]
            if not isinstance(valor, dict):
                print(f"  {key}: {valor}")
    
    # Carregar campos da lista Tbl_Tabelas1
    print("\n=== Tbl_Tabelas1 - Estrutura de Campos ===")
    list_tabelas = ctx.web.lists.get_by_title("Tbl_Tabelas1")
    fields = list_tabelas.fields.get().execute_query()
    print("Campos disponíveis:")
    for field in fields:
        if hasattr(field, 'properties'):
            print(f"  - {field.properties.get('InternalName', 'N/A')}: {field.properties.get('Title', 'N/A')}")
    
    # Carregar dados da lista Tbl_Tabelas1
    print("\n=== Tbl_Tabelas1 - Dados ===")
    items_tabelas = list_tabelas.items.get().execute_query()
    print(f"Total de itens: {len(items_tabelas)}")
    if len(items_tabelas) > 0:
        print("\nPrimeiro item:")
        primeiro = items_tabelas[0]
        for key in sorted(primeiro.properties.keys())[:20]:  # Mostrar primeiras 20 propriedades
            valor = primeiro.properties[key]
            if not isinstance(valor, dict):
                print(f"  {key}: {valor}")
        
except Exception as e:
    print(f"✗ Erro: {str(e)}")
    import traceback
    traceback.print_exc()
