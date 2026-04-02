# Aplicativo de Relacionamento de Tabelas SharePoint

Este aplicativo simples permite relacionar e filtrar dados das tabelas `tbl_clientes` e `tbl_tabelas` do SharePoint.

## Pré-requisitos

- Python 3.13 ou superior
- Bibliotecas: pandas, streamlit

## Como usar

1. Exporte os dados das listas SharePoint para arquivos CSV:
   - `tbl_clientes` para `Dados/clientes.csv`
   - `tbl_tabelas` para `Dados/tabelas.csv`

   Certifique-se de que as colunas correspondam às estruturas fornecidas.

2. Execute o aplicativo:
   ```
   streamlit run app.py
   ```

3. No navegador, use os filtros na barra lateral para selecionar Grupo ou Descrição da tabela, e veja a lista filtrada de clientes.

## Relacionamento

- O campo `SitEmpresa` da `tbl_clientes` é usado como chave estrangeira para o campo `Codigo` da `tbl_tabelas`.