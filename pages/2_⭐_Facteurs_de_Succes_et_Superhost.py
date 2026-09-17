import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os

st.set_page_config(page_title="Facteurs de Succès & Superhost", page_icon="⭐", layout="wide")

@st.cache_data
def load_data():
    parquet_path = "data/listings_clean.parquet"
    csv_path = "data/listings_clean.csv"
    if os.path.exists(parquet_path):
        return pd.read_parquet(parquet_path)
    return pd.read_csv(csv_path)

df = load_data()

st.title("⭐ Facteurs de Succès & Effet Superhost")
st.markdown("> **Objectif :** Mesurer l'impact des notes de satisfaction et du statut Superhost sur le chiffre d'affaires annuel.")

# Filtre rapide
st.sidebar.title("🎚️ Filtres")
selected_superhost = st.sidebar.multiselect("Statut Hôte", df['host_is_superhost_label'].unique(), default=df['host_is_superhost_label'].unique())

df_view = df[df['host_is_superhost_label'].isin(selected_superhost)]

# Section 1 : Comparatif Superhost vs Hôte Classique
c1, c2, c3 = st.columns(3)

sh_rev = df[df['host_is_superhost_label']=='Superhost ⭐']['estimated_revenue_l365d'].median()
cl_rev = df[df['host_is_superhost_label']=='Hôte Classique']['estimated_revenue_l365d'].median()
diff_sh_pct = ((sh_rev - cl_rev) / cl_rev) * 100

with c1:
    st.metric("Revenu Médian Superhost", f"{sh_rev:,.0f} €", delta=f"+{diff_sh_pct:.1f}% vs Hôte classique")
with c2:
    sh_rating = df[df['host_is_superhost_label']=='Superhost ⭐']['review_scores_rating'].mean()
    cl_rating = df[df['host_is_superhost_label']=='Hôte Classique']['review_scores_rating'].mean()
    st.metric("Note Moyenne Superhost", f"{sh_rating:.2f} / 5", delta=f"+{sh_rating - cl_rating:.2f} pts")
with c3:
    sh_occ = df[df['host_is_superhost_label']=='Superhost ⭐']['occupancy_rate_pct'].mean()
    cl_occ = df[df['host_is_superhost_label']=='Hôte Classique']['occupancy_rate_pct'].mean()
    st.metric("Taux d'Occupation Superhost", f"{sh_occ:.1f}%", delta=f"+{sh_occ - cl_occ:.1f} pts")

st.markdown("<br>", unsafe_allow_html=True)

# Section 2 : Impact de la Note Globale sur les Revenus
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("📈 Note Globale vs Revenu Médian (€)")
    # Groupement des notes par tranches
    df_view['rating_bin'] = pd.cut(
        df_view['review_scores_rating'],
        bins=[0, 4.0, 4.5, 4.75, 4.9, 5.0],
        labels=['< 4.0', '4.0 - 4.5', '4.5 - 4.75', '4.75 - 4.9', '4.9 - 5.0']
    )
    
    rating_summary = df_view.groupby('rating_bin', observed=False)['estimated_revenue_l365d'].median().reset_index()
    
    fig_rating = px.bar(
        rating_summary,
        x='rating_bin',
        y='estimated_revenue_l365d',
        color='estimated_revenue_l365d',
        color_continuous_scale='Viridis',
        text_auto='.0f',
        title="Revenu Médian selon la Tranche de Note",
        labels={'rating_bin': 'Note Globale', 'estimated_revenue_l365d': 'Revenu Médian (€)'}
    )
    fig_rating.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#F8FAFC"),
        coloraxis_showscale=False,
        yaxis=dict(gridcolor="#334155")
    )
    st.plotly_chart(fig_rating, use_container_width=True, config={'displayModeBar': False})

with col_right:
    st.subheader("🧩 Importance des Sous-Critères de Satisfaction")
    
    sub_scores = ['review_scores_cleanliness', 'review_scores_location', 'review_scores_value', 'review_scores_communication', 'review_scores_checkin']
    means = [df_view[col].mean() for col in sub_scores]
    labels = ['Propreté', 'Emplacement', 'Rapport Q/P', 'Communication', 'Check-in']
    
    fig_radar = go.Figure(data=go.Scatterpolar(
      r=means,
      theta=labels,
      fill='toself',
      marker_color='#FF385C'
    ))
    fig_radar.update_layout(
      polar=dict(radialaxis=dict(visible=True, range=[4.0, 5.0])),
      showlegend=False,
      title="Profil Moyen de Satisfaction des Logements",
      paper_bgcolor="rgba(0,0,0,0)",
      font=dict(color="#F8FAFC")
    )
    st.plotly_chart(fig_radar, use_container_width=True, config={'displayModeBar': False})
