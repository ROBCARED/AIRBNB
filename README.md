# 🏠 Dashboard Airbnb Paris — Où et comment investir ?

Tableau de bord interactif réalisé en équipe pour aider les **investisseurs immobiliers** et les **conciergeries** à choisir où et comment investir dans la location courte durée à Paris, à partir d'environ 48 000 annonces Airbnb.

## Message clé

> Pour maximiser la rentabilité, privilégier un **appartement entier de 1 à 2 chambres** dans le cœur touristique (Élysée, Louvre, Luxembourg) : revenu médian annuel estimé d'environ **31 500 €**, soit **+85 %** par rapport à la moyenne parisienne, à condition d'obtenir le statut Superhost et une note supérieure à 4,7/5.

La démarche complète (audience, choix des KPI, structure en pyramide de Minto) est décrite dans [`cadrage.md`](cadrage.md).

## Pages du dashboard

| Page | Contenu |
|---|---|
| **Accueil** | Message clé et indicateurs principaux |
| 📊 **Quartiers & rentabilité** | Matrice de positionnement des 20 arrondissements, distribution des revenus, tableau récapitulatif |
| ⭐ **Facteurs de succès & Superhost** | Lien entre note et revenu, poids des sous-critères de satisfaction |
| 💡 **Simulateur de rendement** | Estimation du revenu selon l'arrondissement, le type de bien, le nombre de chambres et la note visée |

## Stack

Python · Pandas · Plotly · Streamlit · Parquet

## Lancer le projet

```bash
pip install -r requirements.txt
streamlit run app.py
```

Les données nettoyées sont dans `data/listings_clean.parquet`.
