import streamlit as st
import requests
from datetime import datetime

st.set_page_config(page_title="NBA Schedule & Projections", layout="centered")

st.title("🏀 NBA Schedule & Projections")

# --- SELECTOR DE FECHA ---
selected_date = st.date_input("Selecciona la fecha del juego", datetime.now())
date_str = selected_date.strftime("%Y%m%d")

# --- DICCIONARIO BASE DE DATOS DE EQUIPOS (Pace, ORTG, DRTG) ---
TEAMS_DATA = {
    "Boston Celtics": {"Pace": 98.5, "ORTG": 118.0, "DRTG": 110.0},
    "Denver Nuggets": {"Pace": 97.2, "ORTG": 116.5, "DRTG": 112.1},
    "Los Angeles Lakers": {"Pace": 101.0, "ORTG": 114.2, "DRTG": 113.8},
    "Golden State Warriors": {"Pace": 100.5, "ORTG": 115.0, "DRTG": 111.5},
    "Miami Heat": {"Pace": 96.0, "ORTG": 112.0, "DRTG": 109.5},
    "Dallas Mavericks": {"Pace": 99.1, "ORTG": 117.1, "DRTG": 114.0},
    "Milwaukee Bucks": {"Pace": 100.2, "ORTG": 116.8, "DRTG": 113.2},
    "Philadelphia 76ers": {"Pace": 97.8, "ORTG": 115.5, "DRTG": 111.8},
    "Phoenix Suns": {"Pace": 98.2, "ORTG": 116.0, "DRTG": 113.0},
    "Minnesota Timberwolves": {"Pace": 97.5, "ORTG": 114.5, "DRTG": 108.5},
    "Oklahoma City Thunder": {"Pace": 99.8, "ORTG": 116.2, "DRTG": 111.0},
    "New York Knicks": {"Pace": 95.8, "ORTG": 117.5, "DRTG": 112.3},
}

DEFAULT_STATS = {"Pace": 99.0, "ORTG": 114.5, "DRTG": 114.5}
LEAGUE_PACE = 99.0
LEAGUE_PTS_100 = 114.5

# --- FUNCIÓN DE CÁLCULO DE PROYECCIÓN ---
def calculate_projection(away_team, home_team):
    away_stats = TEAMS_DATA.get(away_team, DEFAULT_STATS)
    home_stats = TEAMS_DATA.get(home_team, DEFAULT_STATS)

    # 1. Game Pace Proyectado
    game_pace = (away_stats["Pace"] * home_stats["Pace"]) / LEAGUE_PACE

    # 2. Eficiencias Ajustadas
    away_adj_ortg = away_stats["ORTG"] * (home_stats["DRTG"] / LEAGUE_PTS_100)
    home_adj_ortg = home_stats["ORTG"] * (away_stats["DRTG"] / LEAGUE_PTS_100)

    # 3. Puntos Proyectados (+2.5 para localía)
    away_pts = (away_adj_ortg / 100) * game_pace
    home_pts = ((home_adj_ortg / 100) * game_pace) + 2.5
    total_pts = away_pts + home_pts
    
    # 4. Spread Proyectado (Positivo = Local favorito, Negativo = Visitante favorito)
    spread = home_pts - away_pts

    return round(away_pts, 1), round(home_pts, 1), round(total_pts, 1), round(game_pace, 1), round(spread, 1)

