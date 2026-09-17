import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os

# 1. Configuration de la page
st.set_page_config(
    page_title="Airbnb Paris — Optimisation Rentabilité",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Style CSS personnalisé pour les cartes KPI et l'esthétique générale
st.markdown("""
<style>
    .metric-card {
        background-color: #1E293B;
        border-radius: 12px;
        padding: 20px;
        border: 1px solid #334155;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .metric-title {
        color: #94A3B8;
        font-size: 0.9rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .metric-value {
        color: #F8FAFC;
        font-size: 1.8rem;
        font-weight: 700;
        margin-top: 4px;
    }
    .metric-delta {
        font-size: 0.85rem;
        font-weight: 600;
        margin-top: 6px;
    }
    .delta-positive { color: #10B981; }
    .delta-negative { color: #EF4444; }
    .minto-header {
        background: linear-gradient(135deg, #FF385C 0%, #E0245E 100%);
        color: white;
        padding: 24px;
        border-radius: 16px;
        margin-bottom: 24px;
        box-shadow: 0 10px 15px -3px rgba(255, 56, 92, 0.25);
    }
    .minto-header h1 {
        margin: 0;
        font-size: 2.1rem;
        font-weight: 800;
        color: #FFFFFF;
    }
    .minto-header p {
        margin-top: 8px;
        margin-bottom: 0;
        font-size: 1.1rem;
        opacity: 0.95;
    }
</style>
""", unsafe_allow_html=True)

# 2. Chargement des données avec mise en cache
@st.cache_data
def load_data():
    parquet_path = "data/listings_clean.parquet"
    csv_path = "data/listings_clean.csv"
    
    if os.path.exists(parquet_path):
        df = pd.read_parquet(parquet_path)
    elif os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
    else:
        st.error("❌ Fichier de données non trouvé dans data/. Veuillez exécuter prepare_data.py.")
        st.stop()
    return df

df = load_data()

@st.cache_data
def get_benchmarks_and_metadata(_df):
    b_rev = float(_df['estimated_revenue_l365d'].median())
    b_price = float(_df['price'].median())
    b_occ = float(_df['occupancy_rate_pct'].mean())
    
    # Extraction rapide sans boucles
    arr_meta = _df[['neighbourhood_clean', 'arrondissement_num']].drop_duplicates()
    arr_sorted = arr_meta.sort_values('arrondissement_num')['neighbourhood_clean'].tolist()
    return b_rev, b_price, b_occ, arr_sorted

BENCHMARK_REVENUE, BENCHMARK_PRICE, BENCHMARK_OCCUPANCY, arrondissements = get_benchmarks_and_metadata(df)

# 3. Sidebar — Filtres Interactifs
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/6/69/Airbnb_Logo_B%C3%A9lo.svg", width=140)
st.sidebar.title("🎚️ Filtres Stratégiques")

# Filtre 1 : Arrondissements
selected_arr = st.sidebar.multiselect(
    "📍 Arrondissement(s)",
    options=arrondissements,
    default=[],
    placeholder="Tous les arrondissements (par défaut)"
)

# Filtre 2 : Typologie de logement
room_types = list(df['room_type'].cat.categories if hasattr(df['room_type'], 'cat') else df['room_type'].unique())
selected_rooms = st.sidebar.multiselect(
    "🏠 Type de Logement",
    options=room_types,
    default=room_types
)

# Filtre 3 : Statut Superhost
superhost_options = list(df['host_is_superhost_label'].cat.categories if hasattr(df['host_is_superhost_label'], 'cat') else df['host_is_superhost_label'].unique())
selected_superhost = st.sidebar.multiselect(
    "⭐ Statut de l'Hôte",
    options=superhost_options,
    default=superhost_options
)

# Filtre 4 : Tranche de Prix Nuitée
min_p, max_p = int(df['price'].min()), int(df['price'].quantile(0.98))
selected_price_range = st.sidebar.slider(
    "💰 Prix par nuitée (€)",
    min_value=min_p,
    max_value=max_p,
    value=(min_p, max_p)
)

# Application des filtres
df_filtered = df[
    (df['room_type'].isin(selected_rooms)) &
    (df['host_is_superhost_label'].isin(selected_superhost)) &
    (df['price'] >= selected_price_range[0]) &
    (df['price'] <= selected_price_range[1])
]

if selected_arr:
    df_filtered = df_filtered[df_filtered['neighbourhood_clean'].isin(selected_arr)]

if len(df_filtered) == 0:
    st.warning("⚠️ Aucun logement ne correspond aux filtres sélectionnés. Veuillez élargir vos critères.")
    st.stop()

# 4. En-tête Principal — Pyramide de Minto
st.markdown("""
<div class="minto-header">
    <h1>🏠 Maximiser sa Rentabilité Airbnb à Paris</h1>
    <p>💡 <b>Message Clé :</b> Investir dans un appartement entier (1-2 chambres) dans le centre hyper-touristique (1er au 8e arrondissements) génère un revenu locatif médian jusqu'à <b>+85% supérieur</b> à la moyenne parisienne.</p>
</div>
""", unsafe_allow_html=True)

# 5. Zone KPIs (Contextualisés & Actionnables)
rev_median = df_filtered['estimated_revenue_l365d'].median()
price_median = df_filtered['price'].median()
occupancy_mean = df_filtered['occupancy_rate_pct'].mean()
total_listings = len(df_filtered)

diff_rev_pct = ((rev_median - BENCHMARK_REVENUE) / BENCHMARK_REVENUE) * 100
diff_price_pct = ((price_median - BENCHMARK_PRICE) / BENCHMARK_PRICE) * 100
diff_occ_pts = occupancy_mean - BENCHMARK_OCCUPANCY

c1, c2, c3, c4 = st.columns(4)

with c1:
    delta_class = "delta-positive" if diff_rev_pct >= 0 else "delta-negative"
    delta_sign = "+" if diff_rev_pct >= 0 else ""
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Revenu Médian Annuel</div>
        <div class="metric-value">{rev_median:,.0f} €</div>
        <div class="metric-delta {delta_class}">{delta_sign}{diff_rev_pct:.1f}% vs Paris Global ({BENCHMARK_REVENUE:,.0f} €)</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    delta_class = "delta-positive" if diff_price_pct >= 0 else "delta-negative"
    delta_sign = "+" if diff_price_pct >= 0 else ""
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Prix Médian Nuitée</div>
        <div class="metric-value">{price_median:.0f} € / nuit</div>
        <div class="metric-delta {delta_class}">{delta_sign}{diff_price_pct:.1f}% vs Paris Global ({BENCHMARK_PRICE:.0f} €)</div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    delta_class = "delta-positive" if diff_occ_pts >= 0 else "delta-negative"
    delta_sign = "+" if diff_occ_pts >= 0 else ""
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Taux d'Occupation Moy.</div>
        <div class="metric-value">{occupancy_mean:.1f}%</div>
        <div class="metric-delta {delta_class}">{delta_sign}{diff_occ_pts:.1f} pts vs Paris Global ({BENCHMARK_OCCUPANCY:.1f}%)</div>
    </div>
    """, unsafe_allow_html=True)

with c4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Volume de Logements</div>
        <div class="metric-value">{total_listings:,}</div>
        <div class="metric-delta" style="color: #94A3B8;">Échantillon filtré disponible</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# 6. Zone Graphiques & Analyse Visuelle
col_left, col_right = st.columns([1.1, 0.9])

with col_left:
    st.subheader("🗺️ Cartographie de la Rentabilité Locative par Logement")
    st.caption("Chaque point représente un logement Airbnb. La couleur indique le niveau de revenu annuel estimé.")
    
    # Sous-échantillon optimisé à 1000 points pour un rendu fluide à 60fps
    map_sample = df_filtered.sample(min(1000, len(df_filtered)), random_state=42)
    
    map_func = getattr(px, 'scatter_map', getattr(px, 'scatter_mapbox', None))
    style_param = 'map_style' if hasattr(px, 'scatter_map') else 'mapbox_style'
    
    map_kwargs = {
        "lat": "latitude",
        "lon": "longitude",
        "color": "estimated_revenue_l365d",
        "size": "price",
        "color_continuous_scale": "Plasma",
        "size_max": 12,
        "zoom": 11.2,
        "center": {"lat": 48.8566, "lon": 2.3522},
        style_param: "carto-darkmatter",
        "hover_name": "name",
        "hover_data": {
            "neighbourhood_clean": True,
            "room_type": True,
            "price": ":.0f€",
            "estimated_revenue_l365d": ":.0f€",
            "review_scores_rating": ":.2f",
            "latitude": False,
            "longitude": False
        },
        "labels": {
            "estimated_revenue_l365d": "Revenu Annuel (€)",
            "price": "Prix (€)",
            "neighbourhood_clean": "Quartier"
        }
    }
    
    fig_map = map_func(map_sample, **map_kwargs)
    fig_map.update_layout(
        margin={"r":0,"t":0,"l":0,"b":0},
        height=480,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )
    st.plotly_chart(fig_map, use_container_width=True, config={'displayModeBar': False})

with col_right:
    st.subheader("📊 Top Quartiers par Revenu Annuel Médian (€)")
    st.caption("Comparaison des revenus médiaux par arrondissement selon les filtres actifs.")
    
    arr_summary = df_filtered.groupby('neighbourhood_clean').agg(
        rev_median=('estimated_revenue_l365d', 'median'),
        count=('id', 'count')
    ).reset_index().sort_values(by='rev_median', ascending=True)
    
    fig_bar = px.bar(
        arr_summary,
        x='rev_median',
        y='neighbourhood_clean',
        orientation='h',
        color='rev_median',
        color_continuous_scale='Reds',
        text_auto='.0f',
        labels={'rev_median': 'Revenu Médian (€)', 'neighbourhood_clean': 'Quartier'}
    )
    fig_bar.update_layout(
        height=480,
        showlegend=False,
        coloraxis_showscale=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#F8FAFC"),
        xaxis=dict(gridcolor="#334155", title="Revenu Médian Annuel (€)"),
        yaxis=dict(title="")
    )
    st.plotly_chart(fig_bar, use_container_width=True)

# 7. Deuxième rangée de visualisations
c_b1, c_b2 = st.columns(2)

with c_b1:
    st.subheader("🏠 Revenu & Prix selon la Typologie de Logement")
    room_summary = df_filtered.groupby('room_type').agg(
        rev_median=('estimated_revenue_l365d', 'median'),
        price_median=('price', 'median'),
        count=('id', 'count')
    ).reset_index()
    
    fig_room = px.bar(
        room_summary,
        x='room_type',
        y='rev_median',
        color='room_type',
        color_discrete_sequence=['#FF385C', '#38BDF8', '#F59E0B', '#10B981'],
        text_auto='.0f',
        title="Revenu Médian Annuel par Type de Chambre (€)",
        labels={'room_type': 'Type', 'rev_median': 'Revenu Médian (€)'}
    )
    fig_room.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#F8FAFC"),
        showlegend=False,
        yaxis=dict(gridcolor="#334155")
    )
    st.plotly_chart(fig_room, use_container_width=True)

with c_b2:
    st.subheader("⭐ Impact du Statut Superhost sur la Rentabilité")
    sh_summary = df_filtered.groupby('host_is_superhost_label').agg(
        rev_median=('estimated_revenue_l365d', 'median'),
        occupancy_mean=('occupancy_rate_pct', 'mean'),
        rating_mean=('review_scores_rating', 'mean')
    ).reset_index()
    
    fig_sh = px.bar(
        sh_summary,
        x='host_is_superhost_label',
        y='rev_median',
        color='host_is_superhost_label',
        color_discrete_sequence=['#10B981', '#64748B', '#F59E0B'],
        text_auto='.0f',
        title="Surprime de Revenu du Statut Superhost (€/an)",
        labels={'host_is_superhost_label': 'Statut Hôte', 'rev_median': 'Revenu Médian (€)'}
    )
    fig_sh.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#F8FAFC"),
        showlegend=False,
        yaxis=dict(gridcolor="#334155")
    )
    st.plotly_chart(fig_sh, use_container_width=True)

# 8. Explorateur de données brutes
with st.expander("🔍 Explorer l'Échantillon de Données Filtrées"):
    st.dataframe(
        df_filtered[['name', 'neighbourhood_clean', 'room_type', 'price', 'estimated_revenue_l365d', 'occupancy_rate_pct', 'host_is_superhost_label', 'review_scores_rating']].head(100),
        use_container_width=True
    )