import mysql.connector
import pandas as pd
import streamlit as st
import plotly.express as px
import calendar
from babel.numbers import format_currency
from babel import Locale
from streamlit_option_menu import option_menu
from datetime import datetime, timedelta
import facebook
import pickle
from pathlib import Path
import streamlit_authenticator as stauth
st.set_page_config(layout='wide')

locale_brazil = Locale.parse('pt_BR')

# Cor desejada (pode ser um código hexadecimal, nome da cor, etc.)
cor_da_sidebar = "#d3d3d3"  



st.markdown("""
<style>
    [data-testid=stSidebar] {
        background-color: #d3d3d3;
    }
</style>
""", unsafe_allow_html=True)


# URL da imagem que você quer exibir
url_da_imagem = "https://videosoft.com.br/wp-content/uploads/2023/01/logo-SITE-BAIXA.png"

# Exibindo a imagem na sidebar
st.sidebar.image(url_da_imagem, use_column_width=True)


#Cria o Menu
with st.sidebar:
    selected = option_menu(
        menu_title=None,
        options= ['Home','Meta', 'Vendas'],
        icons=['globe', 'bar-chart','graph-up']
    )

# Token de acesso
access_token = 'EAAKTPyYyj6cBO2vkdpo0NRlGLTW9egoC5w1jqEeAfCMvBoBNjaIIRegXIYFJEnjOigu0JQoC2GHUMRVSHKbEEZCm8ARleJSXM15hNmQdQOsRyItQFBZC6yzUcPWTbkpbZAAATeytLZAZC9JSls1nTE5fQHZBZCVsOclrCEtEVdrmZCqtmUV385mCBWZAHZCzV5Tcmr'

# Inicializar o objeto GraphAPI
graph = facebook.GraphAPI(access_token)

info_conta = graph.get_object('me', fields='id,name,adaccounts')

start_date = datetime(2024,1,1)
# Sidebar para selecionar as datas
start_date = st.sidebar.date_input('Data de início')
end_date = st.sidebar.date_input('Data de término')

# Calcular o tamanho do intervalo selecionado pelo usuário
interval_size = (end_date - start_date).days

# Calcular as datas de início e término para o período anterior
previous_start_date = start_date - timedelta(days=interval_size)
previous_end_date = end_date - timedelta(days=interval_size)

# ID da conta de anúncio desejada
ad_account_id = 'act_163324477982807'


# Agora você pode usar a variável valor_gasto para outros cálculos
#if valor_gasto is not None:
    #st.write("Valor gasto no período:", valor_gasto)
#else:
    #st.write("Nenhuma estatística disponível para este período.")


# Informações de conexão
host = "35.232.119.93"
database = "eloz"
username = "dash_user"
password = "useSidenuNCo"

# Conectando ao banco de dados
connection = mysql.connector.connect(
    host=host,
    database=database,
    user=username,
    password=password
)

# Cursor para executar consultas SQL
cursor = connection.cursor()

# Obtendo a lista de tabelas
cursor.execute("SHOW TABLES;")
tabelas = cursor.fetchall()

# Mapeamento de relacionamentos
relacionamentos = {
    'leads': {'companies_leads': 'ID', 'mod_deals_stages': 'stage_id'},
    'mod_deals_companies': {'mod_deals': 'deal_id'},
    'mod_deals_pipelines': {'mod_deals': 'pipelines_id'},
    'mod_fields': {'mod_field_options': 'field_id'}
}


