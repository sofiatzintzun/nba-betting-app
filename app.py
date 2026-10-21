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
    "Atlanta Hawks": {"Pace": 100.2, "ORTG": 115.0, "DRTG": 116.0},
    "Boston Celtics": {"Pace": 98.5, "ORTG": 118.0, "DRTG": 110.0},
    "Brooklyn Nets": {"Pace": 97.8, "ORTG": 111.2, "DRTG": 115.4},
    "Charlotte Hornets": {"Pace": 98.9, "ORTG": 109.8, "DRTG": 116.2},
    "Chicago Bulls": {"Pace": 101.1, "ORTG": 112.5, "DRTG": 115.0},
    "Cleveland Cavaliers": {"Pace": 98.2, "ORTG": 117.2, "DRTG": 110.5},
    "Dallas Mavericks": {"Pace": 99.1, "ORTG": 117.1, "DRTG": 114.0},
    "Denver Nuggets": {"Pace": 97.2, "ORTG": 116.5, "DRTG": 112.1},
    "Detroit Pistons": {"Pace": 98.6, "ORTG": 110.1, "DRTG": 114.8},
    "Golden State Warriors": {"Pace": 100.5, "ORTG": 115.0, "DRTG": 111.5},
    "Houston Rockets": {"Pace": 99.0, "ORTG": 113.8, "DRTG": 111.2},
    "Indiana Pacers": {"Pace": 102.3, "ORTG": 118.5, "DRTG": 117.0},
    "LA Clippers": {"Pace": 97.1, "ORTG": 114.0, "DRTG": 112.0},
    "Los Angeles Lakers": {"Pace": 101.0, "ORTG": 114.2, "DRTG": 113.8},
    "Memphis Grizzlies": {"Pace": 100.8, "ORTG": 113.5, "DRTG": 111.8},
    "Miami Heat": {"Pace": 96.0, "ORTG": 112.0, "DRTG": 109.5},
    "Milwaukee Bucks": {"Pace": 100.2, "ORTG": 116.8, "DRTG": 113.2},
    "Minnesota Timberwolves": {"Pace": 97.5, "ORTG": 114.5, "DRTG": 108.5},
    "New Orleans Pelicans": {"Pace": 98.0, "ORTG": 114.2, "DRTG": 113.5},
    "New York Knicks": {"Pace": 95.8, "ORTG": 117.5, "DRTG": 112.3},
    "Oklahoma City Thunder": {"Pace": 99.8, "ORTG": 116.2, "DRTG": 111.0},
    "Orlando Magic": {"Pace": 97.0, "ORTG": 113.5, "DRTG": 108.5},
    "Philadelphia 76ers": {"Pace": 97.8, "ORTG": 115.5, "DRTG": 111.8},
    "Phoenix Suns": {"Pace": 98.2, "ORTG": 116.0, "DRTG": 113.0},
    "Portland Trail Blazers": {"Pace": 98.4, "ORTG": 108.9, "DRTG": 115.8},
    "Sacramento Kings": {"Pace": 99.5, "ORTG": 116.0, "DRTG": 114.5},
    "San Antonio Spurs": {"Pace": 100.1, "ORTG": 111.0, "DRTG": 113.9},
    "Toronto Raptors": {"Pace": 99.2, "ORTG": 112.3, "DRTG": 115.1},
    "Utah Jazz": {"Pace": 99.7, "ORTG": 113.0, "DRTG": 116.5},
    "Washington Wizards": {"Pace": 102.0, "ORTG": 108.5, "DRTG": 117.8}
}

