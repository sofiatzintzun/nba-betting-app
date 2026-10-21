import streamlit as st
import requests
from datetime import datetime

st.set_page_config(page_title="NBA Schedule & Projections", layout="centered")

st.title("🏀 NBA Schedule & Projections")

# --- SELECTOR DE FECHA ---
selected_date = st.date_input("Selecciona la fecha del juego", datetime.now())
date_str = selected_date.strftime("%Y%m%d")

# --- DICCIONARIO BASE DE DATOS DE EQUIPOS ---
TEAMS_DATA = {
    "Atlanta Hawks": {"Pace": 100.2, "ORTG": 115.0, "DRTG": 116.0},
    "Orlando Magic": {"Pace": 97.0, "ORTG": 113.5, "DRTG": 108.5},
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

# --- DICCIONARIO DE JUGADORES CLAVE POR EQUIPO (PROPS) ---
PLAYERS_PROPS = {
    "Atlanta Hawks": {"PTS": "N. Alexander-Walker", "AST": "Jalen Johnson", "REB": "Jalen Johnson", "STL": "N. Alexander-Walker", "BLK": "Clint Capela"},
    "Orlando Magic": {"PTS": "Paolo Banchero", "AST": "Franz Wagner", "REB": "Paolo Banchero", "STL": "Jalen Suggs", "BLK": "Goga Bitadze"},
    "Boston Celtics": {"PTS": "Jayson Tatum", "AST": "Jrue Holiday", "REB": "Jaylen Brown", "STL": "Derrick White", "BLK": "Kristaps Porzingis"},
    "Denver Nuggets": {"PTS": "Nikola Jokic", "AST": "Nikola Jokic", "REB": "Nikola Jokic", "STL": "Christian Braun", "BLK": "Aaron Gordon"},
    "Los Angeles Lakers": {"PTS": "Luka Doncic", "AST": "LeBron James", "REB": "Anthony Davis", "STL": "Austin Reaves", "BLK": "Anthony Davis"},
    "Golden State Warriors": {"PTS": "Stephen Curry", "AST": "Draymond Green", "REB": "Kevon Looney", "STL": "Brandin Podziemski", "BLK": "Draymond Green"},
    "Miami Heat": {"PTS": "Tyler Herro", "AST": "Jimmy Butler", "REB": "Bam Adebayo", "STL": "Jimmy Butler", "BLK": "Bam Adebayo"},
    "Dallas Mavericks": {"PTS": "Kyrie Irving", "AST": "Luka Doncic", "REB": "P.J. Washington", "STL": "Naji Marshall", "BLK": "Dereck Lively II"},
    "Milwaukee Bucks": {"PTS": "Giannis Antetokounmpo", "AST": "Damian Lillard", "REB": "Giannis Antetokounmpo", "STL": "Gary Trent Jr.", "BLK": "Brook Lopez"},
    "Philadelphia 76ers": {"PTS": "Tyrese Maxey", "AST": "Tyrese Maxey", "REB": "Joel Embiid", "STL": "Kelly Oubre Jr.", "BLK": "Joel Embiid"},
    "Phoenix Suns": {"PTS": "Kevin Durant", "AST": "Devin Booker", "REB": "Jusuf Nurkic", "STL": "Grayson Allen", "BLK": "Kevin Durant"},
    "Minnesota Timberwolves": {"PTS": "Anthony Edwards", "AST": "Mike Conley", "REB": "Rudy Gobert", "STL": "Nickeil Alexander-Walker", "BLK": "Rudy Gobert"},
    "Oklahoma City Thunder": {"PTS": "Shai Gilgeous-Alexander", "AST": "Shai Gilgeous-Alexander", "REB": "Chet Holmgren", "STL": "Alex Caruso", "BLK": "Chet Holmgren"},
    "New York Knicks": {"PTS": "Jalen Brunson", "AST": "Jalen Brunson", "REB": "Karl-Anthony Towns", "STL": "Mikal Bridges", "BLK": "Mitchell Robinson"}
}

DEFAULT_STATS = {"Pace": 99.0, "ORTG": 114.5, "DRTG": 114.5}
DEFAULT_PLAYER = {"PTS": "Líder Principal", "AST": "Playmaker", "REB": "Rebotero", "STL": "Defensor", "BLK": "Protector Aros"}

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
            
            # Obtener props de jugadores
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
                
                # Métricas de Puntos (Visit
