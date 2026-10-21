import streamlit as st
import requests
from datetime import datetime

st.set_page_config(page_title="NBA Schedule App", layout="centered")

st.title("🏀 Calendario NBA")

# --- SELECTOR DE FECHA ---
selected_date = st.date_input("Selecciona la fecha del juego", datetime.now())
date_str = selected_date.strftime("%Y%m%d")

# --- FUNCIÓN PARA OBTENER EL CALENDARIO CON LOGOS ---
@st.cache_data(ttl=300)
def get_schedule(date_formatted):
    url = f"https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard?dates={date_formatted}"
    
    try:
        response = requests.get(url, timeout=10)
        
        if response.status_code != 200:
            return f"Error HTTP {response.status_code}: No se pudo conectar con ESPN."
            
        data = response.json()
        events = data.get('events', [])
        
        schedule_list = []
        for event in events:
            competition = event['competitions'][0]
            competitors = competition['competitors']
            
            home_team = ""
            home_logo = ""
            away_team = ""
            away_logo = ""
            
            for comp in competitors:
                team_name = comp['team']['displayName']
                # Obtenemos el logo del equipo (si existe)
                logo_url = comp['team'].get('logo', 'https://a.espncdn.com/i/teamlogos/default-team-logo.png')
                
                if comp['homeAway'] == 'home':
                    home_team = team_name
                    home_logo = logo_url
                else:
                    away_team = team_name
                    away_logo = logo_url
            
            status_text = competition['status']['type']['detail']
            
            schedule_list.append({
                "Local": home_team,
                "LocalLogo": home_logo,
                "Visitante": away_team,
                "VisitanteLogo": away_logo,
                "Estado": status_text
            })
            
        return schedule_list
        
    except Exception as e:
        return f"Error al procesar los datos: {str(e)}"

# --- BOTÓN DE ACTUALIZACIÓN MANUAL ---
if st.button('🔄 Actualizar Calendario'):
    st.cache_data.clear()

# --- CARGA Y RENDERIZADO DE DATOS ---
result = get_schedule(date_str)

if isinstance(result, str):
    st.error(result)
else:
    games = result
    st.subheader(f"Partidos del {selected_date.strftime('%d/%m/%Y')} ({len(games)})")
    
    if games:
        for game in games:
            with st.container():
                # Creamos 5 columnas para alinear los logos y nombres: 
                # [Logo Vis, Nombre Vis, @/VS, Nombre Loc, Logo Loc]
                col1, col2, col3, col4, col5 = st.columns([1, 2.5, 1, 2.5, 1])
                
                with col1:
                    st.image(game['VisitanteLogo'], width=45)
                with col2:
                    st.markdown(f"**{game['Visitante']}**")
                with col3:
                    st.markdown("<h4 style='text-align: center; margin: 0;'>@</h4>", unsafe_allow_html=True)
                with col4:
                    st.markdown(f"**{game['Local']}**")
                with col5:
                    st.image(game['LocalLogo'], width=45)
                    
                st.caption(f"🕒 {game['Estado']}")
                st.divider()
    else:
        st.info("No hay partidos programados para esta fecha en la NBA.")
