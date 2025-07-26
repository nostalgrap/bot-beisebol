# ==============================================================================
# BOT PELÉ COLAB v2.0 - VERSÃO WEB COM STREAMLIT
# ==============================================================================
import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import time
import random

# --- CONFIGURAÇÃO DA PÁGINA E DO TÍTULO ---
st.set_page_config(page_title="Bot Pelé Colab", page_icon="⚾", layout="wide")
st.title('⚾ Bot Pelé Colab v2.0 - O Estrategista')
st.write('Seu assistente pessoal para análise de jogos de beisebol.')

# --- O NOVO JEITO DE PEGAR A API KEY (SEGURA E SEM EDITAR O CÓDIGO) ---
# Ele vai buscar as chaves no "Cofre de Segredos" do Streamlit.
# Explicarei como configurar o cofre na Fase 3.
try:
    API_KEY = st.secrets["API_KEY"]
    BASE_URL = st.secrets["BASE_URL"]
except:
    st.error("ERRO: As chaves da API não foram encontradas. Por favor, configure os 'Secrets' nas configurações do aplicativo no Streamlit Cloud.")
    st.stop()

# --- FUNÇÕES DO BOT (Exatamente como as que já testamos) ---

@st.cache_data(ttl=3600) # Guarda os resultados por 1 hora para não fazer buscas repetidas.
def buscar_jogos_do_dia():
    data_de_hoje = datetime.now().strftime('%Y-%m-%d')
    endpoint_completo = f"{BASE_URL}/games"
    parametros = {'date': data_de_hoje}
    cracha = {'x-apisports-key': API_KEY}
    response = requests.get(endpoint_completo, params=parametros, headers=cracha)
    response.raise_for_status()
    dados_json = response.json()
    return pd.DataFrame(dados_json['response'])

def buscar_estatisticas_detalhadas_simulado(nome_time):
    stats_simuladas = {
        'pitcher_era': round(random.uniform(2.8, 5.5), 2),
        'pitcher_whip': round(random.uniform(1.1, 1.6), 2),
        'runs_per_game': round(random.uniform(3.5, 5.8), 1)
    }
    return stats_simuladas

def gerar_palpites_e_analise(jogo):
    time_casa_info = jogo['teams']['home']
    time_fora_info = jogo['teams']['away']
    nome_casa = time_casa_info['name']
    nome_fora = time_fora_info['name']

    stats_casa = buscar_estatisticas_detalhadas_simulado(nome_casa)
    stats_fora = buscar_estatisticas_detalhadas_simulado(nome_fora)

    pontos_casa, pontos_fora = 0, 0
    if stats_casa['pitcher_era'] < stats_fora['pitcher_era']: pontos_casa += 3
    else: pontos_fora += 3
    if stats_casa['pitcher_whip'] < stats_fora['pitcher_whip']: pontos_casa += 2
    else: pontos_fora += 2
    if stats_casa['runs_per_game'] > stats_fora['runs_per_game']: pontos_casa += 2
    else: pontos_fora += 2
    pontos_casa += 1

    diferenca_pontos = abs(pontos_casa - pontos_fora)
    palpites = {}
    time_favorito = nome_casa if pontos_casa > pontos_fora else nome_fora

    palpites['moneyline'] = f"Vencedor: {time_favorito}"
    if diferenca_pontos >= 5: palpites['run_line'] = f"{time_favorito} -1.5 (Vencer por 2+ corridas)"

    media_corridas_total = stats_casa['runs_per_game'] + stats_fora['runs_per_game']
    if media_corridas_total > 9.0: palpites['total'] = "Over 8.5 Corridas"
    elif stats_casa['pitcher_era'] < 3.2 and stats_fora['pitcher_era'] < 3.2: palpites['total'] = "Under 8.5 Corridas"

    return {'confianca': diferenca_pontos, 'sugestoes': palpites, 'jogo': f"{nome_fora} @ {nome_casa}"}

# --- EXECUÇÃO PRINCIPAL DO SITE ---
if st.button('Fazer Análise dos Jogos de Hoje!'):
    with st.spinner('Buscando jogos e consultando o estrategista... Por favor, aguarde.'):
        try:
            jogos_de_hoje = buscar_jogos_do_dia()
            resultados_finais = []
            for indice, jogo_da_linha in jogos_de_hoje.iterrows():
                if jogo_da_linha['status']['short'] == 'NS':
                    resultado_analise = gerar_palpites_e_analise(jogo_da_linha)
                    resultados_finais.append(resultado_analise)

            if not resultados_finais:
                st.warning("Nenhum jogo encontrado para hoje que ainda não tenha começado.")
            else:
                resultados_finais.sort(key=lambda item: item['confianca'], reverse=True)

                st.header('🎯 Estratégias e Palpites do Dia')
                for resultado in resultados_finais:
                    with st.expander(f"**{resultado['jogo']}** (Confiança da Análise: {resultado['confianca']} pts)"):
                        for tipo_aposta, palpite in resultado['sugestoes'].items():
                            st.markdown(f"**{tipo_aposta.replace('_', ' ').title()}:** {palpite}")

                st.header('🚀 Sugestão de Múltipla (Aposta de Alto Risco!)')
                multipla = []
                for resultado in resultados_finais:
                    if 'moneyline' in resultado['sugestoes'] and len(multipla) < 3:
                         multipla.append(resultado['sugestoes']['moneyline'])

                if len(multipla) < 2:
                    st.info("Não há jogos com confiança suficiente para montar uma múltipla hoje.")
                else:
                    for i, aposta in enumerate(multipla):
                        st.success(f"**Seleção {i+1}:** {aposta}")
                    st.warning("Lembre-se: Na múltipla, você precisa acertar TODOS os resultados para ganhar.")
        except Exception as e:
            st.error(f"Ocorreu um erro na comunicação com a API. Verifique se suas chaves estão corretas nos 'Secrets'. Erro: {e}")
else:
    st.info("Clique no botão azul acima para iniciar a análise do dia.")

st.markdown("---")
st.markdown("*Aviso de Responsabilidade: As sugestões são baseadas em um modelo estatístico simulado e não garantem resultados. Aposte com responsabilidade.*")
