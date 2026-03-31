# 🏦 Impact de la Libéralisation du Régime de Change sur l’Économie Marocaine
Projet Fil Rouge Data Analyst – Analyse de l’impact de la libéralisation du régime de change sur l’économie marocaine
---

## 📌 Contexte

En janvier 2018, **Bank Al-Maghrib** a initié une réforme progressive du régime de change marocain, en élargissant la bande de fluctuation du dirham.

Cette transition d’un régime quasi-fixe vers un régime plus flexible vise à :

- Renforcer la résilience macroéconomique  
- Améliorer la compétitivité extérieure  
- Atténuer les chocs externes  
- Favoriser l’intégration financière internationale  

Cette réforme constitue un tournant majeur dans la politique monétaire du Maroc.

---

## 🎯 Problématique

> Quel a été l’impact de la libéralisation du régime de change sur les principaux indicateurs macroéconomiques marocains ?

---

## 🎯 Objectifs du projet

- Analyser l’évolution des indicateurs macroéconomiques avant et après 2018  
- Étudier la dynamique du taux de change (USD/MAD, EUR/MAD)  
- Examiner l’effet sur :
  - L’inflation  
  - Les IDE  
  - Les réserves de change  
  - Le commerce extérieur  
  - Le marché financier  
- Préparer une base pour une analyse économétrique  

---

## 🌍 Périmètre de l’étude

- **Pays principal :** Maroc 🇲🇦  
- **Période étudiée :** 2010 – 2025  
- **Date clé :** Janvier 2018 (début de la libéralisation)

### Extension prévue :

Comparaison avec 3 à 5 pays émergents ayant des régimes de change différents.

---

## 📊 Variables étudiées

- Taux de change (USD/MAD, EUR/MAD)  
- Inflation (IPC)  
- Investissements Directs Étrangers (IDE)  
- Réserves de change  
- Commerce extérieur (Exportations / Importations)  
- Indicateurs macroéconomiques de contrôle  
- Indice boursier MASI  

---

## 🏛 Sources de données

Les données proviennent de sources officielles :

- Bank Al-Maghrib  
- World Bank  
- International Monetary Fund  
- Office des Changes  
- Haut-Commissariat au Plan  

---

## 🗂 Structure du projet
```
project_root/
│
├── data/
│   │
│   ├── raw/                  # Données brutes (jamais modifiées)
│   │   ├── maroc/
│   │   │   ├── Taux de change/
│   │   │   ├── inflation/
│   │   │   ├── import et export(ice)/
│   │   │   ├── investissement_etrangers(ide)/
│   │   │   ├── Réserves de change/
│   │   │   ├── Macroeconomic control/
│   │   │   └── donnees financières et de marché/
│   │   │
│   │   ├── pays2/
│   │   ├── pays3/
│   │   └── ...
│   │
│   ├── interim/              # Données structurées mais non finales
│   │   ├── maroc/
│   │   ├── pays2/
│   │   └── ...
│   │
│   ├── processed/            # Données prêtes pour analyse
│   │   
│   └── external/             # PDFs, documentation, régimes, notes
│
├── notebooks/                # EDA & analyses
├── scripts/                  # Scripts python
├── outputs/                  # Graphiques, résultats
└── reports/                  # Cahier de charge, raport de projet, presentation
```

Organisation par pays puis par catégorie :

- exchange_rate  
- inflation  
- trade  
- fdi  
- reserves  
- macro  
- market  

---

## 🧪 Méthodologie

1. Nettoyage et harmonisation des données  
2. Analyse exploratoire (EDA)  
3. Comparaison pré- et post-2018  
4. Construction d’un dataset panel  
5. Modélisation économétrique (à venir)  