# --- DICCIONARIO COMPLETO DE LOS 30 EQUIPOS (LÍDER #1 POR CATEGORÍA) ---
PLAYERS_PROPS = {
    "Atlanta Hawks": {"PTS": "Trae Young", "AST": "Trae Young", "REB": "Jalen Johnson", "STL": "Dyson Daniels", "BLK": "Clint Capela"},
    "Boston Celtics": {"PTS": "Jayson Tatum", "AST": "Jrue Holiday", "REB": "Jayson Tatum", "STL": "Derrick White", "BLK": "Kristaps Porzingis"},
    "Brooklyn Nets": {"PTS": "Cam Thomas", "AST": "Dennis Schroder", "REB": "Nic Claxton", "STL": "Ben Simmons", "BLK": "Nic Claxton"},
    "Charlotte Hornets": {"PTS": "LaMelo Ball", "AST": "LaMelo Ball", "REB": "Miles Bridges", "STL": "LaMelo Ball", "BLK": "Mark Williams"},
    "Chicago Bulls": {"PTS": "Coby White", "AST": "Josh Giddey", "REB": "Nikola Vucevic", "STL": "Ayo Dosunmu", "BLK": "Nikola Vucevic"},
    "Cleveland Cavaliers": {"PTS": "Donovan Mitchell", "AST": "Darius Garland", "REB": "Evan Mobley", "STL": "Donovan Mitchell", "BLK": "Evan Mobley"},
    "Dallas Mavericks": {"PTS": "Luka Doncic", "AST": "Luka Doncic", "REB": "Luka Doncic", "STL": "P.J. Washington", "BLK": "Dereck Lively II"},
    "Denver Nuggets": {"PTS": "Nikola Jokic", "AST": "Nikola Jokic", "REB": "Nikola Jokic", "STL": "Nikola Jokic", "BLK": "Aaron Gordon"},
    "Detroit Pistons": {"PTS": "Cade Cunningham", "AST": "Cade Cunningham", "REB": "Jalen Duren", "STL": "Cade Cunningham", "BLK": "Jalen Duren"},
    "Golden State Warriors": {"PTS": "Stephen Curry", "AST": "Draymond Green", "REB": "Kevon Looney", "STL": "Brandin Podziemski", "BLK": "Draymond Green"},
    "Houston Rockets": {"PTS": "Alperen Sengun", "AST": "Fred VanVleet", "REB": "Alperen Sengun", "STL": "Tari Eason", "BLK": "Amen Thompson"},
    "Indiana Pacers": {"PTS": "Pascal Siakam", "AST": "Tyrese Haliburton", "REB": "Myles Turner", "STL": "Tyrese Haliburton", "BLK": "Myles Turner"},
    "LA Clippers": {"PTS": "James Harden", "AST": "James Harden", "REB": "Ivica Zubac", "STL": "Kris Dunn", "BLK": "Ivica Zubac"},
    "Los Angeles Lakers": {"PTS": "Anthony Davis", "AST": "LeBron James", "REB": "Anthony Davis", "STL": "Austin Reaves", "BLK": "Anthony Davis"},
    "Memphis Grizzlies": {"PTS": "Ja Morant", "AST": "Ja Morant", "REB": "Jaren Jackson Jr.", "STL": "Marcus Smart", "BLK": "Jaren Jackson Jr."},
    "Miami Heat": {"PTS": "Tyler Herro", "AST": "Jimmy Butler", "REB": "Bam Adebayo", "STL": "Jimmy Butler", "BLK": "Bam Adebayo"},
    "Milwaukee Bucks": {"PTS": "Giannis Antetokounmpo", "AST": "Damian Lillard", "REB": "Giannis Antetokounmpo", "STL": "Gary Trent Jr.", "BLK": "Brook Lopez"},
    "Minnesota Timberwolves": {"PTS": "Anthony Edwards", "AST": "Mike Conley", "REB": "Rudy Gobert", "STL": "Nickeil Alexander-Walker", "BLK": "Rudy Gobert"},
    "New Orleans Pelicans": {"PTS": "Zion Williamson", "AST": "DeJounte Murray", "REB": "Zion Williamson", "STL": "DeJounte Murray", "BLK": "Yves Missi"},
    "New York Knicks": {"PTS": "Jalen Brunson", "AST": "Jalen Brunson", "REB": "Karl-Anthony Towns", "STL": "Mikal Bridges", "BLK": "Karl-Anthony Towns"},
    "Oklahoma City Thunder": {"PTS": "Shai Gilgeous-Alexander", "AST": "Shai Gilgeous-Alexander", "REB": "Chet Holmgren", "STL": "Alex Caruso", "BLK": "Chet Holmgren"},
    "Orlando Magic": {"PTS": "Paolo Banchero", "AST": "Franz Wagner", "REB": "Paolo Banchero", "STL": "Jalen Suggs", "BLK": "Goga Bitadze"},
    "Philadelphia 76ers": {"PTS": "Tyrese Maxey", "AST": "Tyrese Maxey", "REB": "Joel Embiid", "STL": "Kelly Oubre Jr.", "BLK": "Joel Embiid"},
    "Phoenix Suns": {"PTS": "Kevin Durant", "AST": "Devin Booker", "REB": "Jusuf Nurkic", "STL": "Grayson Allen", "BLK": "Kevin Durant"},
    "Portland Trail Blazers": {"PTS": "Anfernee Simons", "AST": "Anfernee Simons", "REB": "Deandre Ayton", "STL": "Toumani Camara", "BLK": "Donovan Clingan"},
    "Sacramento Kings": {"PTS": "De'Aaron Fox", "AST": "Domantas Sabonis", "REB": "Domantas Sabonis", "STL": "De'Aaron Fox", "BLK": "Keegan Murray"},
    "San Antonio Spurs": {"PTS": "Victor Wembanyama", "AST": "Chris Paul", "REB": "Victor Wembanyama", "STL": "Victor Wembanyama", "BLK": "Victor Wembanyama"},
    "Toronto Raptors": {"PTS": "RJ Barrett", "AST": "Immanuel Quickley", "REB": "Jakob Poeltl", "STL": "Scottie Barnes", "BLK": "Jakob Poeltl"},
    "Utah Jazz": {"PTS": "Lauri Markkanen", "AST": "Keyonte George", "REB": "Walker Kessler", "STL": "Collin Sexton", "BLK": "Walker Kessler"},
    "Washington Wizards": {"PTS": "Jordan Poole", "AST": "Carlton Carrington", "REB": "Jonas Valanciunas", "STL": "Jordan Poole", "BLK": "Alex Sarr"}
}

