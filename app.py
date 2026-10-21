import streamlit as st
import requests
from datetime import datetime

st.set_page_config(page_title="NBA Schedule & Projections", layout="centered")

# --- CSS PERSONALIZADO PARA RESPONSIVIDAD Y CABECERA EN UNA SOLA LÍNEA ---
st.markdown("""
    <style>
    /* Estilos para la cabecera de equipos en una sola línea en móviles */
    .matchup-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        width: 100%;
        margin-bottom: 10px;
    }
    .team-box {
        display: flex;
        align-items: center;
        gap: 8px;
        flex: 1;
    }
    .team-box.away {
        justify-content: flex-start;
    }
    .team-box.home {
        justify-content: flex-end;
    }
    .team-name {
        font-weight: bold;
        font-size: 0.95rem;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .at-symbol {
        font-weight: bold;
        color: #888;
        padding: 0 8px;
        font-size: 0.9rem;
    }
    
    /* Adaptaciones para métricas en celulares */
    @media (max-width: 768px) {
        .team-name {
            font-size: 0.85rem;
        }
        .stMetric {
            background-color: rgba(240, 242, 246, 0.05);
            padding: 6px;
            border-radius: 6px;
        }
        h1 {
            font-size: 1.5rem !important;
        }
    }

    /* Tarjetas de partidos */
    div[data-testid="stVerticalBlock"] > div[data-testid="stContainer"] {
        border: 1px solid #e0e0e0;
        border-radius: 12px;
        padding: 12px;
        margin-bottom: 12px;
        background-color: rgba(255, 255, 255, 0.02);
    }
    </style>
""", unsafe_allow_html=True)

st.title("🏀 NBA Schedule & Projections")

# --- SELECTOR DE FECHA ---
selected_date = st.date_input("Selecciona la fecha del juego", datetime.now())
date_str = selected_date.strftime("%Y%m%d")

# --- VALORES PROMEDIO DE LA LIGA (RESPALDO Y BASE) ---
LEAGUE_PACE = 99.0
LEAGUE_PTS_100 = 114.5

# --- FUNCIÓN PARA EXTRAER ESTADÍSTICAS DINÁMICAS DE EQUIPOS DESDE ESPN ---
@st.cache_data(ttl=3600)
def get_team_stats_from_espn():
    url = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/teams"
    teams_stats = {}
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            sports = data.get('sports', [])
            if sports:
                leagues = sports[0].get('leagues', [])
                if leagues:
                    teams_list = leagues[0].get('teams', [])
                    for t_item in teams_list:
                        team = t_item.get('team', {})
                        display_name = team.get('displayName')
                        
                        record_info = team.get('record', {}).get('items', [])
                        ppg = LEAGUE_PTS_100
                        opp_ppg = LEAGUE_PTS_100
                        
                        if record_info:
                            stats_list = record_info[0].get('stats', [])
                            for stat in stats_list:
                                if stat.get('name') == 'pointsFor':
                                    ppg = stat.get('value', LEAGUE_PTS_100)
                                elif stat.get('name') == 'pointsAgainst':
                                    opp_ppg = stat.get('value', LEAGUE_PTS_100)
                        
                        teams_stats[display_name] = {
                            "Pace": LEAGUE_PACE,
                            "ORTG": (ppg / LEAGUE_PTS_100) * 114.5,
                            "DRTG": (opp_ppg / LEAGUE_PTS_100) * 114.5
                        }
        return teams_stats
    except Exception:
        return {}

# --- FUNCIÓN DE CÁLCULO DE PROYECCIÓN DINÁMICA ---
def calculate_projection(away_team, home_team, dynamic_stats):
    default_stats = {"Pace": LEAGUE_PACE, "ORTG": LEAGUE_PTS_100, "DRTG": LEAGUE_PTS_100}
    
    away_stats = dynamic_stats.get(away_team, default_stats)
    home_stats = dynamic_stats.get(home_team, default_stats)

    game_pace = (away_stats["Pace"] * home_stats["Pace"]) / LEAGUE_PACE
    away_adj_ortg = away_stats["ORTG"] * (home_stats["DRTG"] / LEAGUE_PTS_100)
    home_adj_ortg = home_stats["ORTG"] * (away_stats["DRTG"] / LEAGUE_PTS_100)

    away_pts = (away_adj_ortg / 100) * game_pace
    home_pts = ((home_adj_ortg / 100) * game_pace) + 2.5
    total_pts = away_pts + home_pts
    spread = home_pts - away_pts

    return round(away_pts, 1), round(home_pts, 1), round(total_pts, 1), round(game_pace, 1), round(spread, 1)

