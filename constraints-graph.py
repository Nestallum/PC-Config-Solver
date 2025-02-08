import networkx as nx
import matplotlib.pyplot as plt

# Création du graphe des contraintes
G = nx.DiGraph()

# Ajout des composants comme nœuds
components = ["CPU", "Motherboard", "RAM", "GPU", "PSU", "Case"]
G.add_nodes_from(components)

# Ajout des contraintes sous forme de relations entre les composants
edges = [
    ("CPU", "Motherboard"),  # Compatibilité socket
    ("Motherboard", "RAM"),  # Type de mémoire supporté
    ("Motherboard", "Case"),  # Format supporté
    ("GPU", "PSU"),  # Alimentation suffisante pour le GPU
    ("PSU", "Case"),  # Format de l'alimentation
]

G.add_edges_from(edges)

# Dessiner le graphe
plt.figure(figsize=(15, 8))
pos = nx.spring_layout(G, seed=5)
nx.draw(G, pos, with_labels=True, node_size=10000, node_color="lightblue", edge_color="black", font_size=10, font_weight="bold")
plt.title("Graphe des Contraintes du Configurateur PC")
plt.show()
