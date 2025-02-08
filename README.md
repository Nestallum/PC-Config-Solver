# Configurateur de PC avec CSP

## Description
Ce projet est un configurateur interactif de PC qui garantit la compatibilité des composants à l’aide d’un **problème de satisfaction de contraintes (CSP)**. Deux approches sont proposées :
- Une approche utilisant un **solveur CSP** (bibliothèque `python-constraint`).
- Une approche basée sur la **propagation de contraintes (MAC)**, optimisée pour un processus interactif.

## Approches utilisées

### 1️⃣ Approche avec Solveur CSP
✔ Utilisation de `python-constraint` pour générer **toutes les solutions valides**.  
✔ Sélection automatique de la **configuration minimale en coût**.  
✔ Possibilité d’ajouter une **contrainte budgétaire** pour filtrer les résultats.  
❌ Peut être lent sur **de grandes bases de données** en raison de l’explosion combinatoire.

### 2️⃣ Approche sans Solveur (MAC)
✔ **Propagation dynamique** des contraintes après chaque choix utilisateur.  
✔ Permet une **interaction fluide** en affichant uniquement les composants compatibles.  
✔ Plus efficace pour **grandes bases de données**, sans générer toutes les solutions.  
❌ Ne gère pas les contraintes budgétaires globales.

## Contraintes gérées
Le configurateur assure la compatibilité entre les composants en respectant les règles suivantes :
- **CPU – Carte Mère** : même socket.
- **Carte Mère – RAM** : même type de mémoire.
- **Carte Mère – Boîtier** : format supporté par le boîtier.
- **PSU – Boîtier** : format d’alimentation supporté par le boîtier.
- **PSU – GPU** : puissance d’alimentation suffisante.

## Installation et Exécution

### 📌 Prérequis
- Python 3.x
- Bibliothèques nécessaires : `pandas`, `constraint`
- Pour construire et afficher le graphe des contraintes : `networkx`,
`matplotlib`

Installez les dépendances avec :
```sh
pip install -r requirements.txt
```

### 🚀 Lancer le configurateur
Avec l'approche solveur :
```sh
python interactive_pc_builder_with_solver.py
```
Avec l'approche MAC (sans solveur) :
```sh
python interactive_pc_builder_without_solver.py
```
### 📊 Construire et afficher le graphe des contraintes
```sh
python constraints-graph.py
```
## Auteur
- **Nassim Lattab** - Université Paris Cité
