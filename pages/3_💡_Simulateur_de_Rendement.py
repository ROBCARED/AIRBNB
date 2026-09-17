import streamlit as st
import pandas as pd
import numpy as np
import os

st.set_page_config(page_title="Simulateur de Rendement", page_icon="💡", layout="wide")

@st.cache_data
def load_data():
    parquet_path = "data/listings_clean.parquet"
    csv_path = "data/listings_clean.csv"
    if os.path.exists(parquet_path):
        return pd.read_parquet(parquet_path)
    return pd.read_csv(csv_path)

df = load_data()

st.title("💡 Simulateur d'Investissement Locatif Airbnb")
st.markdown("> **Outil d'Aide à la Décision :** Simulez le potentiel de revenus d'un bien selon sa localisation et ses caractéristiques à Paris.")

st.markdown("<br>", unsafe_allow_html=True)

# Formulaire interactif
col_form, col_res = st.columns([1, 1.2])

with col_form:
    st.subheader("🛠️ Caractéristiques du Bien")
    
    selected_arr = st.selectbox("Arrondissement visé", sorted(df['neighbourhood_clean'].unique()))
    selected_type = st.selectbox("Type de bien", df['room_type'].unique())
    selected_bedrooms = st.slider("Nombre de chambres", min_value=1, max_value=5, value=1)
    target_superhost = st.radio("Visez-vous le statut Superhost ?", ["Oui ⭐", "Non"], index=0)
    target_rating = st.slider("Note de satisfaction visée (/5)", min_value=4.0, max_value=5.0, value=4.8, step=0.1)

# Calcul des prédictions basées sur le sous-échantillon filtré
df_sim = df[
    (df['neighbourhood_clean'] == selected_arr) &
    (df['room_type'] == selected_type) &
    (df['bedrooms_clean'] == selected_bedrooms)
]

# Fallback si l'échantillon exact est petit
if len(df_sim) < 5:
    df_sim = df[
        (df['neighbourhood_clean'] == selected_arr) &
        (df['room_type'] == selected_type)
    ]

# Métriques prédites
price_pred = df_sim['price'].median()
rev_base = df_sim['estimated_revenue_l365d'].median()

# Ajustements selon statut superhost et rating
superhost_multiplier = 1.15 if target_superhost == "Oui ⭐" else 1.0
rating_multiplier = 1.0 + (target_rating - 4.5) * 0.1
rev_final = rev_base * superhost_multiplier * rating_multiplier
occ_pred = min(95.0, df_sim['occupancy_rate_pct'].mean() * (1.1 if target_superhost=="Oui ⭐" else 1.0))

with col_res:
    st.subheader("📈 Estimation du Potentiel Locatif")
    
    st.markdown(f"""
    <div style="background-color: #1E293B; border-radius: 12px; padding: 24px; border: 1px solid #334155;">
        <h3 style="color: #FF385C; margin-top:0;">Résultats de la Simulation</h3>
        <p style="font-size: 1.1rem; color: #94A3B8;">Basé sur {len(df_sim)} logements comparables dans {selected_arr}.</p>
        <hr style="border-color: #334155;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 16px;">
            <span style="font-weight: 600; color: #F8FAFC;">💰 Prix par nuit recommandé :</span>
            <span style="font-size: 1.4rem; font-weight: 700; color: #10B981;">{price_pred:.0f} € / nuit</span>
        </div>
        <div style="display: flex; justify-content: space-between; margin-bottom: 16px;">
            <span style="font-weight: 600; color: #F8FAFC;">📅 Taux d'occupation estimé :</span>
            <span style="font-size: 1.4rem; font-weight: 700; color: #38BDF8;">{occ_pred:.1f} %</span>
        </div>
        <div style="display: flex; justify-content: space-between; margin-bottom: 16px;">
            <span style="font-weight: 600; color: #F8FAFC;">🏆 Revenu Annuel Estimé :</span>
            <span style="font-size: 1.8rem; font-weight: 800; color: #FF385C;">{rev_final:,.0f} € / an</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.info(f"""
    💡 **Recommandation Stratégique pour {selected_arr} :**  
    Pour ce type de bien, la stratégie idéale est d'imposer une durée de séjour minimale de **2 à 3 nuits** pendant les périodes de haute saison et de proposer la réservation instantanée (*Instant Book*) pour gagner jusqu'à **+15% d'occupation supplémentaire**.
    """)
