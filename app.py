import streamlit as st
import pandas as pd
from nba_api.live.nba.endpoints import scoreboard

# Configuración inicial de la página optimizada para móvil
st.set_page_config(page_title="NBA Schedule App", layout="centered")

st.title("🏀 Calendario NBA de Hoy")

# --- FUNCIÓN PARA OBTENER LOS PARTIDOS DEL DÍA ---
@st.cache_data(ttl=300) # Caché de 5 minutos para evitar peticiones innecesarias
def get_todays_schedule():
    try:
        # Obtenemos el marcador en vivo / calendario de la fecha actual
        board = scoreboard.ScoreBoard()
        data = board.get_dict()
        
        games_raw = data.get('scoreboard', {}).get('games', [])
        
        schedule_list = []
        for game in games_raw:
            # Extraemos nombres y ciudades de los equipos
            home_team = f"{game['homeTeam']['teamCity']} {game['homeTeam']['teamName']}"
            away_team = f"{game['awayTeam']['teamCity']} {game['awayTeam']['teamName']}"
            
            # Estado del juego (ej. Hora de inicio, En vivo, Finalizado)
            status_text = game.get('gameStatusText', '')
            
            schedule_list.append({
                "Local": home_team,
                "Visitante": away_team,
                "Estado": status_text
            })
            
        return schedule_list
    except Exception as e:
        st.error(f"Error al conectar con la API de la NBA: {e}")
        return []

# --- BOTÓN DE ACTUALIZACIÓN MANUAL ---
if st.button('🔄 Actualizar Calendario'):
    st.cache_data.clear()

# --- CARGA Y RENDERIZADO DE DATOS ---
games = get_todays_schedule()

if games:
    st.subheader(f"Partidos programados ({len(games)})")
    
    # Mostramos los juegos en formato de tarjetas limpias
    for game in games:
        with st.container():
            st.markdown(f"**{game['Visitante']}** @ **{game['Local']}**")
            st.caption(f"🕒 {game['Estado']}")
            st.divider()
else:
    st.info("No hay partidos programados para hoy o la jornada aún no está disponible.")
