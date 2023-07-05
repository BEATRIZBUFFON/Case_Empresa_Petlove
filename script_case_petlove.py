#Importando bibliotecas:
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('data-test-analytics.csv')
df.info()
df.head()

#Tratamento dos dados:
df['created_at'] = pd.to_datetime(df['created_at'])
df['deleted_at'] = pd.to_datetime(df['deleted_at'])
df['marketing_source'].replace({
    'crm': 'CRM', 
    'organic_search': 'Pesquisa Orgânica', 
    'direct': 'Fonte de tráfego externa', 
    'paid_search': 'Pesquisa paga', 
    'none': 'Sem infos',
    'telegram_whatsapp': 'Telegram/WhatsApp'
}, inplace=True)
df['status'].replace({
    'active': 'Ativado',
    'paused':'Pausado',
    'canceled':'Cancelado'
},inplace=True)

#Duraçao das assinaturas durante um de terminado período de tempo:
df_cancelamento = df[df['deleted_at'].notnull()]
df_cancelamento['duration'] = (df_cancelamento['deleted_at'] - df_cancelamento['created_at']).dt.days
bins = [0, 30, 90, 180, 365, 547, 730, 1095, 1460, df_cancelamento['duration'].max()]
labels = ['Até 1 mês', '1 - 3 meses', '3 - 6 meses', '6 meses - 1 ano', '1-1.5 anos', '1.5-2 anos', '2-3 anos', '3-4 anos', '4-5 anos']
df_cancelamento['duration_interval'] = pd.cut(df_cancelamento['duration'], bins=bins, labels=labels)
counts = df_cancelamento['duration_interval'].value_counts().sort_index()
counts = counts.reset_index()

#Taxa de cancelamento por estado
cancelamentos_por_estado = df[df['status'] == 'canceled'].groupby('state')['status'].value_counts()
total_assinaturas_por_estado = df.groupby('state')['status'].count()
taxa_cancelamento_por_estado = (cancelamentos_por_estado / total_assinaturas_por_estado) * 100
taxa_cancelamento_por_estado = taxa_cancelamento_por_estado.reset_index()

#Status por estado
status_by_state = df.groupby(['state', 'status'])['id'].count()
status_by_state = status_by_state.unstack()
status_by_state = status_by_state.reset_index()

#Contagem de ativos, cancelados e pausados
status_counts = df['status'].value_counts()
status_counts = status_counts.reset_index()

#Gráfico de correlação entre: canal de marketing que convertou a assinatura e tempo desde a última compra
df_teste = df[['status', 'marketing_source']]
df_teste2 = df[['status', 'recency']]
df_teste = df_teste.reset_index()
df_teste2 = df_teste2.reset_index()

#Ocorrência de cancelamentos e o canal de conversão de marketing
df_canceled = df[df['status'] == 'Cancelado']
freq = df_canceled['marketing_source'].value_counts()
freq = freq.reset_index()

#Análise do tempo méio de cancelamento
df['created_at'] = pd.to_datetime(df['created_at'])
df['deleted_at'] = pd.to_datetime(df['deleted_at'])
df['tempo_ate_cancelamento'] = df['deleted_at'] - df['created_at']
media_tempo_ate_cancelamento = df.loc[df['status'] == 'Cancelado', 'tempo_ate_cancelamento'].mean()
print(f"A média de tempo que os clientes permanecem como assinantes antes de cancelar é de {media_tempo_ate_cancelamento}")

#Identificar periodo especifico apos criação da assinatura em que as taxas são mais elavada
#e tomar medidas para reter clientes nesse periodo
df['data_cancelamento'] = df['deleted_at'].dt.date
cancelamentos_por_dia = df.groupby('data_cancelamento').size()

#Análise do ticket médio de clientes que cancelaram
clientes_cancelados = df[df['status'] == 'Cancelado']
ticket_medio_cancelados = clientes_cancelados['average_ticket'].mean()
clientes_ativos = df[df['status'] != 'Cancelado']
ticket_medio_ativos = clientes_ativos['average_ticket'].mean()
print(f'Ticket médio dos clientes que cancelaram: R${ticket_medio_cancelados:.2f}')
print(f'Ticket médio dos clientes ativos: R${ticket_medio_ativos:.2f}')

#Frequência média de compra de todos os clientes = 0,12
df['active_months'] = (pd.to_datetime(df['deleted_at'].fillna(pd.Timestamp.now())) - pd.to_datetime(df['created_at'])) / pd.Timedelta(days=30)
df['purchase_frequency'] = df['all_orders'] / df['active_months']
df['purchase_frequency'].mean().round(2)

#Comportamento dos clientes antes do cancelamento:
# Média de gasto por pedido nos últimos 6 meses = 1174.8
df['last_6m_avg_ticket'] = df['all_revenue'].rolling(window=6).mean()

#Frequência de compra nos últimos 6 meses = 32.49
df['last_6m_orders']= df['all_orders'].rolling(window=6).sum()
