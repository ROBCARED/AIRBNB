# 📄 Document de Cadrage — Dashboard Airbnb Paris

> **Auteurs :** Équipe de projet (Bachelor Data & IA — MD4)  
> **Module :** Dashboards & Data Visualisation  
> **Date de rendu :** Jeudi 17 septembre 2026  

---

## 🎯 1. Le Message Clé (Principe de la Pyramide de Minto)

> [!IMPORTANT]
> **Message Clé :**  
> *"Pour maximiser la rentabilité d'un investissement locatif Airbnb à Paris, privilégier un appartement entier meublé de 1 à 2 chambres dans le cœur hyper-touristique (Élysée, Louvre, Luxembourg) génère un revenu médian annuel de **31 500 €** (+85 % vs moyenne parisienne), à condition d'obtenir le statut Superhost et de maintenir une note de satisfaction supérieure à 4.7/5."*

---

## 👥 2. Audience Cible

L'audience cible est constituée d'**investisseurs immobiliers particuliers** et de **gestionnaires de conciergerie locative à Paris**.  
Ces décideurs ont besoin d'arbitrer rapidement entre plusieurs opportunités d'achat/gestion et de définir une stratégie tarifaire compétitive basée sur des données réelles et géolocalisées.

---

## 📊 3. Sélection des KPIs : Vanity vs Actionable

Pour garantir des prises de décision concrètes et éviter les "vanity metrics" qui n'apportent aucune valeur stratégique, nous avons sélectionné 3 KPIs principaux :

| KPI Retenu | Type | Justification & Actionnabilité | Benchmark / Contextualisation |
| :--- | :--- | :--- | :--- |
| **1. Revenu Médian Annuel Estimé (€)** | 🟢 **Actionable** | Mesure l'efficacité financière réelle d'un bien sur 12 mois. Permet d'évaluer le retour sur investissement (ROI) potentiel avant acquisition. *(vs Vanity : Nombre total de logements sur le marché).* | Comparé au **Benchmark Global Paris** (Revenu Médian = 17 000 €). |
| **2. Prix Moyen Nuitée (€/nuit)** | 🟢 **Actionable** | Indique le positionnement tarifaire optimal selon l'arrondissement et la taille du bien pour maximiser la marge sans dégrader la demande. *(vs Vanity : Nombre de vues ou de favoris).* | Comparé à la **moyenne sectorielle** du quartier sélectionné. |
| **3. Taux d'Occupation Annuel (%)** | 🟢 **Actionable** | Évalue la régularité du taux de remplissage et la tension locative. Permet d'ajuster les règles de durée minimale de séjour (`minimum_nights`). *(vs Vanity : Nombre total d'avis déposés).* | Comparé au **taux moyen parisien** (~63%). |

---

## 🏗️ 4. Structure et Architecture du Dashboard Streamlit

L'application adopte une **structure multi-pages** (`app.py` + dossier `pages/`) afin de respecter le principe de hiérarchie de l'information (du macro au micro) et de limiter la charge cognitive.

```
┌────────────────────────────────────────────────────────────────────────┐
│ 🎚️ SIDEBAR FILTRES : Arrondissements, Typologie, Prix/nuit, Superhost │
├────────────────────────────────────────────────────────────────────────┤
│ 💡 TITRE MESSAGE : Maximiser la rentabilité locative Airbnb à Paris    │
├────────────────────────────────────────────────────────────────────────┤
│ 📌 ZONE KPIs (3 cartes métriques avec badges Delta vs Benchmark)       │
├────────────────────────────────────────────────────────────────────────┤
│ 🗺️ ZONE SYNTHÈSE : Carte interactive Mapbox & distribution revenus    │
├────────────────────────────────────────────────────────────────────────┤
│ 📑 PAGES SPÉCIALISÉES (Navigation)                                      │
│   ├─ 📊 Vue 1 : Analyse des Quartiers & Rentabilité                    │
│   ├─ ⭐ Vue 2 : Facteurs de Succès & Effet Superhost                   │
│   └─ 💡 Vue 3 : Simulateur d'Investissement Personnalisé              │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 🎨 5. Canaux Pré-attentifs et Justification des Graphiques

Chaque visualisation a été choisie spécifiquement pour exploiter la mémoire pré-attentive (assimilation visuelle en moins de 5 secondes) tout en garantissant une stricte **honnêteté visuelle** :

1. **Cartographie Interactive (Scatter Map Plotly)** :
   - *Canal pré-attentif :* Position géographique (longitude/latitude) + **Couleur (Gradient de prix/revenu)**.
   - *Rôle :* Identifier immédiatement les grappes de haute valeur locative dans le centre de Paris.
2. **Bar Chart Horizontal Trié (Prix & Revenu par Quartier)** :
   - *Canal pré-attentif :* Longueur et alignement.
   - *Rôle :* Faciliter la comparaison directe des 20 arrondissements sans imposer d'effort de lecture (tri par ordre décroissant, axe Y démarrant à 0).
3. **Scatter Plot réactif (Qualité / Note vs Prix par nuit)** :
   - *Canal pré-attentif :* Position sur axe X/Y + Couleur par statut **Superhost**.
   - *Rôle :* Détecter la "zone d'excellence" (hautes notes, prix élevés) et valider la prime financière accordée aux hôtes certifiés.
4. **Histogramme & Distribution (Boxplot/Violin)** :
   - *Canal pré-attentif :* Dispersion et étalement des données.
   - *Rôle :* Éviter le piège de la "moyenne trompeuse" en affichant les quartiles et la médiane réelle des revenus locatifs.

---

## ⚙️ 6. Optimisations Techniques

- **Données optimisées (`.parquet`) :** Compression de 181 Mo à 3,1 Mo avec encodage strict UTF-8 et typage optimisé des variables.
- **Mise en cache (`@st.cache_data`) :** Exécution instantanée des filtres et temps de chargement initial < 100 ms.
- **Design System responsive :** Palette sombre élégante (Thème Dark Slate `#0F172A`, rouge Airbnb `#FF385C`, cartes glassmorphism).
