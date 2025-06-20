import csv
import matplotlib.pyplot as plt
from typing import Dict, List, Optional, Tuple, Union

class Grafo:
    def __init__(self, representacao: str = 'lista'):
        """
        Inicializa um grafo vazio com a representação escolhida
        
        Args:
            representacao: 'matriz' para matriz de adjacência ou 'lista' para lista de adjacência
        """
        self.representacao = representacao
        self.vertices = set()
        self.arestas = []
        self.pesos_vertices = {}
        self.rotulos_vertices = {}
        self.pesos_arestas = {}
        self.rotulos_arestas = {}
        
        if representacao == 'matriz':
            self.estrutura = []
            self._matriz_atualizada = False
        else:
            self.estrutura = {}  # Dicionário para lista de adjacência
    
    def adicionar_vertice(self, v: str, peso: float = 1, rotulo: str = ''):
        """
        Adiciona um vértice ao grafo
        
        Args:
            v: Nome/ID do vértice
            peso: Peso do vértice (opcional)
            rotulo: Rótulo do vértice (opcional)
        """
        if v not in self.vertices:
            self.vertices.add(v)
            
            if self.representacao == 'lista':
                self.estrutura[v] = []
            
            self._matriz_atualizada = False
        
        if peso != 1:
            self.pesos_vertices[v] = peso
        if rotulo:
            self.rotulos_vertices[v] = rotulo
    
    def adicionar_aresta(self, u: str, v: str, peso: float = 1, rotulo: str = ''):
        """
        Adiciona uma aresta entre os vértices u e v
        
        Args:
            u: Vértice de origem
            v: Vértice de destino
            peso: Peso da aresta (opcional, padrão=1)
            rotulo: Rótulo da aresta (opcional, padrão='')
        """
        # Adiciona os vértices se não existirem
        self.adicionar_vertice(u)
        self.adicionar_vertice(v)
            
        if (u, v) not in self.arestas:
            self.arestas.append((u, v))
        
        self.pesos_arestas[(u, v)] = peso
        if rotulo:
            self.rotulos_arestas[(u, v)] = rotulo
            
        if self.representacao == 'matriz':
            self._matriz_atualizada = False
        else:
            # Verifica se a aresta já existe na lista de adjacência
            if not any(vertice == v for vertice, _ in self.estrutura[u]):
                self.estrutura[u].append((v, peso))
    
    def _atualizar_matriz(self):
        """Atualiza a matriz de adjacência baseada nos vértices e arestas atuais"""
        if not self.representacao == 'matriz':
            return
        
        num_vertices = len(self.vertices)
        self.estrutura = [[0] * num_vertices for _ in range(num_vertices)]
        
        # Mapeia vértices para índices
        vertex_index = {v: i for i, v in enumerate(sorted(self.vertices))}
        
        # Preenche a matriz com os pesos das arestas
        for u, v in self.arestas:
            i = vertex_index[u]
            j = vertex_index[v]
            self.estrutura[i][j] = self.pesos_arestas.get((u, v), 1)
        
        self._matriz_atualizada = True
    
    def remover_aresta(self, u: str, v: str):
        """
        Remove a aresta entre os vértices u e v
        
        Args:
            u: Vértice de origem
            v: Vértice de destino
        """
        if (u, v) not in self.arestas:
            raise ValueError("Aresta não existe")
            
        self.arestas.remove((u, v))
        if (u, v) in self.pesos_arestas:
            del self.pesos_arestas[(u, v)]
        if (u, v) in self.rotulos_arestas:
            del self.rotulos_arestas[(u, v)]
            
        if self.representacao == 'matriz':
            self._matriz_atualizada = False
        else:
            self.estrutura[u] = [(vertice, peso) for vertice, peso in self.estrutura[u] if vertice != v]
    
    def remover_vertice(self, v: str):
        """
        Remove um vértice e todas as arestas conectadas a ele
        
        Args:
            v: Vértice a ser removido
        """
        if v not in self.vertices:
            raise ValueError("Vértice não existe")
            
        self.vertices.remove(v)
        
        # Remove arestas associadas
        arestas_para_remover = [(u, w) for u, w in self.arestas if u == v or w == v]
        for u, w in arestas_para_remover:
            self.remover_aresta(u, w)
        
        if self.representacao == 'matriz':
            self._matriz_atualizada = False
        else:
            del self.estrutura[v]
            # Remove referências ao vértice em outras listas
            for u in self.estrutura:
                self.estrutura[u] = [(vertice, peso) for vertice, peso in self.estrutura[u] if vertice != v]
    
    def definir_peso_vertice(self, v: str, peso: float):
        """
        Define o peso de um vértice
        
        Args:
            v: Vértice
            peso: Peso do vértice
        """
        if v not in self.vertices:
            raise ValueError("Vértice inválido")
        self.pesos_vertices[v] = peso
    
    def definir_rotulo_vertice(self, v: str, rotulo: str):
        """
        Define o rótulo de um vértice
        
        Args:
            v: Vértice
            rotulo: Rótulo do vértice
        """
        if v not in self.vertices:
            raise ValueError("Vértice inválido")
        self.rotulos_vertices[v] = rotulo
    
    def sao_adjacentes_vertices(self, u: str, v: str) -> bool:
        """
        Verifica se dois vértices são adjacentes
        
        Args:
            u: Vértice 1
            v: Vértice 2
            
        Returns:
            True se são adjacentes, False caso contrário
        """
        if self.representacao == 'matriz':
            if not self._matriz_atualizada:
                self._atualizar_matriz()
            vertex_index = {v: i for i, v in enumerate(sorted(self.vertices))}
            i = vertex_index[u]
            j = vertex_index[v]
            return self.estrutura[i][j] != 0
        else:
            return any(vertice == v for vertice, _ in self.estrutura.get(u, []))
    
    def quantidade_vertices(self) -> int:
        """
        Retorna a quantidade de vértices do grafo
        
        Returns:
            Número de vértices
        """
        return len(self.vertices)
    
    def quantidade_arestas(self) -> int:
        """
        Retorna a quantidade de arestas do grafo
        
        Returns:
            Número de arestas
        """
        return len(self.arestas)
    
    def e_vazio(self) -> bool:
        """
        Verifica se o grafo é vazio (sem arestas)
        
        Returns:
            True se o grafo é vazio, False caso contrário
        """
        return len(self.arestas) == 0
    
    def exportar_csv(self, nome_arquivo: str):
        """
        Exporta o grafo para um arquivo CSV
        
        Args:
            nome_arquivo: Nome do arquivo CSV de saída
        """
        with open(nome_arquivo, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            
            # Escreve cabeçalho com informações básicas
            writer.writerow(['Tipo', 'Grafo'])
            writer.writerow(['Representacao', self.representacao])
            writer.writerow(['NumVertices', self.quantidade_vertices()])
            
            # Escreve vértices
            writer.writerow([])
            writer.writerow(['Vertices'])
            for v in sorted(self.vertices):
                peso = self.pesos_vertices.get(v, '')
                rotulo = self.rotulos_vertices.get(v, '')
                writer.writerow([v, peso, rotulo])
            
            # Escreve arestas
            writer.writerow([])
            writer.writerow(['Arestas', 'Origem', 'Destino', 'Peso', 'Rotulo'])
            for u, v in sorted(self.arestas):
                peso = self.pesos_arestas.get((u, v), '')
                rotulo = self.rotulos_arestas.get((u, v), '')
                writer.writerow(['', u, v, peso, rotulo])
    
    @classmethod
    def importar_csv(cls, nome_arquivo: str) -> 'Grafo':
        """
        Importa um grafo de um arquivo CSV
        
        Args:
            nome_arquivo: Nome do arquivo CSV de entrada
            
        Returns:
            Instância de Grafo reconstruída a partir do arquivo
        """
        with open(nome_arquivo, 'r') as csvfile:
            reader = csv.reader(csvfile)
            
            # Lê informações básicas
            next(reader)  # Pula linha do cabeçalho
            representacao = next(reader)[1]
            next(reader)  # Pula número de vértices (vamos recalcular)
            
            grafo = cls(representacao)
            
            # Pula linhas vazias até chegar aos vértices
            while True:
                linha = next(reader)
                if linha and linha[0] == 'Vertices':
                    break
            
            # Lê vértices
            for linha in reader:
                if not linha:  # Linha vazia indica fim da seção
                    break
                v, peso, rotulo = linha
                peso = float(peso) if peso else 1.0
                grafo.adicionar_vertice(v, peso, rotulo)
            
            # Lê arestas (pula cabeçalho)
            next(reader)  # Pula linha do cabeçalho
            for linha in reader:
                if not linha:  # Linha vazia indica fim do arquivo
                    break
                _, u, v, peso, rotulo = linha
                peso = float(peso) if peso else 1.0
                grafo.adicionar_aresta(u, v, peso, rotulo)
            
            return grafo
    
    def plotar(self):
        """
        Plota o grafo usando matplotlib (sem NetworkX)
        """
        if not self.vertices:
            print("Grafo vazio - nada para plotar")
            return
        
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Configurações de plotagem
        node_radius = 0.05
        node_positions = self._calcular_posicoes()
        
        # Desenha arestas
        for u, v in self.arestas:
            x1, y1 = node_positions[u]
            x2, y2 = node_positions[v]
            ax.plot([x1, x2], [y1, y2], 'k-', alpha=0.5)
            
            # Adiciona peso/rotulo da aresta
            peso = self.pesos_arestas.get((u, v), '')
            rotulo = self.rotulos_arestas.get((u, v), '')
            label = rotulo if rotulo else str(peso) if peso else ''
            if label:
                ax.text((x1+x2)/2, (y1+y2)/2, label, 
                        ha='center', va='center', 
                        bbox=dict(facecolor='white', alpha=0.7, edgecolor='none'))
        
        # Desenha vértices
        for v, (x, y) in node_positions.items():
            peso = self.pesos_vertices.get(v, 1)
            # Tamanho do nó proporcional ao peso (com limites mínimos e máximos)
            node_size = max(500, min(3000, peso * 100))
            
            ax.add_patch(plt.Circle((x, y), node_radius, 
                         facecolor='skyblue', edgecolor='k'))
            
            # Rótulo do vértice
            rotulo = self.rotulos_vertices.get(v, v)
            ax.text(x, y, rotulo, 
                    ha='center', va='center', 
                    fontsize=10, fontweight='bold')
            
            # Peso do vértice (se diferente de 1)
            if peso != 1:
                ax.text(x, y - node_radius*1.5, f"Peso: {peso}", 
                        ha='center', va='top', fontsize=8)
        
        ax.set_aspect('equal')
        ax.autoscale_view()
        ax.axis('off')
        plt.title("Grafo Social de Interações")
        plt.show()
    
    def _calcular_posicoes(self) -> Dict[str, Tuple[float, float]]:
        """
        Calcula posições para os vértices em um layout circular
        
        Returns:
            Dicionário mapeando vértices para posições (x, y)
        """
        num_vertices = len(self.vertices)
        radius = 1.0
        center = (0, 0)
        
        positions = {}
        for i, v in enumerate(sorted(self.vertices)):
            angle = 2 * 3.141592653589793 * i / num_vertices
            x = center[0] + radius * 1.5 * (1 + 0.1 * (i % 3)) * 3.141592653589793.cos(angle)
            y = center[1] + radius * 1.5 * (1 + 0.1 * (i % 3)) * 3.141592653589793.sin(angle)
            positions[v] = (x, y)
        
        return positions