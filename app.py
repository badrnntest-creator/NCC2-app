# ============================================================
# 🔧 CONFIGURATION DE LA PAGE
# ============================================================

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np
import streamlit.components.v1 as components

st.set_page_config(page_title="NCC2 Dashboard", layout="wide")

def decimal_to_time(dec_hours):
    """Convertit un nombre décimal d'heures en format HH:MM:SS"""
    if pd.isna(dec_hours):
        return "00:00:00"
    total_seconds = int(dec_hours * 3600)
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    return f"{hours:02}:{minutes:02}:{seconds:02}"

# Fonction de formatage Power BI style
def format_number(value):
    """Formate les nombres avec séparateurs et K/M comme Power BI"""
    if value >= 1_000_000:
        return f"{value/1_000_000:.1f}M"
    elif value >= 1_000:
        return f"{value/1_000:.1f}K"
    else:
        return f"{value:.0f}"

def format_number_full(value):
    """Formate avec séparateurs de milliers"""
    return f"{value:,.0f}".replace(",", " ")

# ============================================================
# ---- Background image for login ----
# ============================================================

def add_bg_image():
    st.markdown("""
        <style>
        .stApp {
            background-image: url("https://media.gettyimages.com/id/1433485090/video/dots-makes-global-world-map-global-wireframe-polygonal-lines.jpg?s=640x640&k=20&c=6TpfX8QHt9IPnF0s5HkwOaNoqcNbtYP99Ceh7-iR8MI=");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }
        </style>
    """, unsafe_allow_html=True)

add_bg_image()

PASSWORD = "123"

if "start_time" not in st.session_state:
    st.session_state.start_time = None

# ============================================================
# ---- LOGIN PAGE ----
# ============================================================
if not st.session_state.start_time:
    st.markdown("<h2 style='color:white;text-shadow:2px 2px 5px black;'>Connexion au Dashboard NCC2</h2>", unsafe_allow_html=True)
    visitor_name = st.text_input("Nom du visiteur :", placeholder="Ex : ben el ahmar badr")
    password = st.text_input("Mot de passe :", type="password")
    login_button = st.button("Se connecter")

    if login_button:
        if visitor_name == "":
            st.error("Veuillez entrer votre nom.")
        elif password != PASSWORD:
            st.error("Mot de passe incorrect.")
        else:
            st.success(f"Bienvenue {visitor_name} ✔")
            st.session_state.start_time = datetime.now()
            st.session_state.visitor = visitor_name
            
            try:
                log_df = pd.read_excel("DATA NCC2.xlsx", sheet_name="LOGS")
            except:
                log_df = pd.DataFrame(columns=["Nom", "Date", "Heure d'entrée", "Temps passé (minutes)"])

            new_entry = {
                "Nom": visitor_name,
                "Date": datetime.now().date(),
                "Heure d'entrée": datetime.now().strftime("%H:%M:%S"),
                "Temps passé (minutes)": "En cours..."
            }

            log_df = pd.concat([log_df, pd.DataFrame([new_entry])], ignore_index=True)
            
            with pd.ExcelWriter("DATA NCC2.xlsx", mode="a", if_sheet_exists="replace", engine="openpyxl") as writer:
                log_df.to_excel(writer, sheet_name="LOGS", index=False)

            st.rerun()
    st.stop()

# ============================================================
# ❌ SUPPRESSION DU BACKGROUND APRÈS LOGIN
# ============================================================

def remove_bg():
    st.markdown("""
        <style>
        .stApp { background: none !important; }
        </style>
    """, unsafe_allow_html=True)

remove_bg()

# ============================================================
# 📊 CHARGEMENT DES DONNÉES
# ============================================================

@st.cache_data
def load_data():
    try:
        df = pd.read_excel("DATA NCC2.xlsx", sheet_name="Feuil1")
        df['📆date'] = pd.to_datetime(df['📆date'], format='%d/%m/%Y', errors='coerce')
        return df
    except Exception as e:
        st.error(f"Erreur lors du chargement des données : {e}")
        return pd.DataFrame()

df = load_data()


# SIDEBAR NAVIGATION
# =============================

st.markdown("""
    <style>
    [data-testid="stSidebar"] {
        background-color: #0A1A2F !important;
        padding-top: 25px;
    }
    .stButton>button {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 12px 18px;
        margin: 6px 0;
        border-radius: 8px;
        cursor: pointer;
        font-size: 15px;
        font-weight: 500;
        color: #ffffff;
        transition: 0.15s ease-in-out;
        background-color: transparent;
        border: 1px solid transparent;
        text-align: left;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #12345A;
        transform: translateX(4px);
        border-left: 3px solid #4DA8FF;
    }
    </style>
""", unsafe_allow_html=True)

icons = {
    "overview": "📊",
    "production": "🏭",
    "performances": "📈",
    "Analyse temps": "⏱️",
    "maintenance": "🛠️",
    "datarange": "📅",
    "logout": "🚪"
}

if "page" not in st.session_state:
    st.session_state.page = "overview"

def sidebar_button(label, key):
    clicked = st.sidebar.button(f"{icons[key]} {label}", key=f"btn_{key}")
    if clicked:
        st.session_state.page = key

sidebar_button("Overview", "overview")
sidebar_button("Production", "production")
sidebar_button("Performances", "performances")
sidebar_button("Analyse temps", "Analyse temps")
sidebar_button("Maintenance", "maintenance")
sidebar_button("Data Range", "datarange")

st.sidebar.markdown("---")
sidebar_button("Déconnexion", "logout")

page = st.session_state.get("page", "overview")

# ============================================================
# 📊 PAGE OVERVIEW
# ============================================================

