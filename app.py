import streamlit as st
import requests

st.set_page_config(page_title="NBA Schedule App", layout="centered")

st.title("🏀 Calendario NBA de Hoy")

# --- FUNCIÓN PARA OBTENER EL CALENDARIO DESDE LA API DE ESPN ---
@st.cache_data(ttl=300)
def get_todays_schedule():
    # Endpoint público de la NBA en ESPN (trae los partidos del día actual automáticamente)
    url = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard"
    
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
            
            # Identificar local y visitante
            home_team = ""
            away_team = ""
            for comp in competitors:
                team_name = comp['team']['displayName']
                if comp['homeAway'] == 'home':
                    home_team = team_name
                else:
                    away_team = team_name
            
            # Estado del partido (ej. Horario, En vivo, Finalizado)
            status_text = competition['status']['type']['detail']
            
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