DEFAULT_STATS = {"Pace": 99.0, "ORTG": 114.5, "DRTG": 114.5}
DEFAULT_PLAYER = {"PTS": "Sin registrar", "AST": "Sin registrar", "REB": "Sin registrar", "STL": "Sin registrar", "BLK": "Sin registrar"}

LEAGUE_PACE = 99.0
LEAGUE_PTS_100 = 114.5

# --- FUNCIÓN DE CÁLCULO DE PROYECCIÓN ---
def calculate_projection(away_team, home_team):
    away_stats = TEAMS_DATA.get(away_team, DEFAULT_STATS)
    home_stats = TEAMS_DATA.get(home_team, DEFAULT_STATS)

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
            
            away_pts, home_pts, total_pts, game_pace, model_spread = calculate_projection(away_team, home_team)
            
            if casino_spread is None:
                casino_spread = model_spread
            if casino_ou is None:
                casino_ou = total_pts
            
            # Obtener props de jugadores con método .get() seguro
            away_players = PLAYERS_PROPS.get(away_team, DEFAULT_PLAYER)
            home_players = PLAYERS_PROPS.get(home_team, DEFAULT_PLAYER)
            
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
                "HasOdds": len(odds_data) > 0,
                "AwayPlayers": away_players,
                "HomePlayers": home_players
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
                col1, col2, col3, col4, col5 = st.columns([1, 2.5, 1, 2.5, 1])
                with col1: st.image(game['VisitanteLogo'], width=45)
                with col2: st.markdown(f"**{game['Visitante']}**")
                with col3: st.markdown("<h4 style='text-align: center; margin: 0;'>@</h4>", unsafe_allow_html=True)
                with col4: st.markdown(f"**{game['Local']}**")
                with col5: st.image(game['LocalLogo'], width=45)
                
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
                
                # --- SECCIÓN FUERA DEL CASINO: JUGADORES CLAVE (PROPS) ---
                st.markdown("👥 **Líderes Clave Recomendados (Props):**")
                p_col1, p_col2 = st.columns(2)
                
                with p_col1:
                    st.markdown(f"**{game['Visitante']}**")
                    st.markdown(f"• 🏀 Puntos: `{game['AwayPlayers'].get('PTS', 'N/A')}`")
                    st.markdown(f"• 🎯 Asistencias: `{game['AwayPlayers'].get('AST', 'N/A')}`")
                    st.markdown(f"• 🛡️ Rebotes: `{game['AwayPlayers'].get('REB', 'N/A')}`")
                    st.markdown(f"• 🛑 Robos/Bloq: `{game['AwayPlayers'].get('STL', 'N/A')} / {game['AwayPlayers'].get('BLK', 'N/A')}`")
                    
                with p_col2:
                    st.markdown(f"**{game['Local']}**")
                    st.markdown(f"• 🏀 Puntos: `{game['HomePlayers'].get('PTS', 'N/A')}`")
                    st.markdown(f"• 🎯 Asistencias: `{game['HomePlayers'].get('AST', 'N/A')}`")
                    st.markdown(f"• 🛡️ Rebotes: `{game['HomePlayers'].get('REB', 'N/A')}`")
                    st.markdown(f"• 🛑 Robos/Bloq: `{game['HomePlayers'].get('STL', 'N/A')} / {game['HomePlayers'].get('BLK', 'N/A')}`")

                # --- MODO COMPARATIVO DE VALOR (CASINO) ---
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
