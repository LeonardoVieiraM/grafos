import os
from dotenv import load_dotenv
import requests
import json
import time
from typing import Dict, List, Optional, Set, Tuple
from grafo import Grafo
import matplotlib.pyplot as plt
import math
from collections import defaultdict, deque

load_dotenv()

class SocialGraph:
    def __init__(self, representation: str = 'matriz'):
        """
        Initialize with choice of representation ('lista' or 'matriz')
        """
        self.github_key = os.getenv('GITHUB_KEY')
        self.repositorio = os.getenv('REPOSITORIO')
        if not self.github_key or not self.repositorio:
            raise ValueError("Missing GitHub credentials in .env file")
        self.owner, self.repo = self._parse_repo_url()
        self.graphql_url = 'https://api.github.com/graphql'
        self.headers = {
            'Authorization': f'Bearer {self.github_key}',
            'Content-Type': 'application/json'
        }
        self.representation = representation
        self.grafo = None
    
    def _parse_repo_url(self) -> tuple:
        """Extrai owner e nome do repositório da URL"""
        parts = self.repositorio.replace('https://github.com/', '').split('/')
        return parts[0], parts[1]
    
    def _run_query(self, query: str, variables: Optional[Dict] = None) -> Dict:
        """Executa uma consulta GraphQL"""
        payload = {'query': query}
        if variables:
            payload['variables'] = variables
        
        try:
            response = requests.post(
                self.graphql_url,
                headers=self.headers,
                data=json.dumps(payload),
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            if 'errors' in data:
                error_msg = "\n".join([e['message'] for e in data['errors']])
                raise Exception(f"GraphQL errors: {error_msg}")
            
            if 'data' not in data:
                raise Exception("No 'data' field in response")
                
            return data
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed: {str(e)}")
    
    def _get_issues_and_prs(self, cursor: Optional[str] = None) -> Dict:
        """Obtém issues e PRs com paginação"""
        query = """
        query ($owner: String!, $repo: String!, $cursor: String) {
          repository(owner: $owner, name: $repo) {
            issues(first: 50, after: $cursor, orderBy: {field: CREATED_AT, direction: ASC}) {
              pageInfo {
                hasNextPage
                endCursor
              }
              nodes {
                author {
                  login
                }
                comments(first: 50) {
                  nodes {
                    author {
                      login
                    }
                  }
                }
              }
            }
            pullRequests(first: 50, after: $cursor, orderBy: {field: CREATED_AT, direction: ASC}) {
              pageInfo {
                hasNextPage
                endCursor
              }
              nodes {
                author {
                  login
                }
                comments(first: 50) {
                  nodes {
                    author {
                      login
                    }
                  }
                }
                reviews(first: 50) {
                  nodes {
                    author {
                      login
                    }
                    comments(first: 50) {
                      nodes {
                        author {
                          login
                        }
                      }
                    }
                  }
                }
              }
            }
          }
        }
        """
        variables = {
            'owner': self.owner,
            'repo': self.repo,
            'cursor': cursor
        }
        return self._run_query(query, variables)
    
    def _process_interactions(self, data: Dict) -> Dict[str, Dict[str, int]]:
        """
        Processa os dados da API e retorna um dicionário de interações
        """
        interactions = {}
        
        def add_interaction(source, target, weight=1):
            if not source or not target or not source.get('login') or not target.get('login'):
                return
            
            source_login = source['login']
            target_login = target['login']
            
            if source_login == target_login:
                return
            
            if source_login not in interactions:
                interactions[source_login] = {}
            
            interactions[source_login][target_login] = interactions[source_login].get(target_login, 0) + weight
        
        try:
            repo_data = data['data']['repository']
            
            # Process issues
            for issue in repo_data['issues']['nodes']:
                author = issue.get('author')
                if not author:
                    continue
                
                for comment in issue['comments']['nodes']:
                    comment_author = comment.get('author')
                    add_interaction(author, comment_author)
                    add_interaction(comment_author, author)
            
            # Process PRs
            for pr in repo_data['pullRequests']['nodes']:
                author = pr.get('author')
                if not author:
                    continue
                
                # PR comments
                for comment in pr['comments']['nodes']:
                    comment_author = comment.get('author')
                    add_interaction(author, comment_author)
                    add_interaction(comment_author, author)
                
                # PR reviews and review comments
                for review in pr['reviews']['nodes']:
                    review_author = review.get('author')
                    if not review_author:
                        continue
                    
                    add_interaction(author, review_author, 2)
                    add_interaction(review_author, author, 2)
                    
                    for review_comment in review['comments']['nodes']:
                        review_comment_author = review_comment.get('author')
                        add_interaction(author, review_comment_author)
                        add_interaction(review_comment_author, author)
            
            return interactions
            
        except KeyError as e:
            raise Exception(f"Missing expected data field: {str(e)}")
    
    def build_graph(self, min_interactions: int = 50):
        """Constrói o grafo social com representação escolhida"""
        print(f"Iniciando construção do grafo social ({self.representation})...")
        
        all_interactions = {}
        cursor = None
        has_next_page = True
        request_count = 0
        
        while has_next_page and request_count < 30:
            request_count += 1
            print(f"Realizando requisição {request_count}...")
            
            try:
                data = self._get_issues_and_prs(cursor)
                batch_interactions = self._process_interactions(data)
                
                for user, interactions in batch_interactions.items():
                    if user not in all_interactions:
                        all_interactions[user] = {}
                    for target, weight in interactions.items():
                        all_interactions[user][target] = all_interactions[user].get(target, 0) + weight
                
                issues_page_info = data['data']['repository']['issues']['pageInfo']
                has_next_page = issues_page_info['hasNextPage']
                cursor = issues_page_info['endCursor']
                
                time.sleep(1.5)
                
            except Exception as e:
                print(f"Erro durante a coleta de dados: {str(e)}")
                break
        
        # Create graph with chosen representation
        self.grafo = Grafo(representacao=self.representation)
        
        # Collect all users and filter by activity
        all_users = set()
        user_activity = {}
        
        for source, targets in all_interactions.items():
            total = sum(targets.values())
            user_activity[source] = total
            all_users.add(source)
            all_users.update(targets.keys())
        
        # Filter users by minimum interactions
        if min_interactions > 0:
            active_users = {u for u in all_users if user_activity.get(u, 0) >= min_interactions}
            print(f"Filtrando {len(active_users)} usuários ativos (≥ {min_interactions} interações)")
        else:
            active_users = all_users
        
        # Add vertices (filtered users)
        for user in active_users:
            total_interactions = sum(all_interactions.get(user, {}).values()) + \
                                sum(v.get(user, 0) for v in all_interactions.values())
            self.grafo.adicionar_vertice(user, peso=total_interactions, rotulo=user)
        
        # Add edges (filtered interactions)
        for source, targets in all_interactions.items():
            if source not in active_users:
                continue
            for target, weight in targets.items():
                if target in active_users:
                    self.grafo.adicionar_aresta(source, target, peso=weight)
        
        print("\nGrafo social construído com sucesso!")
        print(f"Total de usuários: {self.grafo.quantidade_vertices()}")
        print(f"Total de interações: {self.grafo.quantidade_arestas()}\n")
        
        
        
    def run_analysis_menu(self):
        """Menu interativo para análise do grafo social"""
        if self.grafo is None or self.grafo.quantidade_vertices() == 0:
            print("Grafo não construído ou vazio. Execute build_graph() primeiro.")
            return
        
        while True:
            print("\n=== MENU DE ANÁLISE DO GRAFO SOCIAL ===")
            print("1. Mostrar 5 usuários mais influentes")
            print("2. Identificar e remover quem gera maior fragmentação")
            print("3. Mostrar grupos naturais existentes")
            print("4. Calcular nível de conexão da comunidade")
            print("5. Encontrar usuários mais próximos de um usuário")
            print("6. Encontrar usuários próximos que não interagem")
            print("7. Visualizar grafo")
            print("0. Sair")
            
            choice = input("Escolha uma opção (0-7): ")
            
            if choice == "1":
                self.show_most_influential()
            elif choice == "2":
                self.handle_fragmentation()
            elif choice == "3":
                self.show_natural_groups()
            elif choice == "4":
                self.show_connection_level()
            elif choice == "5":
                self.show_close_users()
            elif choice == "6":
                self.show_close_non_interacting()
            elif choice == "7":
                self.plot_graph()
            elif choice == "0":
                break
            else:
                print("Opção inválida. Tente novamente.")
    
    def show_most_influential(self):
        """Mostra os 5 usuários mais influentes"""
        top_users = self.usuarios_mais_influentes()
        print("\nTop 5 usuários mais influentes:")
        for i, (user, score) in enumerate(top_users, 1):
            print(f"{i}. {user} (influência: {score})")
    
    def handle_fragmentation(self):
        """Identifica e remove o vértice que causa maior fragmentação"""
        vertice = self.remover_maior_fragmentador()
        print(f"\nVértice que causava maior fragmentação removido: {vertice}")
        print("O grafo foi atualizado. Você pode visualizar as mudanças selecionando a opção 7.")
    
    def show_natural_groups(self):
        """Mostra os grupos naturais identificados"""
        grupos = self.grupos_naturais()
        print("\nGrupos naturais identificados:")
        for i, grupo in enumerate(grupos, 1):
            print(f"\nGrupo {i} ({len(grupo)} membros):")
            print(", ".join(sorted(grupo)))
    
    def show_connection_level(self):
        """Mostra o percentual de conexão da comunidade"""
        percentual = self.nivel_conexao()
        print(f"\nNível de conexão da comunidade: {percentual:.2f}%")
    
    def show_close_users(self):
        """Mostra usuários próximos a um usuário específico"""
        usuario = input("\nDigite o nome do usuário: ")
        try:
            proximos = self.usuarios_proximos(usuario)
            print(f"\nUsuários mais próximos de {usuario}:")
            for i, (user, dist) in enumerate(proximos, 1):
                print(f"{i}. {user} (distância: {dist:.2f})")
        except ValueError as e:
            print(f"Erro: {e}")
    
    def show_close_non_interacting(self):
        """Mostra usuários próximos que não interagem com um usuário específico"""
        usuario = input("\nDigite o nome do usuário: ")
        try:
            proximos = self.usuarios_proximos_nao_interagem(usuario)
            print(f"\nUsuários próximos que não interagem com {usuario}:")
            for i, (user, dist) in enumerate(proximos, 1):
                print(f"{i}. {user} (distância: {dist:.2f})")
        except ValueError as e:
            print(f"Erro: {e}")

    def export_to_gephi(self, filename: str = 'social_graph.gexf'):
        """Exporta o grafo para formato Gephi (GEXF)"""
        if self.grafo is None:
            raise Exception("Grafo não construído. Execute build_graph() primeiro.")
        
        # Implementação alternativa sem NetworkX
        print("Exportação para GEXF requer NetworkX. Use export_to_csv() como alternativa.")
        return False
    
    def export_to_csv(self, filename: str = 'social_graph.csv'):
        """Exporta o grafo social para CSV"""
        if self.grafo is None:
            raise Exception("Grafo não construído. Execute build_graph() primeiro.")
        
        self.grafo.exportar_csv(filename)
        print(f"Grafo exportado para {filename}")
    
    def plot_graph(self):
        """Plota o grafo social"""
        if self.grafo is None:
            raise Exception("Grafo não construído. Execute build_graph() primeiro.")
        
        if self.grafo.quantidade_vertices() == 0:
            print("Grafo vazio - nada para plotar")
            return
        
        self.grafo.plotar()
    
    def usuarios_mais_influentes(self, top_n: int = 5) -> List[tuple[str, int]]:
        """
        Retorna os usuários mais influentes baseado no grau de saída ponderado
        """
        if self.grafo is None:
            raise Exception("Grafo não construído")
        
        influencia = []
        for v in self.grafo.vertices:
            grau_saida = 0
            if self.grafo.representacao == 'lista':
                for (vizinho, peso) in self.grafo.estrutura.get(v, []):
                    grau_saida += peso
            else:
                if not self.grafo._matriz_atualizada:
                    self.grafo._atualizar_matriz()
                idx = self.grafo._vertex_index[v]
                grau_saida = sum(self.grafo.estrutura[idx])
            
            influencia.append((v, grau_saida))
        
        return sorted(influencia, key=lambda x: x[1], reverse=True)[:top_n]

    def remover_maior_fragmentador(self):
        """
        Identifica e remove o vértice que causa maior fragmentação no grafo
        """
        if self.grafo is None:
            raise Exception("Grafo não construído")
        
        # Implementação alternativa de betweenness centrality
        betweenness = self._calcular_betweenness()
        vertice_remover = max(betweenness, key=betweenness.get)
        
        print(f"Removendo vértice que causa maior fragmentação: {vertice_remover}")
        self.grafo.remover_vertice(vertice_remover)
        return vertice_remover
    
    def _calcular_betweenness(self) -> Dict[str, float]:
        """Calcula betweenness centrality sem NetworkX"""
        betweenness = {v: 0.0 for v in self.grafo.vertices}
        
        for s in self.grafo.vertices:
            # Estruturas para o algoritmo
            S = []
            P = {v: [] for v in self.grafo.vertices}
            sigma = {v: 0 for v in self.grafo.vertices}
            sigma[s] = 1
            d = {v: -1 for v in self.grafo.vertices}
            d[s] = 0
            Q = deque()
            Q.append(s)
            
            while Q:
                v = Q.popleft()
                S.append(v)
                for w in self._obter_vizinhos_direcionados(v):
                    if d[w] < 0:
                        Q.append(w)
                        d[w] = d[v] + 1
                    if d[w] == d[v] + 1:
                        sigma[w] += sigma[v]
                        P[w].append(v)
            
            delta = {v: 0 for v in self.grafo.vertices}
            while S:
                w = S.pop()
                for v in P[w]:
                    delta[v] += (sigma[v] / sigma[w]) * (1 + delta[w])
                if w != s:
                    betweenness[w] += delta[w]
        
        # Normalização para grafos direcionados
        n = len(self.grafo.vertices)
        if n > 2:
            for v in betweenness:
                betweenness[v] /= (n - 1) * (n - 2)
        
        return betweenness
    
    def _obter_vizinhos_direcionados(self, v: str) -> List[str]:
        """Obtém vizinhos direcionados (apenas arestas de saída)"""
        if self.grafo.representacao == 'lista':
            return [vizinho for vizinho, _ in self.grafo.estrutura.get(v, [])]
        else:
            if not self.grafo._matriz_atualizada:
                self.grafo._atualizar_matriz()
            idx = self.grafo._vertex_index[v]
            return [vertice for vertice, i in self.grafo._vertex_index.items() 
                   if self.grafo.estrutura[idx][i] > 0]

    def grupos_naturais(self, n_grupos: int = 3) -> List[set[str]]:
        """
        Identifica grupos naturais no grafo usando detecção de comunidades (Louvain alternativo)
        """
        if self.grafo is None:
            raise Exception("Grafo não construído")
        
        # Implementação simplificada de detecção de comunidades
        # Esta é uma versão simplificada - algoritmos reais são mais complexos
        
        # Converte para grafo não direcionado (soma pesos em ambas direções)
        grafo_nao_dir = defaultdict(dict)
        for (u, v), peso in self.grafo.pesos_arestas.items():
            grafo_nao_dir[u][v] = grafo_nao_dir[u].get(v, 0) + peso
            grafo_nao_dir[v][u] = grafo_nao_dir[v].get(u, 0) + peso
        
        # Algoritmo simplificado de detecção de comunidades
        comunidades = {v: i for i, v in enumerate(self.grafo.vertices)}
        mudou = True
        
        while mudou:
            mudou = False
            for v in self.grafo.vertices:
                melhor_comunidade = self._encontrar_melhor_comunidade(v, grafo_nao_dir, comunidades)
                if melhor_comunidade != comunidades[v]:
                    comunidades[v] = melhor_comunidade
                    mudou = True
        
        # Agrupa por comunidade
        grupos = defaultdict(set)
        for v, com in comunidades.items():
            grupos[com].add(v)
        
        # Retorna os maiores grupos
        return sorted(grupos.values(), key=len, reverse=True)[:n_grupos]
    
    def _encontrar_melhor_comunidade(self, v, grafo, comunidades):
        """Auxiliar para encontrar a melhor comunidade para um vértice"""
        vizinhos = grafo.get(v, {})
        comunidades_vizinhos = defaultdict(int)
        
        for vizinho, peso in vizinhos.items():
            com = comunidades[vizinho]
            comunidades_vizinhos[com] += peso
        
        if not comunidades_vizinhos:
            return comunidades[v]
        
        return max(comunidades_vizinhos.items(), key=lambda x: x[1])[0]

    def nivel_conexao(self) -> float:
        """
        Calcula o percentual de conexão da comunidade
        """
        if self.grafo is None:
            raise Exception("Grafo não construído")
        
        n = self.grafo.quantidade_vertices()
        if n <= 1:
            return 0.0
        
        max_edges = n * (n - 1)  # Para grafo direcionado
        actual_edges = self.grafo.quantidade_arestas()
        return (actual_edges / max_edges) * 100

    def usuarios_proximos(self, usuario: str, n: int = 5) -> List[tuple[str, float]]:
        """
        Retorna os usuários mais próximos a um determinado usuário usando Dijkstra
        """
        if self.grafo is None:
            raise Exception("Grafo não construído")
        if usuario not in self.grafo.vertices:
            raise ValueError(f"Usuário {usuario} não encontrado no grafo")
        
        distancias = {v: float('inf') for v in self.grafo.vertices}
        distancias[usuario] = 0
        visitados = set()
        
        while len(visitados) < len(self.grafo.vertices):
            # Encontra o vértice não visitado com menor distância
            corrente = None
            menor_dist = float('inf')
            for v in self.grafo.vertices:
                if v not in visitados and distancias[v] < menor_dist:
                    menor_dist = distancias[v]
                    corrente = v
            
            if corrente is None:
                break
            
            visitados.add(corrente)
            
            # Atualiza distâncias dos vizinhos
            for vizinho, peso in self._obter_vizinhos_pesos(corrente):
                if distancias[vizinho] > distancias[corrente] + (1 / peso if peso > 0 else float('inf')):
                    distancias[vizinho] = distancias[corrente] + (1 / peso if peso > 0 else float('inf'))
        
        # Remove o próprio usuário e infinitos
        distancias.pop(usuario)
        distancias = {k: v for k, v in distancias.items() if v != float('inf')}
        
        return sorted(distancias.items(), key=lambda x: x[1])[:n]
    
    def _obter_vizinhos_pesos(self, v: str) -> List[tuple[str, float]]:
        """Obtém vizinhos e pesos das arestas de saída"""
        if self.grafo.representacao == 'lista':
            return self.grafo.estrutura.get(v, [])
        else:
            if not self.grafo._matriz_atualizada:
                self.grafo._atualizar_matriz()
            idx = self.grafo._vertex_index[v]
            return [(vertice, self.grafo.estrutura[idx][i]) 
                   for vertice, i in self.grafo._vertex_index.items() 
                   if self.grafo.estrutura[idx][i] > 0]

    def usuarios_proximos_nao_interagem(self, usuario: str, n: int = 5) -> List[tuple[str, float]]:
        """
        Retorna usuários próximos que não têm interação direta
        """
        proximos = self.usuarios_proximos(usuario, n*2)  # Pegamos mais para filtrar
        
        # Filtra os que não têm aresta direta
        resultado = []
        for user, dist in proximos:
            if not self.grafo.sao_adjacentes_vertices(usuario, user):
                resultado.append((user, dist))
                if len(resultado) >= n:
                    break
                    
        return resultado

if __name__ == "__main__":
    try:
        load_dotenv()
        social_graph = SocialGraph()
        print("Construindo grafo social...")
        social_graph.build_graph()
        
        if social_graph.grafo and social_graph.grafo.quantidade_vertices() > 0:
            social_graph.run_analysis_menu()
        else:
            print("Nenhum dado foi coletado. Verifique:")
            print("1. Se o token GITHUB_KEY no arquivo .env é válido")
            print("2. Se o repositório possui issues ou pull requests")
            print("3. Se você tem permissão para acessar este repositório")
    
    except Exception as e:
        print(f"\nErro durante a execução: {str(e)}")
        print("Verifique seu arquivo .env e as permissões do token GitHub")