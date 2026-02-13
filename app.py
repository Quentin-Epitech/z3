import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np

# Configuration de la page
st.set_page_config(
    page_title="Analyse Prix BMW Z3",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Titre principal
st.title("🚗 Analyse des Prix BMW Z3")
st.markdown("---")

# Chargement des données
@st.cache_data
def load_data():
    df = pd.read_csv('data.csv')
    
    # Conversion de la date au format datetime
    df['date_publication'] = pd.to_datetime(df['date_publication'], format='%d/%m/%Y')
    
    # Nettoyage des données
    df = df.dropna(subset=['prix_eur', 'date_publication'])
    
    return df

# Charger les données
try:
    df = load_data()
    
    # Sidebar - Filtres
    st.sidebar.header("🔍 Filtres")
    
    # Filtre par date de publication
    st.sidebar.subheader("Date de publication")
    date_min = df['date_publication'].min().date()
    date_max = df['date_publication'].max().date()
    
    date_range = st.sidebar.date_input(
        "Période",
        value=(date_min, date_max),
        min_value=date_min,
        max_value=date_max
    )
    
    # Filtre par année de fabrication
    st.sidebar.subheader("Année de fabrication")
    annee_min = int(df['annee'].min())
    annee_max = int(df['annee'].max())
    annee_range = st.sidebar.slider(
        "Année",
        min_value=annee_min,
        max_value=annee_max,
        value=(annee_min, annee_max)
    )
    
    # Filtre par kilométrage
    st.sidebar.subheader("Kilométrage")
    km_min = int(df['kilometrage_km'].min())
    km_max = int(df['kilometrage_km'].max())
    km_range = st.sidebar.slider(
        "Kilométrage (km)",
        min_value=km_min,
        max_value=km_max,
        value=(km_min, km_max),
        step=1000
    )
    
    # Filtre par prix
    st.sidebar.subheader("Prix")
    prix_min = int(df['prix_eur'].min())
    prix_max = int(df['prix_eur'].max())
    prix_range = st.sidebar.slider(
        "Prix (€)",
        min_value=prix_min,
        max_value=prix_max,
        value=(prix_min, prix_max),
        step=500
    )
    
    # Filtre par type de vendeur
    st.sidebar.subheader("Type de vendeur")
    type_vendeur = st.sidebar.multiselect(
        "Sélectionner",
        options=df['type_vendeur'].unique(),
        default=df['type_vendeur'].unique()
    )
    
    # Application des filtres
    df_filtered = df.copy()
    
    if len(date_range) == 2:
        df_filtered = df_filtered[
            (df_filtered['date_publication'].dt.date >= date_range[0]) &
            (df_filtered['date_publication'].dt.date <= date_range[1])
        ]
    
    df_filtered = df_filtered[
        (df_filtered['annee'] >= annee_range[0]) &
        (df_filtered['annee'] <= annee_range[1]) &
        (df_filtered['kilometrage_km'] >= km_range[0]) &
        (df_filtered['kilometrage_km'] <= km_range[1]) &
        (df_filtered['prix_eur'] >= prix_range[0]) &
        (df_filtered['prix_eur'] <= prix_range[1]) &
        (df_filtered['type_vendeur'].isin(type_vendeur))
    ]
    
    # Statistiques principales
    st.header("📊 Statistiques Clés")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Nombre d'annonces", len(df_filtered))
    
    with col2:
        st.metric("Prix moyen", f"{df_filtered['prix_eur'].mean():,.0f} €")
    
    with col3:
        st.metric("Prix médian", f"{df_filtered['prix_eur'].median():,.0f} €")
    
    with col4:
        st.metric("Kilométrage moyen", f"{df_filtered['kilometrage_km'].mean():,.0f} km")
    
    st.markdown("---")
    
    # Graphique principal : Prix en fonction du temps
    st.header("📈 Évolution des Prix au Fil du Temps")
    
    fig_time = px.scatter(
        df_filtered.sort_values('date_publication'),
        x='date_publication',
        y='prix_eur',
        color='type_vendeur',
        size='kilometrage_km',
        hover_data=['titre', 'annee', 'kilometrage_km', 'ville'],
        title="Prix des BMW Z3 par Date de Publication",
        labels={
            'date_publication': 'Date de Publication',
            'prix_eur': 'Prix (€)',
            'type_vendeur': 'Type de Vendeur',
            'kilometrage_km': 'Kilométrage (km)'
        },
        color_discrete_map={
            'particulier': '#3498db',
            'professionnel': '#e74c3c'
        }
    )
    
    # Ajouter une ligne de tendance
    if len(df_filtered) > 1:
        # Convertir les dates en nombres pour la régression
        df_filtered['date_num'] = (df_filtered['date_publication'] - df_filtered['date_publication'].min()).dt.days
        z = np.polyfit(df_filtered['date_num'], df_filtered['prix_eur'], 1)
        p = np.poly1d(z)
        
        fig_time.add_trace(
            go.Scatter(
                x=df_filtered.sort_values('date_publication')['date_publication'],
                y=p(df_filtered.sort_values('date_publication')['date_num']),
                mode='lines',
                name='Tendance',
                line=dict(color='green', width=2, dash='dash')
            )
        )
    
    fig_time.update_layout(
        height=500,
        hovermode='closest',
        showlegend=True
    )
    
    st.plotly_chart(fig_time, use_container_width=True)
    
    # Deuxième ligne de graphiques
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("💰 Prix vs Kilométrage")
        fig_km = px.scatter(
            df_filtered,
            x='kilometrage_km',
            y='prix_eur',
            color='annee',
            hover_data=['titre', 'ville', 'type_vendeur'],
            title="Relation Prix-Kilométrage",
            labels={
                'kilometrage_km': 'Kilométrage (km)',
                'prix_eur': 'Prix (€)',
                'annee': 'Année'
            },
            color_continuous_scale='Viridis'
        )
        fig_km.update_layout(height=400)
        st.plotly_chart(fig_km, use_container_width=True)
    
    with col2:
        st.subheader("📅 Distribution par Année")
        prix_par_annee = df_filtered.groupby('annee')['prix_eur'].agg(['mean', 'count']).reset_index()
        
        fig_annee = go.Figure()
        fig_annee.add_trace(
            go.Bar(
                x=prix_par_annee['annee'],
                y=prix_par_annee['mean'],
                name='Prix moyen',
                marker_color='#2ecc71',
                text=prix_par_annee['mean'].round(0),
                textposition='outside',
                hovertemplate='Année: %{x}<br>Prix moyen: %{y:,.0f}€<extra></extra>'
            )
        )
        
        fig_annee.update_layout(
            title="Prix Moyen par Année de Fabrication",
            xaxis_title="Année",
            yaxis_title="Prix Moyen (€)",
            height=400,
            showlegend=False
        )
        st.plotly_chart(fig_annee, use_container_width=True)
    
    # Distribution des prix
    st.header("📊 Distribution des Prix")
    
    fig_hist = px.histogram(
        df_filtered,
        x='prix_eur',
        nbins=20,
        title="Distribution des Prix",
        labels={'prix_eur': 'Prix (€)', 'count': 'Nombre d\'annonces'},
        color_discrete_sequence=['#9b59b6']
    )
    fig_hist.update_layout(height=400, showlegend=False)
    st.plotly_chart(fig_hist, use_container_width=True)
    
    # Tableau de données
    st.header("📋 Données Détaillées")
    
    # Préparer les données pour l'affichage
    df_display = df_filtered[[
        'titre', 'date_publication', 'annee', 'kilometrage_km', 
        'prix_eur', 'ville', 'type_vendeur', 'url'
    ]].copy()
    
    df_display['date_publication'] = df_display['date_publication'].dt.strftime('%d/%m/%Y')
    df_display = df_display.sort_values('date_publication', ascending=False)
    
    # Renommer les colonnes pour l'affichage
    df_display.columns = [
        'Titre', 'Date Publication', 'Année', 'Kilométrage (km)',
        'Prix (€)', 'Ville', 'Type Vendeur', 'URL'
    ]
    
    st.dataframe(
        df_display,
        use_container_width=True,
        hide_index=True,
        column_config={
            "URL": st.column_config.LinkColumn("Lien"),
            "Prix (€)": st.column_config.NumberColumn(
                "Prix (€)",
                format="%d €"
            ),
            "Kilométrage (km)": st.column_config.NumberColumn(
                "Kilométrage (km)",
                format="%d km"
            )
        }
    )
    
    # Informations supplémentaires
    st.markdown("---")
    st.info(f"📌 **{len(df_filtered)}** annonces affichées sur **{len(df)}** au total")
    
except FileNotFoundError:
    st.error("❌ Fichier 'data.csv' introuvable. Assurez-vous que le fichier est dans le même répertoire que l'application.")
except Exception as e:
    st.error(f"❌ Erreur lors du chargement des données : {str(e)}")