# --- FUNCIÓN PARA OBTENER EL CALENDARIO ---
@st.cache_data(ttl=300)
def get_schedule(date_formatted):
    url = f"https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard?dates={date_formatted}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            return f"Error HTTP {response.status_code}"
            
        data = response.json()
        events = data.get('events', [])
        
        schedule_list = []
        for event in events:
            competition = event['competitions'][0]
            competitors = competition['competitors']
            
            home_team, home_logo, away_team, away_logo = "", "", "", ""
            for comp in competitors:
                team_name = comp['team']['displayName']
                logo_url = comp['team'].get('logo', 'https://a.espncdn.com/i/teamlogos/default-team-logo.png')
                
                if comp['homeAway'] == 'home':
                    home_team, home_logo = team_name, logo_url
                else:
                    away_team, away_logo = team_name, logo_url
            
            status_text = competition['status']['type']['detail']
            
            away_pts, home_pts, total_pts, game_pace, spread = calculate_projection(away_team, home_team)
            
            schedule_list.append({
                "Local": home_team,
                "LocalLogo": home_logo,
                "Visitante": away_team,
                "VisitanteLogo": away_logo,
                "Estado": status_text,
                "ProjAway": away_pts,
                "ProjHome": home_pts,
                "ProjTotal": total_pts,
                "ProjPace": game_pace,
                "ProjSpread": spread
            })
            
        return schedule_list
    except Exception as e:
        return f"Error: {str(e)}"

# --- BOTÓN DE ACTUALIZACIÓN MANUAL ---
if st.button('🔄 Actualizar Datos'):
    st.cache_data.clear()

# --- RENDERIZADO DE PARTIDOS ---
result = get_schedule(date_str)

if isinstance(result, str):
    st.error(result)
else:
    games = result
    st.subheader(f"Partidos del {selected_date.strftime('%d/%m/%Y')} ({len(games)})")
    
    if games:
        for index, game in enumerate(games):
            with st.container():
                # Encabezado con logos y nombres
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
                
                st.caption(f"🕒 Estado: {game['Estado']}")
                
                # Métricas de Puntos (Visitante, Local, Total)
                m1, m2, m3 = st.columns(3)
                m1.metric(label=f"Proy. {game['Visitante'].split()[-1]}", value=game['ProjAway'])
                m2.metric(label=f"Proy. {game['Local'].split()[-1]}", value=game['ProjHome'])
                m3.metric(label="Total Proyectado", value=game['ProjTotal'])
                
                # Texto del Spread del Modelo
                if game['ProjSpread'] > 0:
                    favorite_text = f"Favorito **{game['Local']}** por **{game['ProjSpread']}** pts"
                elif game['ProjSpread'] < 0:
                    favorite_text = f"Favorito **{game['Visitante']}** por **{abs(game['ProjSpread'])}** pts"
                else:
                    favorite_text = "Partido Empatado"

                st.caption(f"⚡ **Ritmo:** {game['ProjPace']} pos | 🎯 **Modelo:** {favorite_text}")
                
                # --- MODO COMPARATIVO DE VALOR (EXPANDER) ---
                with st.expander("🧮 Analizar Valor de Apuesta vs Casino"):
                    st.markdown(f"Introduce la línea actual del casino para el **equipo Local ({game['Local']})**:")
                    # Input con un key único por cada partido para evitar conflictos en Streamlit
                    casino_spread = st.number_input(
                        f"Spread Casino ({game['Local']})", 
                        value=float(game['ProjSpread']), 
                        step=0.5, 
                        key=f"casino_spread_{index}"
                    )
                    
                    # Comparativa de valor
                    # Si el modelo dice que gana por X y el casino pide Y
                    diff = game['ProjSpread'] - casino_spread
                    
                    st.markdown("---")
                    st.markdown("💡 **Resultado del Análisis de Valor:**")
                    
                    if abs(diff) < 1.0:
                        st.info("⚖️ **Línea justa:** El casino está muy alineado con tu modelo. No hay ventaja clara.")
                    elif diff >= 1.0:
                        # El modelo da favorito al local por más de lo que pide el casino
                        st.success(f"🔥 **Valor en el Favorito ({game['Local']}):** Tu modelo espera que cubra con holgura respecto a la línea del casino.")
                    elif diff <= -1.0:
                        # El modelo da favorito al local por menos, o el casino pide demasiados puntos -> Valor en el Underdog (Visitante)
                        st.success(f" underdog 🛡️ **Valor en el Underdog ({game['Visitante']}):** El casino sobrevalora al local; hay un gran colchón a favor del visitante.")
                
                st.divider()
    else:
        st.info("No hay partidos programados para esta fecha en la NBA.")
