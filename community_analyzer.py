import networkx as nx
import community
import csv
import numpy as np
from collections import defaultdict

class CommunityAnalyzer:
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        self.graph = nx.Graph()
        self.load_graph()
    
    def load_graph(self):
        # Carregar nós
        with open(f"{self.data_dir}/nodes.csv", 'r', encoding='utf-8') as nodes_file:
            reader = csv.DictReader(nodes_file)
            for row in reader:
                self.graph.add_node(row['id'], label=row['label'])
        
        # Carregar arestas
        with open(f"{self.data_dir}/edges.csv", 'r', encoding='utf-8') as edges_file:
            reader = csv.DictReader(edges_file)
            for row in reader:
                weight = float(row['weight'])
                if weight > 0:
                    self.graph.add_edge(
                        row['source'], 
                        row['target'], 
                        weight=weight,
                        type=row['type']
                    )
    
    def top_influential_users(self, top_k=5):
        """Retorna os k usuários mais influentes"""
        centrality = nx.eigenvector_centrality(self.graph, weight='weight', max_iter=1000)
        top_users = sorted(centrality.items(), key=lambda x: x[1], reverse=True)[:top_k]
        return top_users
    
    def fragmentation_culprit(self):
        """Identifica quem causa maior fragmentação ao ser removido"""
        betweenness = nx.betweenness_centrality(self.graph, weight='weight')
        culprit = max(betweenness.items(), key=lambda x: x[1])
        return culprit
    
    def natural_groups(self):
        """Identifica grupos naturais na comunidade"""
        partition = community.best_partition(self.graph, weight='weight')
        communities = defaultdict(list)
        for node, comm_id in partition.items():
            communities[comm_id].append(node)
        return dict(communities)
    
    def connection_level(self):
        """Calcula o nível de conexão da comunidade"""
        density = nx.density(self.graph)
        if nx.is_connected(self.graph):
            connection_percent = 1.0
        else:
            largest_cc = max(nx.connected_components(self.graph), key=len)
            connection_percent = len(largest_cc) / self.graph.number_of_nodes()
        return density, connection_percent
    
    def closest_users(self, username):
        """Encontra os usuários mais próximos de um determinado usuário"""
        if username not in self.graph:
            return None
        
        # Calcular distâncias usando Dijkstra (menor caminho considerando pesos)
        lengths = {}
        for target in self.graph.nodes():
            if target != username:
                try:
                    length = nx.dijkstra_path_length(self.graph, username, target, weight='weight')
                    lengths[target] = length
                except nx.NetworkXNoPath:
                    continue
        
        # Ordenar por proximidade (menor distância primeiro)
        closest = sorted(lengths.items(), key=lambda x: x[1])[:5]
        return closest
    
    def suggested_connections(self, username):
        """Sugere conexões próximas que ainda não existem"""
        if username not in self.graph:
            return None
        
        # Usuários não conectados
        non_neighbors = set(self.graph.nodes()) - set(self.graph.neighbors(username)) - {username}
        
        # Calcular similaridade de Jaccard
        suggestions = []
        for user in non_neighbors:
            neighbors_u = set(self.graph.neighbors(username))
            neighbors_v = set(self.graph.neighbors(user))
            
            if neighbors_u and neighbors_v:
                jaccard = len(neighbors_u & neighbors_v) / len(neighbors_u | neighbors_v)
                suggestions.append((user, jaccard))
        
        # Ordenar por similaridade
        suggestions.sort(key=lambda x: x[1], reverse=True)
        return suggestions[:5]

# Exemplo de uso
if __name__ == '__main__':
    analyzer = CommunityAnalyzer()
    
    print("Top 5 usuários influentes:")
    print(analyzer.top_influential_users())
    
    print("\nMaior causador de fragmentação:")
    print(analyzer.fragmentation_culprit())
    
    print("\nGrupos naturais:")
    groups = analyzer.natural_groups()
    for i, (comm_id, members) in enumerate(groups.items()):
        print(f"Grupo {i+1} ({len(members)} membros): {', '.join(members[:3])}{'...' if len(members) > 3 else ''}")
    
    density, connection_percent = analyzer.connection_level()
    print(f"\nDensidade da rede: {density:.4f}")
    print(f"Percentual de conexão: {connection_percent:.1%}")
    
    username = "pukkandan"  # Exemplo de usuário
    print(f"\nUsuários mais próximos de {username}:")
    print(analyzer.closest_users(username))
    
    print(f"\nConexões sugeridas para {username}:")
    print(analyzer.suggested_connections(username))