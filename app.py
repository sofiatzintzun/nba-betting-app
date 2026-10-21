import streamlit as st
import requests
from datetime import datetime

st.set_page_config(page_title="NBA Betting & Schedule App", layout="centered")

st.title("🏀 NBA Insight & Projections")

# --- CREAMOS PESTAÑAS (TABS) PARA ORGANIZAR LA APP ---
tab1, tab2 = st.tabs(["📅 Calendario del Día", "📊 Proyecciones de Puntos"])

# ==========================================
# PESTAÑA 1: CALENDARIO (El que ya teníamos)
# ==========================================
with tab1:
    st.subheader("Calendario y Horarios")
    selected_date = st.date_input("Selecciona la fecha del juego", datetime.now())
    date_str = selected_date.strftime("%Y%m%d")

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
                schedule_list.append({
                    "Local": home_team, "LocalLogo": home_logo,
                    "Visitante": away_team, "VisitanteLogo": away_logo,
                    "Estado": status_text
                })
            return schedule_list
        except Exception as e:
            return f"Error: {str(e)}"

    result = get_schedule(date_str)

    if isinstance(result, str):
        st.error(result)
    else:
        games = result
        st.caption(f"Partidos del {selected_date.strftime('%d/%m/%Y')} ({len(games)})")
        if games:
            for game in games:
                with st.container():
                    col1, col2, col3, col4, col5 = st.columns([1, 2.5, 1, 2.5, 1])
                    with col1: st.image(game['VisitanteLogo'], width=40)
                    with col2: st.markdown(f"**{game['Visitante']}**")
                    with col3: st.markdown("<h4 style='text-align: center; margin: 0;'>@</h4>", unsafe_allow_html=True)
                    with col4: st.markdown(f"**{game['Local']}**")
                    with col5: st.image(game['LocalLogo'], width=40)
                    st.caption(f"🕒 {game['Estado']}")
                    st.divider()
        else:
            st.info("No hay partidos programados para esta fecha.")

# ==========================================
# PESTAÑA 2: MOTOR DE PROYECCIONES
# ==========================================
with tab2:
    st.subheader("Calculadora de Proyección (Over/Under)")
    st.markdown("Simula un enfrentamiento aplicando la fórmula de **Ritmo y Eficiencias**.")

    # Base de datos simulada/ejemplo de estadísticas de equipos (ORTG, DRTG, Pace)
    # Más adelante podemos automatizar esto conectándolo a un diccionario completo.
    teams_data = {
        "Boston Celtics": {"Pace": 98.5, "ORTG": 118.0, "DRTG": 110.0},
        "Denver Nuggets": {"Pace": 97.2, "ORTG": 116.5, "DRTG": 112.1},
        "Los Angeles Lakers": {"Pace": 101.0, "ORTG": 114.2, "DRTG": 113.8},
        "Golden State Warriors": {"Pace": 100.5, "ORTG": 115.0, "DRTG": 111.5},
        "Miami Heat": {"Pace": 96.0, "ORTG": 112.0, "DRTG": 109.5},
        "Dallas Mavericks": {"Pace": 99.1, "ORTG": 117.1, "DRTG": 114.0}
    }

    team_list = list(teams_data.keys())

    col_a, col_b = st.columns(2)
    with col_a:
        away_sel = st.selectbox("Equipo Visitante", team_list, index=2)
    with col_b:
        home_sel = st.selectbox("Equipo Local", team_list, index=0)

    # Constantes promedio de la liga actual
    LEAGUE_PACE = 99.0
    LEAGUE_PTS_100 = 114.5

    if st.button("🚀 Calcular Proyección del Partido"):
        away_stats = teams_data[away_sel]
        home_stats = teams_data[home_sel]

        # 1. Game Pace Proyectado
        game_pace = (away_stats["Pace"] * home_stats["Pace"]) / LEAGUE_PACE

        # 2. Eficiencias Ajustadas
        away_adj_ortg = away_stats["ORTG"] * (home_stats["DRTG"] / LEAGUE_PTS_100)
        home_adj_ortg = home_stats["ORTG"] * (away_stats["DRTG"] / LEAGUE_PTS_100)

        # 3. Puntos Proyectados (Agregando 2.5 puntos de localía al home team)
        away_projected_pts = (away_adj_ortg / 100) * game_pace
        home_projected_pts = ((home_adj_ortg / 100) * game_pace) + 2.5

        total_projected = away_projected_pts + home_projected_pts
        spread = home_projected_pts - away_projected_pts

        # 4. Mostrar Resultados en Tarjetas Visuales
        st.success("¡Proyección calculada con éxito!")
        
        m1, m2, m3 = st.columns(3)
        m1.metric(label=f"Ptos {away_sel} (Vis)", value=round(away_projected_pts, 1))
        m2.metric(label=f"Ptos {home_sel} (Loc)", value=round(home_projected_pts, 1))
        m3.metric(label="Total Proyectado (O/U)", value=round(total_projected, 1))

        st.info(f"📊 **Ritmo Estimado del Juego:** {round(game_pace, 1)} posesiones | **Spread Proyectado:** {home_sel} por {round(abs(spread), 1)} pts.")