if page == "overview":
    st.markdown("<h1 style='text-align: center;'>📊 Overview - Vue d'ensemble</h1>", unsafe_allow_html=True)
    st.markdown("---")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        oee_moyen = df['%OEE'].mean() * 100
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 20px; border-radius: 10px; color: white; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
            <div style='font-size: 14px; opacity: 0.9;'>OEE Moyen</div>
            <div style='font-size: 32px; font-weight: bold; margin: 10px 0;'>{oee_moyen:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        prod_totale = df['Total Prod ( RM consumption ) "ton"'].sum()
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
                    padding: 20px; border-radius: 10px; color: white; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
            <div style='font-size: 14px; opacity: 0.9;'>Production Totale</div>
            <div style='font-size: 32px; font-weight: bold; margin: 10px 0;'>{format_number_full(prod_totale)} T</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        dispo_moyenne = df['% Availability'].mean() * 100
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); 
                    padding: 20px; border-radius: 10px; color: white; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
            <div style='font-size: 14px; opacity: 0.9;'>Disponibilité Moyenne</div>
            <div style='font-size: 32px; font-weight: bold; margin: 10px 0;'>{dispo_moyenne:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        perf_moyenne = df['%performance'].mean() * 100
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); 
                    padding: 20px; border-radius: 10px; color: white; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
            <div style='font-size: 14px; opacity: 0.9;'>Performance Moyenne</div>
            <div style='font-size: 32px; font-weight: bold; margin: 10px 0;'>{perf_moyenne:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Évolution de l'OEE")
        df_grouped = df.groupby('📆date')['%OEE'].mean().reset_index()
        fig = px.line(df_grouped, x='📆date', y='%OEE', 
                     title='OEE dans le temps',
                     labels={'%OEE': 'OEE (%)', '📆date': 'Date'})
        fig.update_traces(line_color='#667eea', line_width=3)
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🏭 Production par Shift")
        prod_shift = df.groupby('🛄 shift')['Total Prod ( RM consumption ) "ton"'].sum().reset_index()
        fig = px.bar(prod_shift, x='🛄 shift', y='Total Prod ( RM consumption ) "ton"',
                    title='Production totale par shift',
                    color='Total Prod ( RM consumption ) "ton"',
                    color_continuous_scale='Viridis')
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("📋 Dernières Productions")
    colonnes_affichage = ['📆date', '🛄 shift', 'Operator 👷‍♂️:', 'Total Prod ( RM consumption ) "ton"', 
                         '%OEE', '% Availability', '%performance']
    st.dataframe(df[colonnes_affichage].tail(10).sort_values('📆date', ascending=False), 
                use_container_width=True, height=300)

# ============================================================
# 🏭 PAGE PRODUCTION
# ============================================================

elif page == "production":
    st.markdown("<h1 style='text-align: center;'>🏭 Production - Analyse Détaillée</h1>", unsafe_allow_html=True)
    st.markdown("---")

    def format_k(value):
        if value >= 1_000_000:
            return f"{value/1_000_000:.1f}M"
        elif value >= 1_000:
            return f"{value/1_000:.1f}K"
        else:
            return f"{value:.0f}"
    df['📆date'] = pd.to_datetime(df['📆date'])
    # ===================== CALCULS TEMPORELS =====================
    nb_days = df['📆date'].nunique()
    nb_months = df[['YEARS', 'MONTH']].drop_duplicates().shape[0]

    # Totaux
    total_rm = df['Total Prod ( RM consumption ) "ton"'].sum()
    total_out1 = df['OUTPUT 1 "ton"'].sum()
    total_out2 = df['OUTPUT 2 "ton"'].sum()

    # Moyennes
    rm_day_avg = total_rm / nb_days if nb_days > 0 else 0
    rm_month_avg = total_rm / nb_months if nb_months > 0 else 0

    out1_day_avg = total_out1 / nb_days if nb_days > 0 else 0
    out1_month_avg = total_out1 / nb_months if nb_months > 0 else 0

    out2_day_avg = total_out2 / nb_days if nb_days > 0 else 0
    out2_month_avg = total_out2 / nb_months if nb_months > 0 else 0

    # Pourcentages vs RM
    pct_out1 = (total_out1 / total_rm * 100) if total_rm > 0 else 0
    pct_out2 = (total_out2 / total_rm * 100) if total_rm > 0 else 0

    # ============================================================
    # LIGNE 01 — KPIs + GRAPHES (STYLE POWER BI)
    # ============================================================

    col1, col2, col3 = st.columns(3)

    # ===================== COL 1 : RAW MATERIAL =====================
    with col1:
        st.subheader("📦 Raw Material")

        st.metric("Total RM", f"{format_k(total_rm)} T")
        st.metric("Moyenne / Jour", f"{format_k(rm_day_avg)} T/j")
        st.metric("Moyenne / Mois", f"{format_k(rm_month_avg)} T/mois")
        st.markdown("---")

        rm_rep = (
            df.groupby('Input( Raw material type )')
            ['Total Prod ( RM consumption ) "ton"']
            .sum()
            .reset_index()
            .sort_values('Total Prod ( RM consumption ) "ton"', ascending=True)  
            # ← important : ascending=True pour avoir le plus grand en haut en horizontal
        )

        fig = go.Figure(go.Bar(
            y=rm_rep['Input( Raw material type )'],
            x=rm_rep['Total Prod ( RM consumption ) "ton"'],
            orientation="h",
            text=[
                f"{format_k(v)} T ({v/total_rm*100:.1f}%)"
                for v in rm_rep['Total Prod ( RM consumption ) "ton"']
            ],
            textposition="outside",
            marker_color="#667eea"
        ))

        fig.update_layout(
            height=300,
            margin=dict(l=10, r=10, t=30, b=10),

            # 🚫 Suppression de l’axe X
            xaxis=dict(
                showticklabels=False,
                showgrid=False,
                zeroline=False,
                title=""
            ),

            # Nettoyage axe Y
            yaxis=dict(
                title="",
                automargin=True
            )
        )

        st.plotly_chart(fig, use_container_width=True)

    # ===================== COL 2 : OUTPUT 1 =====================
    with col2:
        st.subheader("📤 Output 1 (Export)")

        st.metric("Total Output 1", f"{format_k(total_out1)} T ({pct_out1:.1f}%)")
        st.metric("Moyenne / Jour", f"{format_k(out1_day_avg)} T/j")
        st.metric("Moyenne / Mois", f"{format_k(out1_month_avg)} T/mois")

        st.markdown("---")

        out1_rep = (
            df.groupby('OUTPUT 1 ( type of export product )')
            ['OUTPUT 1 "ton"']
            .sum()
            .reset_index()
            .sort_values('OUTPUT 1 "ton"', ascending=True)
            # ↑ ascending=True pour afficher le plus grand en haut
        )

        fig = go.Figure(go.Bar(
            y=out1_rep['OUTPUT 1 ( type of export product )'],
            x=out1_rep['OUTPUT 1 "ton"'],
            orientation="h",
            text=[
                f"{format_k(v)} T ({v/total_rm*100:.1f}%)"
                for v in out1_rep['OUTPUT 1 "ton"']
            ],
            textposition="outside",
            marker_color="#f5576c"
        ))

        fig.update_layout(
            height=300,
            margin=dict(l=10, r=10, t=30, b=10),

            # 🚫 Suppression axe X
            xaxis=dict(
                showticklabels=False,
                showgrid=False,
                zeroline=False,
                title=""
            ),

            # Nettoyage axe Y
            yaxis=dict(
                title="",
                automargin=True
            )
        )

        # Sécurité si le texte dépasse
        fig.update_traces(cliponaxis=False)

        st.plotly_chart(fig, use_container_width=True)


    # ===================== COL 3 : OUTPUT 2 =====================
    with col3:
        st.subheader("📥 Output 2 (Fine)")

        st.metric("Total Output 2", f"{format_k(total_out2)} T ({pct_out2:.1f}%)")
        st.metric("Moyenne / Jour", f"{format_k(out2_day_avg)} T/j")
        st.metric("Moyenne / Mois", f"{format_k(out2_month_avg)} T/mois")

        st.markdown("---")

        out2_rep = (
            df.groupby('OUTPUT 2 ( type of seconde output )')
            ['OUTPUT 2 "ton"']
            .sum()
            .reset_index()
            .sort_values('OUTPUT 2 "ton"', ascending=True)
            # ↑ ascending=True → plus grand en haut (barres horizontales)
        )

        fig = go.Figure(go.Bar(
            y=out2_rep['OUTPUT 2 ( type of seconde output )'],
            x=out2_rep['OUTPUT 2 "ton"'],
            orientation="h",
            text=[
                f"{format_k(v)} T ({v/total_rm*100:.1f}%)"
                for v in out2_rep['OUTPUT 2 "ton"']
            ],
            textposition="outside",
            marker_color="#4facfe"
        ))

        fig.update_layout(
            height=300,
            margin=dict(l=10, r=10, t=30, b=10),

            # 🚫 Suppression axe X
            xaxis=dict(
                showticklabels=False,
                showgrid=False,
                zeroline=False,
                title=""
            ),

            # Nettoyage axe Y
            yaxis=dict(
                title="",
                automargin=True
            )
        )

        # Sécurité si le texte dépasse la zone
        fig.update_traces(cliponaxis=False)

        st.plotly_chart(fig, use_container_width=True)

    
    # ============================================================
    # LIGNE 02 : RM CONSUMPTION
    # ============================================================
    def format_k(v):
        return f"{v/1000:.1f}K" if v >= 1000 else f"{v:.0f}"

    st.markdown("### 📦 Raw Material Consumption Analysis")
    st.markdown("#### RM Consumption Timeline")

    gran_rm1 = st.radio("", ["Jour", "Mois", "Année"], horizontal=True, key="gr1")

    if gran_rm1 == "Jour":
        rm_time = df.groupby('📆date')['Total Prod ( RM consumption ) "ton"'].sum().reset_index()
        x_col = '📆date'
    elif gran_rm1 == "Mois":
        df['Mois'] = df['📆date'].dt.to_period('M').astype(str)
        rm_time = df.groupby('Mois')['Total Prod ( RM consumption ) "ton"'].sum().reset_index()
        x_col = 'Mois'
    else:
        rm_time = df.groupby('YEARS')['Total Prod ( RM consumption ) "ton"'].sum().reset_index()
        x_col = 'YEARS'

    y = rm_time['Total Prod ( RM consumption ) "ton"']
    moyenne = y.mean()

    # Comptage BI
    nb_total = len(y)
    nb_above = (y > moyenne).sum()
    nb_below = (y < moyenne).sum()

    pct_above = nb_above / nb_total * 100
    pct_below = nb_below / nb_total * 100

    # Couleurs conditionnelles
    colors = ['#2ecc71' if v >= moyenne else '#e74c3c' for v in y]

    fig = go.Figure()

    # Bar chart
    fig.add_trace(go.Bar(
        x=rm_time[x_col],
        y=y,
        marker_color=colors,
        text=[format_k(v) for v in y],
        textposition='outside',
        name='RM Consumption'
    ))

    # Ligne moyenne
    fig.add_trace(go.Scatter(
        x=rm_time[x_col],
        y=[moyenne]*nb_total,
        mode='lines',
        name=f'Moyenne : {format_k(moyenne)}',
        line=dict(color='#34495e', dash='dash', width=2)
    ))

    fig.update_layout(
        height=420,
        hovermode='x unified',
        yaxis_title='Tonnes',
        showlegend=True,
        margin=dict(l=10, r=10, t=70, b=20),

        # Annotation BI en haut
        annotations=[
            dict(
                x=0.01,
                y=1.15,
                xref='paper',
                yref='paper',
                text=f"<b style='color:#2ecc71'>▲ {pct_above:.1f}% au-dessus de la moyenne</b>",
                showarrow=False
            ),
            dict(
                x=0.5,
                y=1.15,
                xref='paper',
                yref='paper',
                text=f"<b style='color:#e74c3c'>▼ {pct_below:.1f}% en-dessous de la moyenne</b>",
                showarrow=False
            )
        ]
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("#### RM by Type (Stacked)")
    gran_rm2 = st.radio("", ["Jour", "Mois", "Année"], horizontal=True, key="gr2")

    if gran_rm2 == "Jour":
        rm_type = df.groupby(['📆date', 'Input( Raw material type )'])['Total Prod ( RM consumption ) "ton"'].sum().reset_index()
        x_col = '📆date'
    elif gran_rm2 == "Mois":
        df['Mois'] = df['📆date'].dt.to_period('M').astype(str)
        rm_type = df.groupby(['Mois', 'Input( Raw material type )'])['Total Prod ( RM consumption ) "ton"'].sum().reset_index()
        x_col = 'Mois'
    else:
        rm_type = df.groupby(['YEARS', 'Input( Raw material type )'])['Total Prod ( RM consumption ) "ton"'].sum().reset_index()
        x_col = 'YEARS'

    fig = px.bar(rm_type, x=x_col, y='Total Prod ( RM consumption ) "ton"',
                color='Input( Raw material type )',
                text_auto=True, barmode='stack')
    fig.update_traces(texttemplate='%{y:.0f}', textposition='inside')
    fig.update_layout(height=400, yaxis_title='Tonnes')
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
        
    # ============================================================
    # LIGNE 03 : OUTPUT 1
    # ============================================================
    st.markdown("### 📤 OUTPUT 1 - Export Product Analysis")
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("#### Répartition OUTPUT 1")
        out1_detail = df.groupby('OUTPUT 1 ( type of export product )')[
            'OUTPUT 1 "ton"'].sum().reset_index()
        out1_detail['Pourcentage'] = (out1_detail['OUTPUT 1 "ton"'] / 
                                       out1_detail['OUTPUT 1 "ton"'].sum() * 100)
        out1_detail = out1_detail.sort_values('OUTPUT 1 "ton"', ascending=False)
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            name='Tonnes',
            x=out1_detail['OUTPUT 1 ( type of export product )'],
            y=out1_detail['OUTPUT 1 "ton"'],
            text=[format_number(v) + ' T' for v in out1_detail['OUTPUT 1 "ton"']],
            textposition='outside',
            marker_color='#f5576c'
        ))
        fig.add_trace(go.Bar(
            name='%',
            x=out1_detail['OUTPUT 1 ( type of export product )'],
            y=out1_detail['Pourcentage'],
            text=[f"{v:.1f}%" for v in out1_detail['Pourcentage']],
            textposition='outside',
            marker_color='#f093fb',
            yaxis='y2'
        ))
        
        fig.update_layout(
            barmode='group',
            height=450,
            yaxis=dict(title='Tonnes'),
            yaxis2=dict(title='%', overlaying='y', side='right')
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### OUTPUT 1 Timeline (Stacked)")
        gran_out1 = st.radio("", ["Jour", "Mois", "Année"], horizontal=True, key="gro1")
        
        if gran_out1 == "Jour":
            out1_time = df.groupby(['📆date', 'OUTPUT 1 ( type of export product )'])[
                'OUTPUT 1 "ton"'].sum().reset_index()
            x_col = '📆date'
        elif gran_out1 == "Mois":
            df['Mois'] = df['📆date'].dt.to_period('M').astype(str)
            out1_time = df.groupby(['Mois', 'OUTPUT 1 ( type of export product )'])[
                'OUTPUT 1 "ton"'].sum().reset_index()
            x_col = 'Mois'
        else:
            out1_time = df.groupby(['YEARS', 'OUTPUT 1 ( type of export product )'])[
                'OUTPUT 1 "ton"'].sum().reset_index()
            x_col = 'YEARS'
        
        fig = px.bar(out1_time, x=x_col, y='OUTPUT 1 "ton"',
                    color='OUTPUT 1 ( type of export product )',
                    text_auto=True, barmode='stack',
                    color_discrete_sequence=px.colors.sequential.Reds_r)
        fig.update_traces(texttemplate='%{y:.0f}', textposition='inside')
        fig.update_layout(height=450, yaxis_title='Tonnes')
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ============================================================
    # LIGNE 04 : OUTPUT 2
    # ============================================================
    st.markdown("### 📥 OUTPUT 2 - Fine Product Analysis")
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("#### Répartition OUTPUT 2")
        out2_detail = df.groupby('OUTPUT 2 ( type of seconde output )')[
            'OUTPUT 2 "ton"'].sum().reset_index()
        out2_detail['Pourcentage'] = (out2_detail['OUTPUT 2 "ton"'] / 
                                       out2_detail['OUTPUT 2 "ton"'].sum() * 100)
        out2_detail = out2_detail.sort_values('OUTPUT 2 "ton"', ascending=False)
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            name='Tonnes',
            x=out2_detail['OUTPUT 2 ( type of seconde output )'],
            y=out2_detail['OUTPUT 2 "ton"'],
            text=[format_number(v) + ' T' for v in out2_detail['OUTPUT 2 "ton"']],
            textposition='outside',
            marker_color='#4facfe'
        ))
        fig.add_trace(go.Bar(
            name='%',
            x=out2_detail['OUTPUT 2 ( type of seconde output )'],
            y=out2_detail['Pourcentage'],
            text=[f"{v:.1f}%" for v in out2_detail['Pourcentage']],
            textposition='outside',
            marker_color='#00f2fe',
            yaxis='y2'
        ))
        
        fig.update_layout(
            barmode='group',
            height=450,
            yaxis=dict(title='Tonnes'),
            yaxis2=dict(title='%', overlaying='y', side='right')
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### OUTPUT 2 Timeline (Stacked)")
        gran_out2 = st.radio("", ["Jour", "Mois", "Année"], horizontal=True, key="gro2")
        
        if gran_out2 == "Jour":
            out2_time = df.groupby(['📆date', 'OUTPUT 2 ( type of seconde output )'])[
                'OUTPUT 2 "ton"'].sum().reset_index()
            x_col = '📆date'
        elif gran_out2 == "Mois":
            df['Mois'] = df['📆date'].dt.to_period('M').astype(str)
            out2_time = df.groupby(['Mois', 'OUTPUT 2 ( type of seconde output )'])[
                'OUTPUT 2 "ton"'].sum().reset_index()
            x_col = 'Mois'
        else:
            out2_time = df.groupby(['YEARS', 'OUTPUT 2 ( type of seconde output )'])[
                'OUTPUT 2 "ton"'].sum().reset_index()
            x_col = 'YEARS'
        
        fig = px.bar(out2_time, x=x_col, y='OUTPUT 2 "ton"',
                    color='OUTPUT 2 ( type of seconde output )',
                    text_auto=True, barmode='stack',
                    color_discrete_sequence=px.colors.sequential.Blues_r)
        fig.update_traces(texttemplate='%{y:.0f}', textposition='inside')
        fig.update_layout(height=450, yaxis_title='Tonnes')
        st.plotly_chart(fig, use_container_width=True)

# ============================================================
# 📈 PAGE PERFORMANCES
# ============================================================
elif page == "performances":
    st.markdown("<h1 style='text-align: center;'>📈 Performances_Analyse OEE_Analyse Cadadence_Analyse temps</h1>", unsafe_allow_html=True)
    st.markdown("---")
    
    # ============================================================
    # SECTION 01 : ANALYSE OEE
    # ============================================================
    st.markdown("### Ⅰ_Analyse OEE🎯:")
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ============================================================
    # LIGNE 1 : 4 CARTES KPI (OEE, TP, TD, TQ)
    # ============================================================
    col1, col2, col3, col4 = st.columns(4)
    
    # Fonction pour créer une carte KPI
    def create_kpi_card(title, icon, mean_val, max_val, min_val, std_val, gradient_color1, gradient_color2):
        html_content = f"""
        <div style='background: linear-gradient(135deg, {gradient_color1}, {gradient_color2});
                    padding: 20px; border-radius: 15px; color: white; 
                    box-shadow: 0 4px 15px rgba(0,0,0,0.1); height: 200px;'>
            <div style='display: flex; align-items: center; gap: 10px; margin-bottom: 10px;'>
                <div style='font-size: 28px;'>{icon}</div>
                <div style='font-size: 13px; font-weight: 600; opacity: 0.9;'>{title}</div>
            </div>
            <div style='font-size: 38px; font-weight: 800; margin: 10px 0;'>{mean_val:.0f}%</div>
            <div style='font-size: 11px; opacity: 0.9; margin-bottom: 5px;'>Moyenne</div>
            <div style='display: flex; justify-content: space-between; margin-top: 15px;'>
                <div style='background: rgba(255,255,255,0.15); padding: 8px 12px; border-radius: 8px; flex: 1; margin-right: 5px;'>
                    <div style='font-size: 9px; opacity: 0.8;'>MAX</div>
                    <div style='font-size: 16px; font-weight: bold; color: #4ade80;'>{max_val:.0f}%</div>
                </div>
                <div style='background: rgba(255,255,255,0.15); padding: 8px 12px; border-radius: 8px; flex: 1; margin: 0 5px;'>
                    <div style='font-size: 9px; opacity: 0.8;'>MIN</div>
                    <div style='font-size: 16px; font-weight: bold; color: #ef4444;'>{min_val:.0f}%</div>
                </div>
                <div style='background: rgba(255,255,255,0.15); padding: 8px 12px; border-radius: 8px; flex: 1; margin-left: 5px;'>
                    <div style='font-size: 9px; opacity: 0.8;'>ÉCART</div>
                    <div style='font-size: 16px; font-weight: bold;color: #6050DC;'>±{std_val:.1f}%</div>
                </div>
            </div>
        </div>
        """
        return html_content
    
    with col1:
        oee_mean = df['%OEE'].mean() * 100
        oee_max = df['%OEE'].max() * 100
        oee_min = df['%OEE'].min() * 100
        oee_std = df['%OEE'].std() * 100
        st.markdown(create_kpi_card("OEE", "🎯", oee_mean, oee_max, oee_min, oee_std, 
                                     "rgba(102, 126, 234, 0.9)", "rgba(118, 75, 162, 0.9)"), 
                    unsafe_allow_html=True)
    
    with col2:
        tp_mean = df['%performance'].mean() * 100
        tp_max = df['%performance'].max() * 100
        tp_min = df['%performance'].min() * 100
        tp_std = df['%performance'].std() * 100
        st.markdown(create_kpi_card("TP (Performance)", "⚡", tp_mean, tp_max, tp_min, tp_std,
                                     "rgba(245, 87, 108, 0.9)", "rgba(240, 147, 251, 0.9)"), 
                    unsafe_allow_html=True)
    
    with col3:
        td_mean = df['% Availability'].mean() * 100
        td_max = df['% Availability'].max() * 100
        td_min = df['% Availability'].min() * 100
        td_std = df['% Availability'].std() * 100
        st.markdown(create_kpi_card("TD (Disponibilité)", "🔧", td_mean, td_max, td_min, td_std,
                                     "rgba(79, 172, 254, 0.9)", "rgba(0, 242, 254, 0.9)"), 
                    unsafe_allow_html=True)
    
    with col4:
        tq_mean = df['%Quality'].mean() * 100
        tq_max = df['%Quality'].max() * 100
        tq_min = df['%Quality'].min() * 100
        tq_std = df['%Quality'].std() * 100
        st.markdown(create_kpi_card("TQ (Qualité)", "✅", tq_mean, tq_max, tq_min, tq_std,
                                     "rgba(250, 112, 154, 0.9)", "rgba(254, 225, 64, 0.9)"), 
                    unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ============================================================
    # LIGNE 2 : COURBE DE TENDANCE OEE/TP/TD/TQ
    # ============================================================
    st.markdown("#### 📈 Tendances des Indicateurs (Analyse OEE) ")
    
    # Contrôle de granularité
    gran_perf = st.radio("", ["Jour", "Mois", "Année"], horizontal=True, key="gran_perf")
    
    if gran_perf == "Jour":
        perf_time = df.groupby('📆date')[['%OEE', '%performance', '% Availability', '%Quality']].mean().reset_index()
        x_col = '📆date'
        show_text = False
    elif gran_perf == "Mois":
        df['Mois'] = df['📆date'].dt.to_period('M').astype(str)
        perf_time = df.groupby('Mois')[['%OEE', '%performance', '% Availability', '%Quality']].mean().reset_index()
        x_col = 'Mois'
        show_text = True
    else:
        perf_time = df.groupby('YEARS')[['%OEE', '%performance', '% Availability', '%Quality']].mean().reset_index()
        x_col = 'YEARS'
        show_text = True
    
    perf_time[['%OEE', '%performance', '% Availability', '%Quality']] *= 100
    
    # Calcul des moyennes
    oee_avg = perf_time['%OEE'].mean()
    tp_avg = perf_time['%performance'].mean()
    td_avg = perf_time['% Availability'].mean()
    tq_avg = perf_time['%Quality'].mean()
    
    # Calcul des points au-dessus/en-dessous de la moyenne EN POURCENTAGE
    total_points = len(perf_time)
    oee_above_pct = (perf_time['%OEE'] >= oee_avg).sum() / total_points * 100
    oee_below_pct = (perf_time['%OEE'] < oee_avg).sum() / total_points * 100
    tp_above_pct = (perf_time['%performance'] >= tp_avg).sum() / total_points * 100
    tp_below_pct = (perf_time['%performance'] < tp_avg).sum() / total_points * 100
    td_above_pct = (perf_time['% Availability'] >= td_avg).sum() / total_points * 100
    td_below_pct = (perf_time['% Availability'] < td_avg).sum() / total_points * 100
    tq_above_pct = (perf_time['%Quality'] >= tq_avg).sum() / total_points * 100
    tq_below_pct = (perf_time['%Quality'] < tq_avg).sum() / total_points * 100
    
    # Affichage des indicateurs au-dessus du graphique
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div style='background: rgba(102, 126, 234, 0.1); padding: 10px; border-radius: 8px; text-align: center;'>
            <div style='font-size: 11px; color: #667eea; font-weight: 600;'>OEE</div>
            <div style='font-size: 14px; margin-top: 5px;'>
                <span style='color: #4ade80; font-weight: bold;'>▲ {oee_above_pct:.0f}%</span> | 
                <span style='color: #ef4444; font-weight: bold;'>▼ {oee_below_pct:.0f}%</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style='background: rgba(245, 87, 108, 0.1); padding: 10px; border-radius: 8px; text-align: center;'>
            <div style='font-size: 11px; color: #f5576c; font-weight: 600;'>TP</div>
            <div style='font-size: 14px; margin-top: 5px;'>
                <span style='color: #4ade80; font-weight: bold;'>▲ {tp_above_pct:.0f}%</span> | 
                <span style='color: #ef4444; font-weight: bold;'>▼ {tp_below_pct:.0f}%</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div style='background: rgba(79, 172, 254, 0.1); padding: 10px; border-radius: 8px; text-align: center;'>
            <div style='font-size: 11px; color: #4facfe; font-weight: 600;'>TD</div>
            <div style='font-size: 14px; margin-top: 5px;'>
                <span style='color: #4ade80; font-weight: bold;'>▲ {td_above_pct:.0f}%</span> | 
                <span style='color: #ef4444; font-weight: bold;'>▼ {td_below_pct:.0f}%</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div style='background: rgba(250, 112, 154, 0.1); padding: 10px; border-radius: 8px; text-align: center;'>
            <div style='font-size: 11px; color: #fa709a; font-weight: 600;'>TQ</div>
            <div style='font-size: 14px; margin-top: 5px;'>
                <span style='color: #4ade80; font-weight: bold;'>▲ {tq_above_pct:.0f}%</span> | 
                <span style='color: #ef4444; font-weight: bold;'>▼ {tq_below_pct:.0f}%</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
    
    # Graphique de tendance
    fig = go.Figure()
    
    # Courbes principales avec les couleurs des cartes KPI
    fig.add_trace(go.Scatter(
        x=perf_time[x_col], 
        y=perf_time['%OEE'],
        mode='lines+markers+text' if show_text else 'lines+markers',
        name='OEE',
        line=dict(color="#cc34da", width=1.5),  # Violet (OEE)
        marker=dict(size=5, color="#7711dd"),
        text=[f'{v:.0f}%' for v in perf_time['%OEE']] if show_text else None,
        textposition='top center',
        textfont=dict(size=10, color="#4B005A")
    ))
    
    fig.add_trace(go.Scatter(
        x=perf_time[x_col], 
        y=perf_time['%performance'],
        mode='lines+markers+text' if show_text else 'lines+markers',
        name='TP',
        line=dict(color="#e23c8f", width=1.5),  # Rose/Rouge (TP)
        marker=dict(size=5, color="#bd339a"),
        text=[f'{v:.0f}%' for v in perf_time['%performance']] if show_text else None,
        textposition='top center',
        textfont=dict(size=10, color="#5a0044")
    ))
    
    fig.add_trace(go.Scatter(
        x=perf_time[x_col], 
        y=perf_time['% Availability'],
        mode='lines+markers+text' if show_text else 'lines+markers',
        name='TD',
        line=dict(color="#2618a5", width=2),  # Bleu (TD)
        marker=dict(size=5, color="#0115c9"),
        text=[f'{v:.0f}%' for v in perf_time['% Availability']] if show_text else None,
        textposition='top center',
        textfont=dict(size=10, color="#09005a")
    ))
    
    fig.add_trace(go.Scatter(
        x=perf_time[x_col], 
        y=perf_time['%Quality'],
        mode='lines+markers+text' if show_text else 'lines+markers',
        name='TQ',
        line=dict(color="#be9c02", width=1.5),  # Rose/Jaune (TQ)
        marker=dict(size=4, color="#b69b00"),
        text=[f'{v:.0f}%' for v in perf_time['%Quality']] if show_text else None,
        textposition='top center',
        textfont=dict(size=10, color="#ac8d03")
    ))
    
    # Lignes de moyenne (en pointillés)
    fig.add_trace(go.Scatter(
        x=perf_time[x_col], y=[oee_avg] * len(perf_time),
        mode='lines', name=f'Moy. OEE: {oee_avg:.0f}%',
        line=dict(color='#667eea', width=2, dash='dash'),
        showlegend=True
    ))
    
    fig.add_trace(go.Scatter(
        x=perf_time[x_col], y=[tp_avg] * len(perf_time),
        mode='lines', name=f'Moy. TP: {tp_avg:.0f}%',
        line=dict(color='#f5576c', width=1.5, dash='dash'),
        showlegend=True
    ))
    
    fig.add_trace(go.Scatter(
        x=perf_time[x_col], y=[td_avg] * len(perf_time),
        mode='lines', name=f'Moy. TD: {td_avg:.0f}%',
        line=dict(color='#4facfe', width=1.5, dash='dash'),
        showlegend=True
    ))
    
    fig.add_trace(go.Scatter(
        x=perf_time[x_col], y=[tq_avg] * len(perf_time),
        mode='lines', name=f'Moy. TQ: {tq_avg:.0f}%',
        line=dict(color='#fee140', width=1.5, dash='dash'),
        showlegend=True
    ))
    
    fig.update_layout(
        height=450,
        hovermode='x unified',
        yaxis_title='Pourcentage (%)',
        xaxis_title='',
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        yaxis=dict(range=[0, 105])
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ============================================================
    # LIGNE 3 : ANALYSE PAR SHIFT, OPERATEUR ET RAW MATERIAL
    # ============================================================
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### 🏭 Analyse OEE per Shift")
        
        shift_analysis = df.groupby('🛄 shift')[['%OEE', '%performance', '% Availability', '%Quality']].mean().reset_index()
        shift_analysis[['%OEE', '%performance', '% Availability', '%Quality']] *= 100
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            name='OEE',
            x=shift_analysis['🛄 shift'],
            y=shift_analysis['%OEE'],
            text=[f'{v:.0f}%' for v in shift_analysis['%OEE']],
            textposition='inside',
            marker_color='#667eea'
        ))
        
        fig.add_trace(go.Bar(
            name='TP',
            x=shift_analysis['🛄 shift'],
            y=shift_analysis['%performance'],
            text=[f'{v:.0f}%' for v in shift_analysis['%performance']],
            textposition='inside',
            marker_color='#f5576c'
        ))
        
        fig.add_trace(go.Bar(
            name='TD',
            x=shift_analysis['🛄 shift'],
            y=shift_analysis['% Availability'],
            text=[f'{v:.0f}%' for v in shift_analysis['% Availability']],
            textposition='inside',
            marker_color='#4facfe'
        ))
        
        fig.add_trace(go.Bar(
            name='TQ',
            x=shift_analysis['🛄 shift'],
            y=shift_analysis['%Quality'],
            text=[f'{v:.0f}%' for v in shift_analysis['%Quality']],
            textposition='inside',
            marker_color='#fa709a'
        ))
        
        fig.update_layout(
            barmode='group',
            height=400,
            yaxis_title='Pourcentage (%)',
            xaxis_title='Shift',
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### 👷‍♂️ Analyse OEE per Operator")
        
        operator_analysis = df.groupby('Operator 👷‍♂️:')[['%OEE', '%performance', '% Availability', '%Quality']].mean().reset_index()
        operator_analysis[['%OEE', '%performance', '% Availability', '%Quality']] *= 100
        operator_analysis = operator_analysis.sort_values('%OEE', ascending=False)
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            name='OEE',
            x=operator_analysis['Operator 👷‍♂️:'],
            y=operator_analysis['%OEE'],
            text=[f'{v:.0f}%' for v in operator_analysis['%OEE']],
            textposition='inside',
            marker_color='#667eea'
        ))
        
        fig.add_trace(go.Bar(
            name='TP',
            x=operator_analysis['Operator 👷‍♂️:'],
            y=operator_analysis['%performance'],
            text=[f'{v:.0f}%' for v in operator_analysis['%performance']],
            textposition='inside',
            marker_color='#f5576c'
        ))
        
        fig.add_trace(go.Bar(
            name='TD',
            x=operator_analysis['Operator 👷‍♂️:'],
            y=operator_analysis['% Availability'],
            text=[f'{v:.0f}%' for v in operator_analysis['% Availability']],
            textposition='inside',
            marker_color='#4facfe'
        ))
        
        fig.add_trace(go.Bar(
            name='TQ',
            x=operator_analysis['Operator 👷‍♂️:'],
            y=operator_analysis['%Quality'],
            text=[f'{v:.0f}%' for v in operator_analysis['%Quality']],
            textposition='inside',
            marker_color='#fa709a'
        ))
        
        fig.update_layout(
            barmode='group',
            height=400,
            yaxis_title='Pourcentage (%)',
            xaxis_title='Operator',
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col3:
        st.markdown("#### 📦 Analyse OEE per Raw Material")
        
        rm_analysis = df.groupby('Input( Raw material type )')[['%OEE', '%performance', '% Availability', '%Quality']].mean().reset_index()
        rm_analysis[['%OEE', '%performance', '% Availability', '%Quality']] *= 100
        rm_analysis = rm_analysis.sort_values('%OEE', ascending=False)
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            name='OEE',
            x=rm_analysis['Input( Raw material type )'],
            y=rm_analysis['%OEE'],
            text=[f'{v:.0f}%' for v in rm_analysis['%OEE']],
            textposition='inside',
            marker_color='#667eea'
        ))
        
        fig.add_trace(go.Bar(
            name='TP',
            x=rm_analysis['Input( Raw material type )'],
            y=rm_analysis['%performance'],
            text=[f'{v:.0f}%' for v in rm_analysis['%performance']],
            textposition='inside',
            marker_color='#f5576c'
        ))
        
        fig.add_trace(go.Bar(
            name='TD',
            x=rm_analysis['Input( Raw material type )'],
            y=rm_analysis['% Availability'],
            text=[f'{v:.0f}%' for v in rm_analysis['% Availability']],
            textposition='inside',
            marker_color='#4facfe'
        ))
        
        fig.add_trace(go.Bar(
            name='TQ',
            x=rm_analysis['Input( Raw material type )'],
            y=rm_analysis['%Quality'],
            text=[f'{v:.0f}%' for v in rm_analysis['%Quality']],
            textposition='inside',
            marker_color='#fa709a'
        ))
        
        fig.update_layout(
            barmode='group',
            height=400,
            yaxis_title='Pourcentage (%)',
            xaxis_title='Raw Material Type',
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    # ============================================================
    # SECTION 02 : ANALYSE CADENCES PRODUCTION
    # ============================================================
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("### ⚡ Analyse Cadences Production")
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ============================================================
    # LIGNE 1 : HISTOGRAMME + BOXPLOT + TIMELINE CADENCE
    # ============================================================
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📊 Distribution des Cadences")
        
        cadence_data = df['Production Rate t/h'].dropna()
        mean_cadence = cadence_data.mean()
        median_cadence = cadence_data.median()
        
        # Créer subplot avec histogramme et boxplot
        from plotly.subplots import make_subplots
        
        fig = make_subplots(
            rows=2, cols=1,
            row_heights=[0.7, 0.3],
            vertical_spacing=0.05,
            subplot_titles=('Distribution', 'Box Plot')
        )
        
        # Histogramme
        fig.add_trace(
            go.Histogram(
                x=cadence_data,
                nbinsx=30,
                name='Fréquence',
                marker=dict(
                    color='#667eea',
                    line=dict(color='white', width=1)
                ),
                opacity=0.7
            ),
            row=1, col=1
        )
        
        # Lignes de moyenne et médiane
        fig.add_vline(x=mean_cadence, line_dash="dash", line_color="#f5576c", 
                     annotation_text=f"Moy: {mean_cadence:.1f}",
                     annotation_position="top", row=1)
        fig.add_vline(x=median_cadence, line_dash="dot", line_color="#4facfe",
                     annotation_text=f"Méd: {median_cadence:.1f}",
                     annotation_position="bottom", row=1)
        
        # Box Plot horizontal
        fig.add_trace(
            go.Box(
                x=cadence_data,
                name='',
                marker_color='#667eea',
                fillcolor='rgba(102, 126, 234, 0.5)',
                line=dict(color='#667eea', width=2),
                boxmean='sd'
            ),
            row=2, col=1
        )
        
        fig.update_xaxes(title_text="Cadence (T/h)", row=2, col=1)
        fig.update_yaxes(title_text="Fréquence", row=1, col=1)
        fig.update_yaxes(showticklabels=False, row=2, col=1)
        
        fig.update_layout(
            height=400,
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### 📈 Évolution de la Cadence")
        
        # Contrôle de granularité
        gran_cadence = st.radio("", ["Jour", "Mois", "Année"], horizontal=True, key="gran_cadence")
        
        if gran_cadence == "Jour":
            cadence_time = df.groupby('📆date')['Production Rate t/h'].mean().reset_index()
            x_col = '📆date'
            show_text = False
        elif gran_cadence == "Mois":
            df['Mois'] = df['📆date'].dt.to_period('M').astype(str)
            cadence_time = df.groupby('Mois')['Production Rate t/h'].mean().reset_index()
            x_col = 'Mois'
            show_text = True
        else:
            cadence_time = df.groupby('YEARS')['Production Rate t/h'].mean().reset_index()
            x_col = 'YEARS'
            show_text = True
        
        # Calcul de la moyenne et des points au-dessus/dessous
        cadence_avg = cadence_time['Production Rate t/h'].mean()
        total_points = len(cadence_time)
        above_avg_pct = (cadence_time['Production Rate t/h'] >= cadence_avg).sum() / total_points * 100
        below_avg_pct = (cadence_time['Production Rate t/h'] < cadence_avg).sum() / total_points * 100
        
        # Indicateur au-dessus du graphique
        st.markdown(f"""
        <div style='background: rgba(102, 126, 234, 0.1); padding: 10px; border-radius: 8px; text-align: center; margin-bottom: 10px;'>
            <div style='font-size: 11px; color: #667eea; font-weight: 600;'>CADENCE</div>
            <div style='font-size: 14px; margin-top: 5px;'>
                <span style='color: #4ade80; font-weight: bold;'>▲ {above_avg_pct:.0f}%</span> | 
                <span style='color: #ef4444; font-weight: bold;'>▼ {below_avg_pct:.0f}%</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        fig = go.Figure()
        
        # Courbe principale
        fig.add_trace(go.Scatter(
            x=cadence_time[x_col],
            y=cadence_time['Production Rate t/h'],
            mode='lines+markers+text' if show_text else 'lines+markers',
            name='Cadence',
            line=dict(color="#ac008f", width=1.5),
            marker=dict(size=5, color='#764ba2'),
            text=[f'{v:.0f}' for v in cadence_time['Production Rate t/h']] if show_text else None,
            textposition='top center',
            textfont=dict(size=10, color="#002fff"),
            fill='tozeroy',
            fillcolor='rgba(102, 126, 234, 0.2)'
        ))
        
        # Ligne de moyenne
        fig.add_trace(go.Scatter(
            x=cadence_time[x_col],
            y=[cadence_avg] * len(cadence_time),
            mode='lines',
            name=f'Moyenne: {cadence_avg:.1f} T/h',
            line=dict(color='#f5576c', width=2, dash='dash')
        ))
        
        fig.update_layout(
            height=400,
            yaxis_title='Cadence (T/h)',
            xaxis_title='',
            hovermode='x unified',
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ============================================================
    # LIGNE 2 : ANALYSE CADENCE PAR SHIFT / OPERATOR / RAW MATERIAL
    # ============================================================
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### 🏭 Cadence per Shift")
        
        # Violin Plot avec moyenne affichée
        fig = go.Figure()
        
        shifts = df['🛄 shift'].unique()
        colors = ['#667eea', '#f5576c', '#4facfe']
        
        for i, shift in enumerate(shifts):
            shift_data = df[df['🛄 shift'] == shift]['Production Rate t/h'].dropna()
            shift_mean = shift_data.mean()
            
            # Violin plot
            fig.add_trace(go.Violin(
                y=shift_data,
                name=shift,
                box_visible=True,
                meanline_visible=True,
                fillcolor=colors[i % len(colors)],
                opacity=0.6,
                x0=shift,
                line_color=colors[i % len(colors)]
            ))
            
            # Annoter la moyenne sur le graphique
            fig.add_annotation(
                x=i,
                y=shift_mean,
                text=f"Moy: {shift_mean:.0f}",
                showarrow=True,
                arrowhead=2,
                arrowcolor=colors[i % len(colors)],
                font=dict(size=10, color=colors[i % len(colors)], family='Arial Black'),
                bgcolor='white',
                bordercolor=colors[i % len(colors)],
                borderwidth=2,
                borderpad=4
            )
        
        fig.update_layout(
            height=400,
            yaxis_title='Cadence (T/h)',
            xaxis_title='Shift',
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### 👷‍♂️ Cadence per Operator")
        
        # Histogramme groupé avec ligne de moyenne
        operator_cadence = df.groupby('Operator 👷‍♂️:')['Production Rate t/h'].mean().reset_index()
        operator_cadence = operator_cadence.sort_values('Production Rate t/h', ascending=False)
        
        fig = go.Figure()
        
        # Barres
        fig.add_trace(go.Bar(
            x=operator_cadence['Operator 👷‍♂️:'],
            y=operator_cadence['Production Rate t/h'],
            marker_color='#f5576c',
            text=[f'{v:.0f}' for v in operator_cadence['Production Rate t/h']],
            textposition='outside',
            textfont=dict(size=11, color="#001486", family='Arial Black'),
            name='Cadence'
        ))
        
        fig.update_layout(
            height=400,
            yaxis_title='Cadence (T/h)',
            xaxis_title='Operator',
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col3:
        st.markdown("#### 📦 Cadence per Raw Material")
        
        # Violin Plot avec moyenne affichée (identique à Shift)
        fig = go.Figure()
        
        rm_types = df['Input( Raw material type )'].unique()
        colors_rm = ['#4facfe', '#00f2fe', '#7ec8ff']
        
        for i, rm in enumerate(rm_types):
            rm_data = df[df['Input( Raw material type )'] == rm]['Production Rate t/h'].dropna()
            rm_mean = rm_data.mean()
            
            # Violin plot
            fig.add_trace(go.Violin(
                y=rm_data,
                name=rm,
                box_visible=True,
                meanline_visible=True,
                fillcolor=colors_rm[i % len(colors_rm)],
                opacity=0.6,
                x0=rm,
                line_color=colors_rm[i % len(colors_rm)]
            ))
            
            # Annoter la moyenne
            fig.add_annotation(
                x=i,
                y=rm_mean,
                text=f"Moy: {rm_mean:.0f}",
                showarrow=True,
                arrowhead=2,
                arrowcolor=colors_rm[i % len(colors_rm)],
                font=dict(size=10, color=colors_rm[i % len(colors_rm)], family='Arial Black'),
                bgcolor='white',
                bordercolor=colors_rm[i % len(colors_rm)],
                borderwidth=2,
                borderpad=4
            )
        
        fig.update_layout(
            height=400,
            yaxis_title='Cadence (T/h)',
            xaxis_title='Raw Material Type',
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)

# ============================================================
# SECTION 03 : ANALYSE TEMPS
# ============================================================
elif page == "Analyse temps":  # ← Changé de "Analyse temps" à "temps"
    st.markdown("<h1 style='text-align: center;'>⏱️ Analyse Temps - Time Analysis</h1>", unsafe_allow_html=True)
    st.markdown("---")
    
    # ============================================================
    # SECTION 1 : VUE D'ENSEMBLE DES TEMPS
    # ============================================================
    st.markdown("### ⏰ Vue d'ensemble des Temps")
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ============================================================
    # LIGNE 1 : 5 CARTES KPI (STYLE GRIS TRANSPARENT)
    # ============================================================
    
    def create_time_kpi_card(title, icon, total_hours, avg_day, avg_month, percentage_label, percentage_value):
        html_content = f"""
        <div style="background: rgba(120,120,120,0.10); border: 1px solid rgba(200,200,200,0.35); border-radius: 14px; padding: 14px 16px; height: 240px; display: flex; flex-direction: column; justify-content: space-between; box-shadow: 0 3px 12px rgba(0,0,0,0.08);">
            <div style="display:flex; align-items:center; gap:8px;">
                <div style="font-size:18px;">{icon}</div>
                <div style="font-size:12px; font-weight:600; color:#555; text-transform: uppercase;">{title}</div>
            </div>
            <div style="font-size:34px; font-weight:800; color:#111; text-align:center; margin: 6px 0;">
                {total_hours:.1f} <span style="font-size:14px;">h</span>
            </div>
            <div style="display:flex; gap:10px;">
                <div style="flex:1; background: rgba(160,160,160,0.12); border-radius:8px; padding:8px; text-align:center;">
                    <div style="font-size:9px; color:#666;">MOY / JOUR</div>
                    <div style="font-size:13px; font-weight:700;">{avg_day:.1f} h</div>
                </div>
                <div style="flex:1; background: rgba(160,160,160,0.12); border-radius:8px; padding:8px; text-align:center;">
                    <div style="font-size:9px; color:#666;">MOY / MOIS</div>
                    <div style="font-size:13px; font-weight:700;">{avg_month:.1f} h</div>
                </div>
            </div>
            <div style="background: rgba(16,185,129,0.15); border-radius:8px; padding:8px; text-align:center;">
                <div style="font-size:9px; color:#047857;">{percentage_label}</div>
                <div style="font-size:15px; font-weight:800; color:#10b981;">{percentage_value:.1f} %</div>
            </div>
        </div>
        """
        return html_content
    
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    # Calculs des temps (déjà en heures décimales, * 24 pour conversion)
    opening_time_total = df['OPENING TIME'].sum() * 24
    opening_time_per_day = df.groupby('📆date')['OPENING TIME'].sum().mean() * 24
    opening_time_per_month = df.groupby(['YEARS', 'MONTH'])['OPENING TIME'].sum().mean() * 24
    
    time_required_total = df['TIME REQUIRED'].sum() * 24
    time_required_per_day = df.groupby('📆date')['TIME REQUIRED'].sum().mean() * 24
    time_required_per_month = df.groupby(['YEARS', 'MONTH'])['TIME REQUIRED'].sum().mean() * 24
    time_required_pct = (time_required_total / opening_time_total * 100) if opening_time_total > 0 else 0
    
    operating_time_total = df['OPERATING TIME'].sum() * 24
    operating_time_per_day = df.groupby('📆date')['OPERATING TIME'].sum().mean() * 24
    operating_time_per_month = df.groupby(['YEARS', 'MONTH'])['OPERATING TIME'].sum().mean() * 24
    operating_time_pct = (operating_time_total / time_required_total * 100) if time_required_total > 0 else 0
    
    # CALCULER directement au lieu de lire les colonnes
    planned_downtime_total = opening_time_total - time_required_total
    planned_downtime_per_day = (df.groupby('📆date')['OPENING TIME'].sum().mean() - 
                                df.groupby('📆date')['TIME REQUIRED'].sum().mean()) * 24
    planned_downtime_per_month = (df.groupby(['YEARS', 'MONTH'])['OPENING TIME'].sum().mean() - 
                                  df.groupby(['YEARS', 'MONTH'])['TIME REQUIRED'].sum().mean()) * 24
    planned_downtime_pct = (planned_downtime_total / opening_time_total * 100) if opening_time_total > 0 else 0
    
    unplanned_downtime_total = time_required_total - operating_time_total
    unplanned_downtime_per_day = (df.groupby('📆date')['TIME REQUIRED'].sum().mean() - 
                                  df.groupby('📆date')['OPERATING TIME'].sum().mean()) * 24
    unplanned_downtime_per_month = (df.groupby(['YEARS', 'MONTH'])['TIME REQUIRED'].sum().mean() - 
                                    df.groupby(['YEARS', 'MONTH'])['OPERATING TIME'].sum().mean()) * 24
    unplanned_downtime_pct = (unplanned_downtime_total / time_required_total * 100) if time_required_total > 0 else 0
    
    with col1:
        st.markdown(create_time_kpi_card(
            "OPENING TIME", "⏰", 
            opening_time_total, opening_time_per_day, opening_time_per_month,
            "Référence", 100.0
        ), unsafe_allow_html=True)
    
    with col2:
        st.markdown(create_time_kpi_card(
            "TIME REQUIRED", "📋", 
            time_required_total, time_required_per_day, time_required_per_month,
            "% du Opening Time", time_required_pct
        ), unsafe_allow_html=True)
    
    with col3:
        st.markdown(create_time_kpi_card(
            "OPERATING TIME", "✅", 
            operating_time_total, operating_time_per_day, operating_time_per_month,
            "% du Time Required", operating_time_pct
        ), unsafe_allow_html=True)
    
    with col4:
        st.markdown(create_time_kpi_card(
            "PLANNED DOWNTIME", "📅", 
            planned_downtime_total, planned_downtime_per_day, planned_downtime_per_month,
            "% du Opening Time", planned_downtime_pct
        ), unsafe_allow_html=True)
    
    with col5:
        st.markdown(create_time_kpi_card(
            "UNPLANNED DOWNTIME", "⚠️", 
            unplanned_downtime_total, unplanned_downtime_per_day, unplanned_downtime_per_month,
            "% du Time Required", unplanned_downtime_pct
        ), unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)

    # ============================================================
    # LIGNE 2 : WATERFALL CHART
    # ============================================================
    st.markdown("#### 🌊 Cascade des Temps (Waterfall)")

    # ===============================
    # CALCUL DES POURCENTAGES
    # ===============================
    pct_planned = (planned_downtime_total / opening_time_total) * 100
    pct_unplanned = (unplanned_downtime_total / opening_time_total) * 100
    pct_operating = (operating_time_total / opening_time_total) * 100

    fig = go.Figure(go.Waterfall(
        name="Temps",
        orientation="v",
        measure=["absolute", "relative", "total", "relative", "total"],
        x=[
            "Opening Time",
            "Planned<br>Downtime",
            "Time<br>Required",
            "Unplanned<br>Downtime",
            "Operating<br>Time"
        ],
        textposition="outside",
        text=[
            f"{opening_time_total:.1f}h<br><b>100%</b>",
            f"-{planned_downtime_total:.1f}h<br><span style='color:#ef4444'>-{pct_planned:.1f}%</span>",
            f"{time_required_total:.1f}h<br><b>{100 - pct_planned:.1f}%</b>",
            f"-{unplanned_downtime_total:.1f}h<br><span style='color:#ef4444'>-{pct_unplanned:.1f}%</span>",
            f"{operating_time_total:.1f}h<br><b>{pct_operating:.1f}%</b>"
        ],
        y=[
            opening_time_total,
            -planned_downtime_total,
            0,
            -unplanned_downtime_total,
            0
        ],
        connector={"line": {"color": "rgba(100, 100, 100, 0.5)", "width": 2}},
        decreasing={"marker": {"color": "#ef4444"}},
        increasing={"marker": {"color": "#10b981"}},
        totals={"marker": {"color": "#3b82f6"}}
    ))

    fig.update_layout(
        height=450,
        showlegend=False,
        yaxis_title="Heures",
        uniformtext_minsize=10,
        uniformtext_mode="hide"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("<br><br>", unsafe_allow_html=True)

    
    # ============================================================
    # SECTION 2 : ANALYSE UTILISATION DU TEMPS
    # ============================================================

    st.markdown("### 📊 Analyse Utilisation du Temps")
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### 🍩 Répartition Opening Time")
        
        time_on_total = df['TIME ON hh:mm:ss'].sum() * 24
        time_off_total = df['TIME OFF hh:mm:ss'].sum() * 24
        
        fig = go.Figure(go.Pie(
            labels=['TIME ON', 'TIME OFF'],
            values=[time_on_total, time_off_total],
            hole=0.6,
            marker=dict(colors=['#10b981', '#ef4444'], line=dict(color='white', width=3)),
            texttemplate="<b>%{label}</b><br>%{value:.0f}h<br>(%{percent})",
            textfont=dict(size=12, color='white', family='Arial Black'),
            textposition='inside'
        ))
        
        fig.add_annotation(
            text=f"<b>TOTAL</b><br>{time_on_total + time_off_total:.0f}h",
            font=dict(size=16, color='#666', family='Arial Black'),
            showarrow=False,
            x=0.5, y=0.5
        )
        
        fig.update_layout(height=350, showlegend=False, margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### 📊 Utilisation par Shift")
        
        shift_time = df.groupby('🛄 shift')[['TIME ON hh:mm:ss', 'TIME OFF hh:mm:ss']].sum() * 24
        shift_time_pct = shift_time.div(shift_time.sum(axis=1), axis=0) * 100
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            y=shift_time.index,
            x=shift_time_pct['TIME ON hh:mm:ss'],
            name='TIME ON',
            orientation='h',
            marker_color='#10b981',
            text=[f"{v:.0f}%" for v in shift_time_pct['TIME ON hh:mm:ss']],
            textposition='inside',
            textfont=dict(color='white', size=14, family='Arial Black')
        ))
        
        fig.add_trace(go.Bar(
            y=shift_time.index,
            x=shift_time_pct['TIME OFF hh:mm:ss'],
            name='TIME OFF',
            orientation='h',
            marker_color='#ef4444',
            text=[f"{v:.0f}%" for v in shift_time_pct['TIME OFF hh:mm:ss']],
            textposition='inside',
            textfont=dict(color='white', size=14, family='Arial Black')
        ))
        
        fig.update_layout(
            barmode='stack',
            height=350,
            xaxis_title='Pourcentage (%)',
            yaxis_title='',
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col3:
        st.markdown("#### 📈 Timeline Utilisation")
        
        gran_time = st.radio("", ["Jour", "Mois", "Année"], horizontal=True, key="gran_time")
        
        if gran_time == "Jour":
            time_timeline = df.groupby('📆date')[['%TIME ON / OPTIMAL TIME', '%TIME OFF / OPTIMAL TIME']].mean().reset_index()
            x_col = '📆date'
            show_text = False
        elif gran_time == "Mois":
            df['Mois'] = df['📆date'].dt.to_period('M').astype(str)
            time_timeline = df.groupby('Mois')[['%TIME ON / OPTIMAL TIME', '%TIME OFF / OPTIMAL TIME']].mean().reset_index()
            x_col = 'Mois'
            show_text = True
        else:
            time_timeline = df.groupby('YEARS')[['%TIME ON / OPTIMAL TIME', '%TIME OFF / OPTIMAL TIME']].mean().reset_index()
            x_col = 'YEARS'
            show_text = True
        
        time_timeline[['%TIME ON / OPTIMAL TIME', '%TIME OFF / OPTIMAL TIME']] *= 100
        
        fig = go.Figure()
        
        # TIME ON
        fig.add_trace(go.Scatter(
            x=time_timeline[x_col],
            y=time_timeline['%TIME ON / OPTIMAL TIME'],
            mode='lines+markers+text' if show_text else 'lines+markers',
            name='TIME ON',
            line=dict(color='#10b981', width=3),
            marker=dict(size=8),
            text=[f"{v:.0f}%" for v in time_timeline['%TIME ON / OPTIMAL TIME']] if show_text else None,
            textposition='top center',
            fill='tozeroy',
            fillcolor='rgba(16, 185, 129, 0.2)'
        ))
        
        # TIME OFF
        fig.add_trace(go.Scatter(
            x=time_timeline[x_col],
            y=time_timeline['%TIME OFF / OPTIMAL TIME'],
            mode='lines+markers+text' if show_text else 'lines+markers',
            name='TIME OFF',
            line=dict(color='#ef4444', width=3),
            marker=dict(size=8),
            text=[f"{v:.0f}%" for v in time_timeline['%TIME OFF / OPTIMAL TIME']] if show_text else None,
            textposition='bottom center',
            fill='tozeroy',
            fillcolor='rgba(239, 68, 68, 0.2)'
        ))
        
        # Moyennes
        time_on_avg = time_timeline['%TIME ON / OPTIMAL TIME'].mean()
        time_off_avg = time_timeline['%TIME OFF / OPTIMAL TIME'].mean()
        
        fig.add_hline(y=time_on_avg, line_dash="dash", line_color="#10b981", 
                     annotation_text=f"Moy ON: {time_on_avg:.0f}%")
        fig.add_hline(y=time_off_avg, line_dash="dash", line_color="#ef4444",
                     annotation_text=f"Moy OFF: {time_off_avg:.0f}%")
        
        fig.update_layout(
            height=350,
            yaxis_title='% Optimal Time',
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # ============================================================
    # SECTION 3 : ANALYSE DES ARRÊTS
    # ============================================================
    st.markdown("### 🛑 Analyse des Arrêts (Downtimes)")
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.markdown("#### ☀️ Hiérarchie des Arrêts (Sunburst)")
        
        # Préparer données pour Sunburst
        downtime_data = {
            'Maintenance': df['maintenance downtime'].sum() * 24,
            'Cleaning': df['stock removal / factory cleaning work'].sum() * 24,
            'Retard Prod': df['retard engine prod'].sum() * 24,
            'Loading Export': df['NAVIRE LOADING EXPORT'].sum() * 24,
            'Lack RM': df['lack of RM'].sum() * 24,
            'Prod Loss': df['Prod loss time'].sum() * 24
        }
        
        # Créer structure pour Sunburst
        labels = ['Total Downtime'] + list(downtime_data.keys())
        parents = [''] + ['Total Downtime'] * len(downtime_data)
        values = [sum(downtime_data.values())] + list(downtime_data.values())
        
        # Couleurs TRÈS distinctes
        colors_sunburst = ['#94a3b8',  # Gris pour total
                          '#3b82f6',  # Bleu saphir - Maintenance
                          '#06b6d4',  # Cyan - Cleaning
                          '#8b5cf6',  # Violet - Retard
                          '#ec4899',  # Rose - Loading
                          '#f59e0b',  # Orange - Lack RM
                          '#10b981']  # Vert - Prod Loss
        
        fig = go.Figure(go.Sunburst(
            labels=labels,
            parents=parents,
            values=values,
            branchvalues="total",
            marker=dict(colors=colors_sunburst, line=dict(color='white', width=2)),
            texttemplate="<b>%{label}</b><br>%{value:.0f}h<br>(%{percentParent})",
            textfont=dict(size=11, color='white', family='Arial Black'),
            hovertemplate='<b>%{label}</b><br>%{value:.0f}h<br>%{percentParent}<extra></extra>'
        ))
        
        fig.update_layout(height=450, margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### 📊 Pareto - Top Causes")
        
        downtime_sorted = sorted(downtime_data.items(), key=lambda x: x[1], reverse=True)
        causes = [item[0] for item in downtime_sorted]
        hours = [item[1] for item in downtime_sorted]
        cumulative = np.cumsum(hours) / sum(hours) * 100
        
        fig = go.Figure()
        
        # Barres
        fig.add_trace(go.Bar(
            x=causes,
            y=hours,
            name='Heures',
            marker=dict(
                color=hours,
                colorscale=[[0, '#10b981'], [0.5, '#f59e0b'], [1, '#ef4444']],
                showscale=False
            ),
            text=[f"{h:.0f}h" for h in hours],
            textposition='outside',
            yaxis='y'
        ))
        
        # Courbe cumulative
        fig.add_trace(go.Scatter(
            x=causes,
            y=cumulative,
            name='Cumulatif',
            mode='lines+markers',
            line=dict(color='#f97316', width=3),
            marker=dict(size=10),
            yaxis='y2'
        ))
        
        fig.add_hline(
            y=80,
            line_dash="dash",
            line_color="#ef4444",
            annotation_text="80%",
            yref="y2"
)

        fig.update_layout(
            height=450,
            yaxis=dict(title='Heures', side='left'),
            yaxis2=dict(title='Cumulatif (%)', side='right', overlaying='y', range=[0, 105]),
            xaxis_tickangle=-45,
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("<br><br>", unsafe_allow_html=True)
    
    # ============================================================
    # SECTION 4 : ANALYSE TEMPORELLE DES ARRÊTS
    # ============================================================
    st.markdown("### 📅 Analyse Temporelle des Arrêts")
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🔥 Heatmap Calendar - Unplanned Downtime")
        
        # CALCULER Unplanned Downtime au lieu de lire la colonne
        df_temp = df.copy()
        df_temp['Unplanned_Hours'] = (df_temp['TIME REQUIRED'] - df_temp['OPERATING TIME']) * 24
        
        # Préparer données pour heatmap
        heatmap_data = df_temp.groupby('📆date')['Unplanned_Hours'].sum().reset_index()
        heatmap_data['Heures'] = heatmap_data['Unplanned_Hours']
        heatmap_data['Jour'] = heatmap_data['📆date'].dt.day_name()
        heatmap_data['Semaine'] = heatmap_data['📆date'].dt.isocalendar().week
        
        # Créer pivot pour heatmap
        pivot_data = heatmap_data.pivot_table(
            index='Semaine',
            columns='Jour',
            values='Heures',
            aggfunc='mean'
        )
        
        # Réorganiser les jours de la semaine
        days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        pivot_data = pivot_data.reindex(columns=[d for d in days_order if d in pivot_data.columns])
        
        fig = go.Figure(data=go.Heatmap(
            z=pivot_data.values,
            x=pivot_data.columns,
            y=pivot_data.index,
            colorscale=[[0, '#10b981'], [0.5, '#fbbf24'], [1, '#ef4444']],
            text=np.round(pivot_data.values, 1),
            texttemplate='%{text}h',
            textfont=dict(size=10, color='white', family='Arial Black'),
            hovertemplate='Semaine: %{y}<br>Jour: %{x}<br>Heures: %{z:.1f}h<extra></extra>',
            colorbar=dict(title='Heures')
        ))
        
        fig.update_layout(
            height=400,
            xaxis_title='Jour de la semaine',
            yaxis_title='Semaine',
            yaxis=dict(autorange='reversed')
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### 📈 Évolution Arrêts (Stacked Area)")
        
        # Contrôle de granularité
        gran_downtime = st.radio("", ["Jour", "Mois", "Année"], horizontal=True, key="gran_downtime")
        
        if gran_downtime == "Jour":
            downtime_timeline = df.groupby('📆date')[
                ['maintenance downtime', 'stock removal / factory cleaning work', 
                 'retard engine prod', 'NAVIRE LOADING EXPORT', 'lack of RM', 'Prod loss time']
            ].sum().reset_index()
            x_col = '📆date'
        elif gran_downtime == "Mois":
            df['Mois'] = df['📆date'].dt.to_period('M').astype(str)
            downtime_timeline = df.groupby('Mois')[
                ['maintenance downtime', 'stock removal / factory cleaning work', 
                 'retard engine prod', 'NAVIRE LOADING EXPORT', 'lack of RM', 'Prod loss time']
            ].sum().reset_index()
            x_col = 'Mois'
        else:
            downtime_timeline = df.groupby('YEARS')[
                ['maintenance downtime', 'stock removal / factory cleaning work', 
                 'retard engine prod', 'NAVIRE LOADING EXPORT', 'lack of RM', 'Prod loss time']
            ].sum().reset_index()
            x_col = 'YEARS'
        
        # Convertir en heures
        for col in ['maintenance downtime', 'stock removal / factory cleaning work', 
                    'retard engine prod', 'NAVIRE LOADING EXPORT', 'lack of RM', 'Prod loss time']:
            downtime_timeline[col] = downtime_timeline[col] * 24
        
        fig = go.Figure()
        
        # Couleurs distinctes
        colors_area = {
            'maintenance downtime': '#3b82f6',
            'stock removal / factory cleaning work': '#06b6d4',
            'retard engine prod': '#8b5cf6',
            'NAVIRE LOADING EXPORT': '#ec4899',
            'lack of RM': '#f59e0b',
            'Prod loss time': '#10b981'
        }
        
        for col, color in colors_area.items():
            fig.add_trace(go.Scatter(
                x=downtime_timeline[x_col],
                y=downtime_timeline[col],
                name=col.replace('downtime', '').replace('stock removal / factory cleaning work', 'Cleaning'),
                mode='lines',
                stackgroup='one',
                fillcolor=color,
                line=dict(width=0.5, color=color),
                opacity=0.7
            ))
        
        fig.update_layout(
            height=400,
            yaxis_title='Heures',
            xaxis_title='',
            hovermode='x unified',
            legend=dict(orientation='v', yanchor='top', y=1, xanchor='left', x=1.02)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # ============================================================
    # SECTION 5 : ANALYSE COMPARATIVE
    # ============================================================
    st.markdown("### 🔄 Analyse Comparative des Arrêts")
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### 🏭 Downtime per Shift")
        
        shift_downtime = df.groupby('🛄 shift')[
            ['maintenance downtime', 'stock removal / factory cleaning work', 
             'retard engine prod', 'NAVIRE LOADING EXPORT', 'lack of RM', 'Prod loss time']
        ].sum() * 24
        
        fig = go.Figure()
        
        colors_bar = ['#3b82f6', '#06b6d4', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981']
        
        for i, col in enumerate(shift_downtime.columns):
            fig.add_trace(go.Bar(
                name=col.replace('downtime', '').replace('stock removal / factory cleaning work', 'Cleaning')[:15],
                x=shift_downtime.index,
                y=shift_downtime[col],
                marker_color=colors_bar[i],
                text=[f"{v:.0f}h" for v in shift_downtime[col]],
                textposition='inside',
                textfont=dict(size=9, color='white')
            ))
        
        fig.update_layout(
            barmode='group',
            height=400,
            yaxis_title='Heures',
            xaxis_title='Shift',
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### 👷‍♂️ Downtime per Operator")
        
        operator_downtime = df.groupby('Operator 👷‍♂️:')[
            ['maintenance downtime', 'stock removal / factory cleaning work', 
             'retard engine prod', 'NAVIRE LOADING EXPORT', 'lack of RM', 'Prod loss time']
        ].sum() * 24
        
        # Calculer total et trier
        operator_downtime['Total'] = operator_downtime.sum(axis=1)
        operator_downtime = operator_downtime.sort_values('Total', ascending=False)
        operator_downtime = operator_downtime.drop('Total', axis=1)
        
        fig = go.Figure()
        
        for i, col in enumerate(operator_downtime.columns):
            fig.add_trace(go.Bar(
                name=col.replace('downtime', '').replace('stock removal / factory cleaning work', 'Cleaning')[:15],
                x=operator_downtime.index,
                y=operator_downtime[col],
                marker_color=colors_bar[i],
                text=[f"{v:.0f}h" if v > 0 else "" for v in operator_downtime[col]],
                textposition='inside',
                textfont=dict(size=9, color='white')
            ))
        
        fig.update_layout(
            barmode='group',
            height=400,
            yaxis_title='Heures',
            xaxis_title='Operator',
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col3:
        st.markdown("#### 📊 Distribution %TIME ON")
        
        fig = go.Figure()
        
        shifts = df['🛄 shift'].unique()
        colors_violin = ['#3b82f6', '#ec4899', '#8b5cf6']
        
        for i, shift in enumerate(shifts):
            shift_data = df[df['🛄 shift'] == shift]['%TIME ON / OPTIMAL TIME'].dropna() * 100
            
            fig.add_trace(go.Violin(
                y=shift_data,
                name=shift,
                box_visible=True,
                meanline_visible=True,
                fillcolor=colors_violin[i % len(colors_violin)],
                opacity=0.6,
                x0=shift,
                line_color=colors_violin[i % len(colors_violin)]
            ))
        
        fig.update_layout(
            height=400,
            yaxis_title='% TIME ON',
            xaxis_title='Shift',
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # ============================================================
    # SECTION 6 : FOCUS MAINTENANCE
    # ============================================================
    st.markdown("### 🔧 Focus Maintenance")
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### 📉 Évolution Maintenance")
        
        maint_timeline = df.groupby('📆date')['maintenance downtime'].sum().reset_index()
        maint_timeline['Heures'] = maint_timeline['maintenance downtime'] * 24
        maint_timeline['Rolling_Avg'] = maint_timeline['Heures'].rolling(window=7, min_periods=1).mean()
        
        maint_avg = maint_timeline['Heures'].mean()
        
        fig = go.Figure()
        
        # Courbe principale
        fig.add_trace(go.Scatter(
            x=maint_timeline['📆date'],
            y=maint_timeline['Heures'],
            mode='lines',
            name='Maintenance',
            line=dict(color='#3b82f6', width=2),
            fill='tozeroy',
            fillcolor='rgba(59, 130, 246, 0.2)'
        ))
        
        # Rolling average
        fig.add_trace(go.Scatter(
            x=maint_timeline['📆date'],
            y=maint_timeline['Rolling_Avg'],
            mode='lines',
            name='Moyenne mobile 7j',
            line=dict(color='#f59e0b', width=3, dash='dash')
        ))
        
        # Bandes de seuil
        fig.add_hrect(y0=0, y1=maint_avg*0.7, fillcolor='#10b981', opacity=0.1, line_width=0)
        fig.add_hrect(y0=maint_avg*0.7, y1=maint_avg*1.3, fillcolor='#fbbf24', opacity=0.1, line_width=0)
        fig.add_hrect(y0=maint_avg*1.3, y1=maint_timeline['Heures'].max()*1.1, fillcolor='#ef4444', opacity=0.1, line_width=0)
        
        fig.add_hline(y=maint_avg, line_dash="dot", line_color="#666",
                     annotation_text=f"Moyenne: {maint_avg:.1f}h")
        
        fig.update_layout(
            height=350,
            yaxis_title='Heures',
            xaxis_title='',
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### 📊 Analyse OEE – Performance & Disponibilité")

        # ===============================
        # 1️⃣ PRÉPARATION DES DONNÉES
        # ===============================
        data_oee = df[['📆date', '%OEE', '%performance', '% Availability']].copy()

        # Conversion en %
        data_oee['OEE (%)'] = data_oee['%OEE'] * 100
        data_oee['Performance (%)'] = data_oee['%performance'] * 100
        data_oee['Disponibilité (%)'] = data_oee['% Availability'] * 100

        data_oee = data_oee.dropna()

        # ===============================
        # 2️⃣ PERFORMANCE → OEE
        # ===============================
        x_perf = data_oee['Performance (%)']
        y_oee = data_oee['OEE (%)']

        coef_perf = np.polyfit(x_perf, y_oee, 1)
        corr_perf = np.corrcoef(x_perf, y_oee)[0, 1]
        r2_perf = corr_perf ** 2

        # ===============================
        # 3️⃣ DISPONIBILITÉ → OEE
        # ===============================
        x_disp = data_oee['Disponibilité (%)']

        coef_disp = np.polyfit(x_disp, y_oee, 1)
        corr_disp = np.corrcoef(x_disp, y_oee)[0, 1]
        r2_disp = corr_disp ** 2

        # ===============================
        # 4️⃣ VISUALISATION – PERFORMANCE
        # ===============================
        fig_perf = go.Figure()

        fig_perf.add_trace(go.Scatter(
            x=x_perf,
            y=y_oee,
            mode='markers',
            name='Performance vs OEE',
            marker=dict(size=10, opacity=0.7)
        ))

        x_line = np.linspace(x_perf.min(), x_perf.max(), 100)
        y_line = coef_perf[0] * x_line + coef_perf[1]

        fig_perf.add_trace(go.Scatter(
            x=x_line,
            y=y_line,
            mode='lines',
            name=f"Régression (coef={coef_perf[0]:.2f})",
            line=dict(dash='dash', width=3)
        ))

        fig_perf.update_layout(
            height=340,
            title='Influence de la Performance sur l’OEE',
            xaxis_title='Performance (%)',
            yaxis_title='OEE (%)',
            hovermode='closest'
        )

        st.plotly_chart(fig_perf, use_container_width=True)

        # ===============================
        # 5️⃣ VISUALISATION – DISPONIBILITÉ
        # ===============================
    with col3:
        fig_disp = go.Figure()

        fig_disp.add_trace(go.Scatter(
            x=x_disp,
            y=y_oee,
            mode='markers',
            name='Disponibilité vs OEE',
            marker=dict(size=10, opacity=0.7)
        ))

        x_line2 = np.linspace(x_disp.min(), x_disp.max(), 100)
        y_line2 = coef_disp[0] * x_line2 + coef_disp[1]

        fig_disp.add_trace(go.Scatter(
            x=x_line2,
            y=y_line2,
            mode='lines',
            name=f"Régression (coef={coef_disp[0]:.2f})",
            line=dict(dash='dash', width=3)
        ))

        fig_disp.update_layout(
            height=340,
            title='Influence de la Disponibilité sur l’OEE',
            xaxis_title='Disponibilité (%)',
            yaxis_title='OEE (%)',
            hovermode='closest'
        )

        st.plotly_chart(fig_disp, use_container_width=True)

        # ===============================
        # 6️⃣ KPIs SYNTHÈSE
        # ===============================
        k1, k2, k3 = st.columns(3)

        with k1:
            st.metric("📈 Pente Performance", f"{coef_perf[0]:.2f}", help="% OEE / % Performance")

        with k2:
            st.metric("📊 R² Performance", f"{r2_perf:.3f}", help="Pouvoir explicatif")

        with k3:
            st.metric("🔗 Corrélation Performance", f"{corr_perf:.3f}")

        k4, k5, k6 = st.columns(3)

        with k4:
            st.metric("📈 Pente Disponibilité", f"{coef_disp[0]:.2f}", help="% OEE / % Disponibilité")

        with k5:
            st.metric("📊 R² Disponibilité", f"{r2_disp:.3f}")

        with k6:
            st.metric("🔗 Corrélation Disponibilité", f"{corr_disp:.3f}")

        # ===============================
        # 7️⃣ CONCLUSION MÉTIER
        # ===============================
        st.markdown("##### 🧠 Lecture industrielle")

        st.info(
            f"🔹 La **Performance** explique **{r2_perf*100:.1f}%** de la variabilité de l’OEE.\n\n"
            f"🔹 La **Disponibilité** explique **{r2_disp*100:.1f}%** de la variabilité de l’OEE.\n\n"
            f"👉 Le levier prioritaire d’amélioration est celui ayant le **R² le plus élevé**."
        )


# ============================================================
# 🛠️ PAGE MAINTENANCE
# ============================================================

elif page == "maintenance":
    st.markdown("<h1 style='text-align: center;'>🛠️ Maintenance - Analyse des Pannes</h1>", unsafe_allow_html=True)
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        downtime_total = df['maintenance downtime'].sum() * 24
        st.metric("⏱️ Temps d'Arrêt Total", f"{downtime_total:.1f}h")
    
    with col2:
        meca_down = df['Mechanical downtime'].sum() * 24
        st.metric("🔧 Pannes Mécaniques", f"{meca_down:.1f}h")
    
    with col3:
        elec_down = df['Electrical downtime'].sum() * 24
        st.metric("⚡ Pannes Électriques", f"{elec_down:.1f}h")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔝 Top Équipements en Panne")
        pannes = df['Equipment failure 01'].value_counts().head(10).reset_index()
        pannes.columns = ['Équipement', 'Nombre']
        fig = px.bar(pannes, x='Nombre', y='Équipement', 
                    orientation='h', color='Nombre',
                    color_continuous_scale='Reds')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("📊 Types d'Arrêts")
        downtime_types = pd.DataFrame({
            'Type': ['Mécanique', 'Électrique', 'Nettoyage', 'Manque MP', 'Chargement'],
            'Heures': [
                df['Mechanical downtime'].sum() * 24,
                df['Electrical downtime'].sum() * 24,
                df['stock removal / factory cleaning work'].sum() * 24,
                df['lack of RM'].sum() * 24,
                df['NAVIRE LOADING EXPORT'].sum() * 24
            ]
        })
        fig = px.pie(downtime_types, values='Heures', names='Type')
        st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("📅 Évolution Temps d'Arrêt")
    downtime_daily = df.groupby('📆date')[['maintenance downtime', 'Mechanical downtime', 'Electrical downtime']].sum().reset_index()
    downtime_daily[['maintenance downtime', 'Mechanical downtime', 'Electrical downtime']] *= 24
    
    fig = go.Figure()
    fig.add_trace(go.Bar(x=downtime_daily['📆date'], y=downtime_daily['maintenance downtime'],
                        name='Total', marker_color='#667eea'))
    fig.add_trace(go.Bar(x=downtime_daily['📆date'], y=downtime_daily['Mechanical downtime'],
                        name='Mécanique', marker_color='#f5576c'))
    fig.add_trace(go.Bar(x=downtime_daily['📆date'], y=downtime_daily['Electrical downtime'],
                        name='Électrique', marker_color='#4facfe'))
    fig.update_layout(barmode='group', height=400, yaxis_title='Heures')
    st.plotly_chart(fig, use_container_width=True)

# ============================================================
# 📅 PAGE DATA RANGE
# ============================================================

elif page == "datarange":
    st.markdown("<h1 style='text-align: center;'>📅 Data Range - Filtrage</h1>", unsafe_allow_html=True)
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        date_debut = st.date_input("📅 Date début", value=df['📆date'].min())
    
    with col2:
        date_fin = st.date_input("📅 Date fin", value=df['📆date'].max())
    
    with col3:
        shifts = df['🛄 shift'].unique().tolist()
        shift_sel = st.multiselect("🛄 Shift", shifts, default=shifts)
    
    operateurs = df['Operator 👷‍♂️:'].unique().tolist()
    op_sel = st.multiselect("👷‍♂️ Opérateur", operateurs, default=operateurs)
    
    df_filtre = df[
        (df['📆date'] >= pd.to_datetime(date_debut)) &
        (df['📆date'] <= pd.to_datetime(date_fin)) &
        (df['🛄 shift'].isin(shift_sel)) &
        (df['Operator 👷‍♂️:'].isin(op_sel))
    ]
    
    st.markdown(f"### 📊 Résultats : {len(df_filtre)} lignes")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🏭 Production", f"{format_number_full(df_filtre['Total Prod ( RM consumption ) \"ton\"'].sum())} T")
    
    with col2:
        st.metric("🎯 OEE Moyen", f"{df_filtre['%OEE'].mean()*100:.1f}%")
    
    with col3:
        st.metric("⚡ Taux Prod.", f"{df_filtre['Production Rate t/h'].mean():.1f} T/h")
    
    with col4:
        st.metric("⏱️ Temps Arrêt", f"{df_filtre['maintenance downtime'].sum()*24:.1f}h")
    
    st.markdown("### 📋 Données Filtrées")
    st.dataframe(df_filtre, use_container_width=True, height=400)
    
    csv = df_filtre.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Télécharger CSV",
        data=csv,
        file_name=f'export_ncc2_{date_debut}_{date_fin}.csv',
        mime='text/csv',
    )

elif page == "logout":
    st.session_state.start_time = None
    st.session_state.page = "overview"
    st.rerun()