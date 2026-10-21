import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="NBA Schedule App", layout="centered")

st.title("🏀 Calendario NBA de Hoy")

# --- FUNCIÓN CON HEADERS PERSONALIZADOS PARA EVITAR BLOQUEOS ---
@st.cache_data(ttl=300)
def get_todays_schedule():
    url = "https://stats.nba.com/stats/scoreboardv3"
    
    # Headers obligatorios para que la API de la NBA no rechace la conexión desde la nube
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://www.nba.com/',
        'Origin': 'https://www.nba.com',
        'Connection': 'keep-alive'
    }
    
    try:
        # Hacemos la petición directa con requests para controlar los headers
        response = requests.get(url, headers=headers, timeout=10)
        
        # Verificamos si la petición fue exitosa
        if response.status_code != 200:
            return f"Error HTTP {response.status_code}: La NBA bloqueó la solicitud."
            
        data = response.json()
        
        # Extraemos los juegos del scoreboardv3
        games_raw = data.get('scoreboard', {}).get('games', [])
        
        schedule_list = []
        for game in games_raw:
            home_team = f"{game['homeTeam']['teamCity']} {game['homeTeam']['teamName']}"
            away_team = f"{game['awayTeam']['teamCity']} {game['awayTeam']['teamName']}"
            
            # Estado del juego
            status_text = game.get('gameStatusText', '')
            
            schedule_list.append({
                "Local": home_team,
                "Visitante": away_team,
                "Estado": status_text
            })
            
        return schedule_list
        
    except Exception as e:
        return f"Error al procesar los datos: {str(e)}"

# --- BOTÓN DE ACTUALIZACIÓN MANUAL ---
if st.button('🔄 Actualizar Calendario'):
    st.cache_data.clear()

# --- CARGA Y RENDERIZADO DE DATOS ---
result = get_todays_schedule()

if isinstance(result, str):
    st.error(result)
else:
    games = result
    st.subheader(f"Partidos programados ({len(games)})")
    
    if games:
        for game in games:
            with st.container():
                st.markdown(f"**{game['Visitante']}** @ **{game['Local']}**")
                st.caption(f"🕒 {game['Estado']}")
                st.divider()
    else:
        st.info("No hay partidos programados para hoy en la NBA.")