# --- FUNCIÓN PARA OBTENER EL CALENDARIO Y ODDS DE ESPN ---
@st.cache_data(ttl=300)
def get_schedule(date_formatted):
    url = f"https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard?dates={date_formatted}"
    dynamic_stats = get_team_stats_from_espn()
    
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
            
            # Extraer Odds
            odds_data = competition.get('odds', [])
            casino_spread = None
            casino_ou = None
            
            if odds_data:
                odds_item = odds_data[0]
                casino_spread = odds_item.get('spread', None)
                casino_ou = odds_item.get('overUnder', None)
            
            away_pts, home_pts, total_pts, game_pace, model_spread = calculate_projection(away_team, home_team, dynamic_stats)
            
            if casino_spread is None:
                casino_spread = model_spread
            if casino_ou is None:
                casino_ou = total_pts
            
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
                "ProjSpread": model_spread,
                "CasinoSpread": float(casino_spread),
                "CasinoOU": float(casino_ou),
                "HasOdds": len(odds_data) > 0
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
        for game in games:
            with st.container():
                # --- CABECERA DE EQUIPOS UNIFICADA EN UNA SOLA LÍNEA ---
                st.markdown(f"""
                    <div class="matchup-header">
                        <div class="team-box away">
                            <img src="{game['VisitanteLogo']}" width="28"/>
                            <span class="team-name">{game['Visitante']}</span>
                        </div>
                        <span class="at-symbol">@</span>
                        <div class="team-box home">
                            <span class="team-name">{game['Local']}</span>
                            <img src="{game['LocalLogo']}" width="28"/>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                st.caption(f"🕒 Estado: {game['Estado']}")
                
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
                
                # --- MODO COMPARATIVO DE VALOR (SPREAD + TOTAL) ---
                with st.expander("🧮 Comparativa Automática con el Casino"):
                    if not game['HasOdds']:
                        st.warning("⚠️ Sin cuotas oficiales publicadas en ESPN aún.")
                    
                    st.markdown(f"**Línea detectada del Casino ({game['Local']} Spread):** `{game['CasinoSpread']}`")
                    st.markdown(f"**Línea detectada del Casino (Over/Under):** `{game['CasinoOU']}`")
                    
                    st.markdown("---")
                    st.markdown("💡 **Resultado del Análisis de Valor:**")
                    
                    # 1. Análisis de Spread
                    casino_margin_for_home = -1 * game['CasinoSpread'] if game['CasinoSpread'] < 0 else game['CasinoSpread']
                    diff_spread = game['ProjSpread'] - casino_margin_for_home
                    
                    st.markdown("🎯 **Hándicap / Spread:**")
                    if abs(diff_spread) < 0.8:
                        st.info("⚖️ **Línea justa en Spread:** El casino está alineado con el modelo.")
                    elif diff_spread > 0.8:
                        st.success(f"🔥 **Valor en el Favorito ({game['Local']}):** El modelo proyecta que gana por **{game['ProjSpread']}** pts (superando el hándicap del casino de {casino_margin_for_home} pts).")
                    else:
                        st.success(f"🛡️ **Valor en el Underdog ({game['Visitante']}):** El casino pide mucho al local ({casino_margin_for_home} pts). Margen a favor del visitante.")

                    # 2. Análisis de Total (Over/Under)
                    ou_diff = game['ProjTotal'] - game['CasinoOU']
                    
                    st.markdown("🏀 **Totales (Over/Under):**")
                    if abs(ou_diff) < 1.0:
                        st.info(f"⚖️ **Línea justa en Total:** Proyección ({game['ProjTotal']}) muy cercana a la línea del casino ({game['CasinoOU']}).")
                    elif ou_diff < -1.0:
                        st.success(f"📉 **Valor en el Under:** El casino marcó **{game['CasinoOU']}** pts, pero tu modelo proyecta **{game['ProjTotal']}** pts. Hay valor en el **Under** por **{abs(round(ou_diff, 1))}** puntos.")
                    else:
                        st.success(f"📈 **Valor en el Over:** El casino marcó **{game['CasinoOU']}** pts, pero tu modelo proyecta **{game['ProjTotal']}** pts. Hay valor en el **Over** por **{round(ou_diff, 1)}** puntos.")

                st.divider()
    else:
        st.info("No hay partidos programados para esta fecha en la NBA.")
