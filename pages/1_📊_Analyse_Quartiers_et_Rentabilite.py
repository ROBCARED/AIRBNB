import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os

st.set_page_config(page_title="Analyse Quartiers & Rentabilité", page_icon="📊", layout="wide")

@st.cache_data
def load_data():
    parquet_path = "data/listings_clean.parquet"
    csv_path = "data/listings_clean.csv"
    if os.path.exists(parquet_path):
        return pd.read_parquet(parquet_path)
    return pd.read_csv(csv_path)

df = load_data()

st.title("📊 Analyse Approfondie des Quartiers & Rentabilité")
st.markdown("> **Objectif :** Identifier les arrondissements de Paris offrant le meilleur couple *Revenu Annuel / Taux d'Occupation*.")

# Sidebar local filters
st.sidebar.title("🎚️ Filtres de la Vue")
selected_rooms = st.sidebar.multiselect("Typologie de bien", df['room_type'].unique(), default=df['room_type'].unique())
selected_bedrooms = st.sidebar.multiselect("Nombre de chambres", df['bedrooms_label'].unique(), default=df['bedrooms_label'].unique())

df_view = df[(df['room_type'].isin(selected_rooms)) & (df['bedrooms_label'].isin(selected_bedrooms))]

# Section 1 : Matrice de Performance Quartiers (Scatter Prix vs Occupancy vs Revenu)
st.subheader("🎯 Matrice de Positionnement des 20 Arrondissements")
st.caption("Axe X = Prix nuitée moyen, Axe Y = Taux d'occupation moyen, Taille/Couleur = Revenu annuel médian.")

agg_arr = df_view.groupby('neighbourhood_clean').agg(
    prix_moyen=('price', 'median'),
    occupation_moyenne=('occupancy_rate_pct', 'mean'),
    revenu_median=('estimated_revenue_l365d', 'median'),
    nombre_logements=('id', 'count')
).reset_index()

fig_scatter = px.scatter(
    agg_arr,
    x='prix_moyen',
    y='occupation_moyenne',
    size='revenu_median',
    color='revenu_median',
    text='neighbourhood_clean',
    color_continuous_scale='Turbo',
    hover_name='neighbourhood_clean',
    labels={
        'prix_moyen': 'Prix Médian Nuitée (€)',
        'occupation_moyenne': "Taux d'Occupation Moyen (%)",
        'revenu_median': 'Revenu Annuel Médian (€)'
    },
    title="Rentabilité vs Tension Locative par Quartier"
)
fig_scatter.update_traces(textposition='top center')
fig_scatter.update_layout(
    height=550,
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#F8FAFC"),
    xaxis=dict(gridcolor="#334155"),
    yaxis=dict(gridcolor="#334155")
)
st.plotly_chart(fig_scatter, use_container_width=True)

# Section 2 : Distribution des Revenus par Arrondissement (Boxplot pour éviter l'effet moyenne)
st.subheader("📦 Distribution Réelle des Revenus (Boxplot par Arrondissement)")
st.caption("Permet d'observer la dispersion des revenus réels et d'éviter l'illusion des valeurs moyennes.")

top_arr_list = agg_arr.sort_values(by='revenu_median', ascending=False)['neighbourhood_clean'].tolist()

box_data = df_view[df_view['neighbourhood_clean'].isin(top_arr_list[:10])]
if len(box_data) > 5000:
    box_data = box_data.sample(5000, random_state=42)

fig_box = px.box(
    box_data,
    x='neighbourhood_clean',
    y='estimated_revenue_l365d',
    color='neighbourhood_clean',
    labels={'neighbourhood_clean': 'Quartier', 'estimated_revenue_l365d': 'Revenu Annuel (€)'},
    title="Dispersion des Revenus dans le Top 10 des Quartiers"
)
fig_box.update_layout(
    height=480,
    showlegend=False,
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#F8FAFC"),
    yaxis=dict(gridcolor="#334155", range=[0, df_view['estimated_revenue_l365d'].quantile(0.98)])
)
st.plotly_chart(fig_box, use_container_width=True, config={'displayModeBar': False})

# Section 3 : Tableau synthétique des Quartiers
st.subheader("📋 Tableau Récapitulatif des Métriques par Quartier")
st.dataframe(
    agg_arr.sort_values(by='revenu_median', ascending=False).style.format({
        'prix_moyen': '{:.0f} €',
        'occupation_moyenne': '{:.1f} %',
        'revenu_median': '{:,.0f} €',
        'nombre_logements': '{:,}'
    }),
    use_container_width=True
)