if selected == 'Vendas':

    if start_date is not None and end_date is not None:
        try:
            # Formatar as datas para o formato esperado pela API do Facebook
            since_date = start_date.strftime('%Y-%m-%d')
            until_date = end_date.strftime('%Y-%m-%d')
            
            # Obter as estatísticas de spend para toda a conta de anúncios no intervalo de datas especificado
            insights_params = {
                'fields': 'spend',
                'level': 'account',
                'time_range': f'{{"since":"{since_date}","until":"{until_date}"}}',
                'access_token': access_token
            }
            stats = graph.get_object(ad_account_id + '/insights', **insights_params)

            # Criar um DataFrame para armazenar as informações de spend por dia
            spend_data = {'Date': [], 'Spend': []}

            # Extrair informações de spend por dia dos resultados
            for entry in stats['data']:
                spend_data['Date'].append(pd.Timestamp(entry['date_start']))
                spend_data['Spend'].append(float(entry['spend']))

            # Criar DataFrame com as informações organizadas
            df = pd.DataFrame(spend_data)

            # Exibir DataFrame
            #st.write("Informações de gastos por dia:")
            #st.dataframe(df)

        except facebook.GraphAPIError as e:
            st.error(f"Erro ao acessar estatísticas: {e}")

        
    if previous_start_date is not None and previous_end_date is not None:
        try:
            # Formatar as datas para o formato esperado pela API do Facebook
            previous_since_date = previous_start_date.strftime('%Y-%m-%d')
            previous_until_date = previous_end_date.strftime('%Y-%m-%d')
            
            # Obter as estatísticas de spend para toda a conta de anúncios no intervalo de datas especificado
            previous_insights_params = {
                'fields': 'spend',
                'level': 'account',
                'time_range': f'{{"since":"{previous_since_date}","until":"{previous_until_date}"}}',
                'access_token': access_token
            }
            previous_stats = graph.get_object(ad_account_id + '/insights', **previous_insights_params)

            # Criar um DataFrame para armazenar as informações de spend por dia
            previous_spend_data = {'Date': [], 'Spend': []}

            # Extrair informações de spend por dia dos resultados
            for entry in previous_stats['data']:
                previous_spend_data['Date'].append(pd.Timestamp(entry['date_start']))
                previous_spend_data['Spend'].append(float(entry['spend']))

            # Criar DataFrame com as informações organizadas
            previous_df = pd.DataFrame(previous_spend_data)

            # Exibir DataFrame
            #st.write("Informações de gastos por dia:")
            #st.dataframe(previous_df)

        except facebook.GraphAPIError as e:
            st.error(f"Erro ao acessar estatísticas: {e}")


        # Inserir código CSS para personalizar estilos
        st.markdown("""
        <style>
            [data-testid="stMetric"] {
                background-color: #d3d3d3;
                color: #000000;
                border: 1px solid #ffdd0b;
                padding: 12px;
                border-radius: 8px;
                margin-bottom: 8px;
                text-align: center;
            }
        </style>
        """, unsafe_allow_html=True)

        

        # Seletor de data inicial e final na Sidebar
        data_inicial = start_date
        data_final = end_date

        # Botão na Sidebar para aplicar o filtro
        #if st.sidebar.button("Aplicar Filtro"):
            # Aqui você pode colocar o código para filtrar suas tabelas com 'data_inicial' e 'data_final'
            #st.write(f"Filtrar de {data_inicial} até {data_final}")

        # Consulta SQL com filtro e relacionamentos
        query_mod_deals = f"""
                SELECT 
                    mod_deals.*,  -- Selecionar todas as colunas da tabela mod_deals
                    s.id as stage_id,
                    mod_deals_pipelines.id as pipeline_id
                FROM mod_deals
                INNER JOIN mod_deals_stages s ON s.id = mod_deals.stage_id
                INNER JOIN mod_deals_pipelines ON mod_deals_pipelines.id = s.pipeline_id
                WHERE mod_deals.pipeline_id = 13
                AND mod_deals.forecastPropability BETWEEN '{data_inicial}' AND '{data_final}';
            """
        df_mod_deals = pd.read_sql(query_mod_deals, connection)

        # Remover colunas duplicadas
        df_mod_deals = df_mod_deals.loc[:, ~df_mod_deals.columns.duplicated()]

        # Exibir o DataFrame com todas as colunas
        #st.write(df_mod_deals)

        # Consulta SQL para carregar os dados da tabela mod_field_values
        query_mod_field_values = f"""
                SELECT *
                FROM mod_field_values
                WHERE object_id IN ({', '.join(map(str, df_mod_deals['id'].tolist()))});
            """
        # Carregar os dados da tabela mod_field_values em um DataFrame
        df_mod_field_values = pd.read_sql(query_mod_field_values, connection)

        # Calcular a soma dos valores (convertendo a coluna "value" para numérica apenas na operação de soma)
        sum_values_70 = pd.to_numeric(df_mod_field_values[df_mod_field_values['field_id'] == 70]['value'], errors='coerce').sum()

        # Calcular a soma das métricas
        total_reunioes_concluidas = df_mod_field_values[(df_mod_field_values['value'] == 'Concluido') & (df_mod_field_values['field_id'] == 150)].shape[0]
        total_reunioes_agendadas = df_mod_field_values[(df_mod_field_values['value'] == 'Agendado') & (df_mod_field_values['field_id'] == 150)].shape[0]
        total_reunioes_canceladas = df_mod_field_values[(df_mod_field_values['value'] == 'Cancelado') & (df_mod_field_values['field_id'] == 150)].shape[0]
        total_reunioes_reagendadas = df_mod_field_values[(df_mod_field_values['value'] == 'Reagendado') & (df_mod_field_values['field_id'] == 150)].shape[0]

        # Soma das métricas
        total_reunioes = total_reunioes_concluidas + total_reunioes_agendadas + total_reunioes_canceladas + total_reunioes_reagendadas

        #INICIO INICIOINICIO INICIOINICIO INICIOINICIO INICIOINICIO INICIOINICIO INICIO
        # Seletor de data inicial e final na Sidebar
        previous_data_inicial = previous_start_date
        previous_data_final = previous_end_date

        # Botão na Sidebar para aplicar o filtro
        #if st.sidebar.button("Aplicar Filtro"):
            # Aqui você pode colocar o código para filtrar suas tabelas com 'data_inicial' e 'data_final'
            #st.write(f"Filtrar de {data_inicial} até {data_final}")

        # Consulta SQL com filtro e relacionamentos
        previous_query_mod_deals = f"""
                SELECT 
                    mod_deals.*,  -- Selecionar todas as colunas da tabela mod_deals
                    s.id as stage_id,
                    mod_deals_pipelines.id as pipeline_id
                FROM mod_deals
                INNER JOIN mod_deals_stages s ON s.id = mod_deals.stage_id
                INNER JOIN mod_deals_pipelines ON mod_deals_pipelines.id = s.pipeline_id
                WHERE mod_deals.pipeline_id = 13
                AND mod_deals.forecastPropability BETWEEN '{previous_data_inicial}' AND '{previous_data_final}';
            """
        previous_df_mod_deals = pd.read_sql(previous_query_mod_deals, connection)

        # Remover colunas duplicadas
        previous_df_mod_deals = previous_df_mod_deals.loc[:, ~previous_df_mod_deals.columns.duplicated()]

        # Exibir o DataFrame com todas as colunas
        #st.write(previous_df_mod_deals)

        # Consulta SQL para carregar os dados da tabela mod_field_values
        previous_query_mod_field_values = f"""
                SELECT *
                FROM mod_field_values
                WHERE object_id IN ({', '.join(map(str, previous_df_mod_deals['id'].tolist()))});
            """
        # Carregar os dados da tabela mod_field_values em um DataFrame
        previous_df_mod_field_values = pd.read_sql(previous_query_mod_field_values, connection)

        # Calcular a soma dos valores (convertendo a coluna "value" para numérica apenas na operação de soma)
        previous_sum_values_70 = pd.to_numeric(previous_df_mod_field_values[previous_df_mod_field_values['field_id'] == 70]['value'], errors='coerce').sum()

        # Calcular a soma das métricas
        previous_total_reunioes_concluidas = previous_df_mod_field_values[(previous_df_mod_field_values['value'] == 'Concluido') & (previous_df_mod_field_values['field_id'] == 150)].shape[0]
        previous_total_reunioes_agendadas = previous_df_mod_field_values[(previous_df_mod_field_values['value'] == 'Agendado') & (previous_df_mod_field_values['field_id'] == 150)].shape[0]
        previous_total_reunioes_canceladas = previous_df_mod_field_values[(previous_df_mod_field_values['value'] == 'Cancelado') & (previous_df_mod_field_values['field_id'] == 150)].shape[0]
        previous_total_reunioes_reagendadas = previous_df_mod_field_values[(previous_df_mod_field_values['value'] == 'Reagendado') & (previous_df_mod_field_values['field_id'] == 150)].shape[0]

        # Soma das métricas
        previous_total_reunioes = previous_total_reunioes_concluidas + previous_total_reunioes_agendadas + previous_total_reunioes_canceladas + previous_total_reunioes_reagendadas

        #FIM FIM FIM FIM FIM

        # Exibir os dados carregados
        #st.write("Dados da tabela mod_field_values:")
        #st.write(df_mod_field_values)

        col1B,col2B,col3B,col4B,col5B = st.columns(5)

        # Calcular as métricas conforme as suas necessidades
        #st.metric("Quantidade de Totens", sum_values_70)
        #col2B.metric("Reuniões concluídas", df_mod_field_values[(df_mod_field_values['value'] == 'Concluido') & (df_mod_field_values['field_id'] == 150)].shape[0])
        #col3B.metric("Reuniões agendadas", df_mod_field_values[(df_mod_field_values['value'] == 'Agendado') & (df_mod_field_values['field_id'] == 150)].shape[0])
        #col4B.metric("Reuniões canceladas", df_mod_field_values[(df_mod_field_values['value'] == 'Cancelado') & (df_mod_field_values['field_id'] == 150)].shape[0])
        #col5B.metric("Reuniões reagendadas", df_mod_field_values[(df_mod_field_values['value'] == 'Reagendado') & (df_mod_field_values['field_id'] == 150)].shape[0])
        #col6B.metric("Total de negócios aptos à reunião", df_mod_field_values[df_mod_field_values['field_id'] == 150].shape[0])


        # Filtrar o DataFrame mod_deals para cada estágio específico
        lead_sem_atendimento = df_mod_deals[df_mod_deals['stage_id'] == 88].shape[0]
        suspect_em_abordagem = df_mod_deals[df_mod_deals['stage_id'] == 89].shape[0]
        proposta = df_mod_deals[df_mod_deals['stage_id'] == 91].shape[0]
        negociacao = df_mod_deals[df_mod_deals['stage_id'] == 92].shape[0]
        aceite = df_mod_deals[df_mod_deals['stage_id'] == 93].shape[0]
        ganha = df_mod_deals[df_mod_deals['stage_id'] == 94].shape[0]
        perdida = df_mod_deals[df_mod_deals['stage_id'] == 95].shape[0]
        oportunidade_stand_by = df_mod_deals[df_mod_deals['stage_id'] == 179].shape[0]

        leads_totais_do_periodo = lead_sem_atendimento + suspect_em_abordagem + proposta + negociacao + aceite + ganha + perdida + oportunidade_stand_by
        
        total_spend = df['Spend']


        # Filtrar o DataFrame mod_deals para cada estágio específico
        previous_lead_sem_atendimento = previous_df_mod_deals[previous_df_mod_deals['stage_id'] == 88].shape[0]
        previous_suspect_em_abordagem = previous_df_mod_deals[previous_df_mod_deals['stage_id'] == 89].shape[0]
        previous_proposta = previous_df_mod_deals[previous_df_mod_deals['stage_id'] == 91].shape[0]
        previous_negociacao = previous_df_mod_deals[previous_df_mod_deals['stage_id'] == 92].shape[0]
        previous_aceite = previous_df_mod_deals[previous_df_mod_deals['stage_id'] == 93].shape[0]
        previous_ganha = previous_df_mod_deals[previous_df_mod_deals['stage_id'] == 94].shape[0]
        previous_perdida = previous_df_mod_deals[previous_df_mod_deals['stage_id'] == 95].shape[0]
        previous_oportunidade_stand_by = previous_df_mod_deals[previous_df_mod_deals['stage_id'] == 179].shape[0]

        previous_leads_totais_do_periodo = previous_lead_sem_atendimento + previous_suspect_em_abordagem + previous_proposta + previous_negociacao + previous_aceite + previous_ganha + previous_perdida + previous_oportunidade_stand_by
        
        previous_total_spend = previous_df['Spend']
        

        #CALCULO DOS DELTAS COLUNA 2
        delta_leads = 100*((leads_totais_do_periodo / previous_leads_totais_do_periodo)-1)
        delta_total_reunioes = 100*((total_reunioes / previous_total_reunioes)-1)
        delta_total_reunioes_concluidas = 100*((total_reunioes_concluidas / previous_total_reunioes_concluidas)-1)
        delta_ganha = 100*((ganha / previous_ganha)-1)
        delta_sum_values_70 = 100*((sum_values_70 / previous_sum_values_70)-1)

        




        #calcular métricas para layout (dividido por spend)
        if leads_totais_do_periodo > 0:
            metrica_resultante = total_spend / leads_totais_do_periodo
        else:
            metrica_resultante = 0

        #Reuniões agendadas dividido por spend
        if total_reunioes >0:
            spend_total_reunioes = total_spend /total_reunioes
        else:
            spend_total_reunioes = 0

        #Reunioes realizadas dividido por spend
        if total_reunioes_concluidas >0:
            spend_total_reunioes_concluidas = total_spend / total_reunioes_concluidas
        else:
            spend_total_reunioes_concluidas = 0

        #Vendas dividido por spend
        if ganha >0:
            spend_ganha = total_spend / ganha
        else:
            spend_ganha = 0

        #Totem vendidos por spend
        if sum_values_70 >0:
            totem_por_spend = total_spend / sum_values_70
        else:
            totem_por_spend = 0

        #calcular métricas para layout (dividido por spend)
        if previous_leads_totais_do_periodo > 0:
            previous_metrica_resultante = previous_total_spend / previous_leads_totais_do_periodo
        else:
            previous_metrica_resultante = 0

        #Reuniões agendadas dividido por spend
        if previous_total_reunioes >0:
            previous_spend_total_reunioes = previous_total_spend /previous_total_reunioes
        else:
            previous_spend_total_reunioes = 0

        #Reunioes realizadas dividido por spend
        if previous_total_reunioes_concluidas >0:
            previous_spend_total_reunioes_concluidas = previous_total_spend / previous_total_reunioes_concluidas
        else:
            previous_spend_total_reunioes_concluidas = 0

        #Vendas dividido por spend
        if previous_ganha >0:
            previous_spend_ganha = previous_total_spend / previous_ganha
        else:
            previous_spend_ganha = 0

        #Totem vendidos por spend
        if previous_sum_values_70 >0:
            previous_totem_por_spend = previous_total_spend / previous_sum_values_70
        else:
            previous_totem_por_spend = 0

        #CALCULO DOS DELTAS COLUNA 1
        delta_metrica_resultante = 100*((metrica_resultante / previous_metrica_resultante)-1)
        delta_spend_total_reunioes = 100*((spend_total_reunioes / previous_spend_total_reunioes)-1)
        delta_spend_total_reunioes_concluidas = 100*((spend_total_reunioes_concluidas / previous_spend_total_reunioes_concluidas)-1)
        delta_spend_ganha = 100*((spend_ganha / previous_spend_ganha)-1)
        delta_totem_por_spend = 100*((totem_por_spend / previous_totem_por_spend)-1)

        #criar colunas para disposição das métricas de negócios
        col1A, col2A, col3A, col4A, col5A = st.columns(5)

        #COLUNA 1
        col1A.metric('CPL', f'R${metrica_resultante.iloc[0]:.2f}', delta=f'{delta_metrica_resultante.iloc[0]:.2f}%')
        col2A.metric('Custo por reunião agendada', f'R${spend_total_reunioes.iloc[0]:.2f}',delta=f'{delta_spend_total_reunioes.iloc[0]:.2f}%')
        col3A.metric('Custo por reunião realizada', f'R${spend_total_reunioes_concluidas.iloc[0]:.2f}',delta=f'{delta_spend_total_reunioes_concluidas.iloc[0]:.2f}%')
        col4A.metric('Custo por venda', f'R${spend_ganha.iloc[0]:.2f}',delta=f'{delta_spend_ganha.iloc[0]:.2f}%')
        col5A.metric('Custo por Totem vendido', f'R${totem_por_spend.iloc[0]:.2f}', delta=f'{delta_totem_por_spend.iloc[0]:.2f}%')


        #COLUNA 2
        col1B.metric('Leads', leads_totais_do_periodo, delta=f'{delta_leads:.2f}%')
        col2B.metric("Reuniões agendadas", total_reunioes, delta=f'{delta_total_reunioes:.2f}%')
        col3B.metric('Reuniões realizadas', total_reunioes_concluidas, delta=f'{delta_total_reunioes_concluidas:.2f}%')
        col4B.metric('Vendas', ganha, delta=f'{delta_ganha:.2f}%')
        col5B.metric('Totens vendidos', sum_values_70, delta=f'{delta_sum_values_70:.2f}%')
        

        # Mostrar as métricas lado a lado
        #st.metric("LEAD (sem atendimento)", lead_sem_atendimento)
        #col2A.metric("SUSPECT (em abordagem)", suspect_em_abordagem)
        #col3A.metric("Proposta", proposta)
        #col4A.metric("Negociação", negociacao)
        #col5A.metric("Aceite", aceite)
        #col6A.metric("Ganha", ganha)
        #col7A.metric("Perdida", perdida)
        #col8A.metric("Oportunidade (Stand by)", oportunidade_stand_by)

        delta_total_spend = 100*((total_spend / previous_total_spend)-1)

        #COLUNA 3
        col1C, col2C, col3C = st.columns(3)
        col2C.metric("Investimento", f'R${total_spend.iloc[0]:.2f}',delta=f'{delta_total_spend.iloc[0]:.2f}%')
        

        #st.sidebar.write("Selecione o período para o gráfico'))
        totem_data_inicial=st.sidebar.date_input('Data de início gráfico', None)
        totem_data_final=st.sidebar.date_input('Data final do gráfico')

        # Consulta SQL com filtro e relacionamentos
        totem_query_mod_deals = f"""
                SELECT 
                    mod_deals.*,  -- Selecionar todas as colunas da tabela mod_deals
                    s.id as stage_id,
                    mod_deals_pipelines.id as pipeline_id
                FROM mod_deals
                INNER JOIN mod_deals_stages s ON s.id = mod_deals.stage_id
                INNER JOIN mod_deals_pipelines ON mod_deals_pipelines.id = s.pipeline_id
                WHERE mod_deals.pipeline_id = 13
                AND mod_deals.forecastPropability BETWEEN '{totem_data_inicial}' AND '{totem_data_final}';
            """
        totem_df_mod_deals = pd.read_sql(totem_query_mod_deals, connection)

        # Remover colunas duplicadas
        totem_df_mod_deals = totem_df_mod_deals.loc[:, ~totem_df_mod_deals.columns.duplicated()]

        # Consulta SQL para carregar a coluna forecastPropability da tabela mod_deals
        totem_query_mod_deals = f"""
            SELECT id, forecastPropability
            FROM mod_deals
            WHERE id IN ({', '.join(map(str, totem_df_mod_deals['id'].tolist()))});
        """

        # Carregar dados da coluna forecastPropability
        totem_df_mod_deals_forecast = pd.read_sql(totem_query_mod_deals, connection)


        # Consulta SQL para carregar os dados da tabela mod_field_values
        totem_query_mod_field_values = f"""
                SELECT *
                FROM mod_field_values
                WHERE object_id IN ({', '.join(map(str, totem_df_mod_deals['id'].tolist()))});
            """
        # Carregar os dados da tabela mod_field_values em um DataFrame
        totem_df_mod_field_values = pd.read_sql(totem_query_mod_field_values, connection)

        # Unir os DataFrames usando a coluna 'object_id'
        totem_df_merged = pd.merge(totem_df_mod_field_values, totem_df_mod_deals_forecast, left_on='object_id', right_on='id', how='left')

        # Exibir o DataFrame resultante
        #st.dataframe(df_merged)

    # Criar colunas de mês e ano usando a coluna 'forecastPropability'
        totem_df_merged['month'] = totem_df_merged['forecastPropability'].dt.month
        totem_df_merged['year'] = totem_df_merged['forecastPropability'].dt.year

        #st.dataframe(df_merged)

        # Seletor de métricas
        metric_options = ["Quantidade de Totens"]   
        # Criar selectbox para escolher a métrica
        selected_metric = metric_options[0]

    

        # Lógica para cada métrica
        if selected_metric == "Quantidade de Totens":
            totem_df_merged[selected_metric] = pd.to_numeric(totem_df_merged[totem_df_merged['field_id'] == 70]['value'], errors='coerce')
    

        # Calcular a soma da métrica por mês e ano
        df_grouped = totem_df_merged.groupby(['year', 'month']).agg({selected_metric: 'sum'}).reset_index()

        # Adicionar coluna 'month_name' durante o agrupamento
        df_grouped = totem_df_merged.groupby(['year', 'month']).agg({selected_metric: 'sum'}).reset_index()
        df_grouped['month_name'] = df_grouped['month'].apply(lambda x: calendar.month_name[int(x)] if x is not None else None)
        
        #st.write(df_merged)
        col2D,col1D = st.columns([2,1])
        col1D.write(df_grouped)

    
        #Criar gráfico de linhas
        fig = px.line(df_grouped, x='month_name', y=selected_metric, color='year', color_discrete_sequence=['yellow','white'], title=f'{selected_metric} por Mês e Ano',hover_data=selected_metric,markers=True,text=f'{selected_metric}')

        

        # Exiba o gráfico
        col2D.plotly_chart(fig)
