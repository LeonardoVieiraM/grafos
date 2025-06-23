import os
from dotenv import load_dotenv
import requests
import json
import time
from typing import Dict, List, Optional
from grafo import Grafo
import networkx as nx

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
    
    def build_graph(self, min_interactions: int = 30):
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

    def export_to_gephi(self, filename: str = 'social_graph.gexf'):
        """Exporta o grafo para formato Gephi (GEXF)"""
        if self.grafo is None:
            raise Exception("Grafo não construído. Execute build_graph() primeiro.")
        
        try:
            G = nx.DiGraph()
            
            # Add nodes with attributes
            for v in self.grafo.vertices:
                G.add_node(v, 
                          weight=self.grafo.pesos_vertices.get(v, 1),
                          label=self.grafo.rotulos_vertices.get(v, v))
            
            # Add edges with weights
            if self.representation == 'lista':
                for u in self.grafo.estrutura:
                    for (v, weight) in self.grafo.estrutura[u]:
                        G.add_edge(u, v, weight=weight)
            else:  # matriz
                vertex_index = {v: i for i, v in enumerate(sorted(self.grafo.vertices))}
                for i, u in enumerate(sorted(self.grafo.vertices)):
                    for j, v in enumerate(sorted(self.grafo.vertices)):
                        weight = self.grafo.estrutura[i][j]
                        if weight > 0:
                            G.add_edge(u, v, weight=weight)
            
            # Write GEXF file
            nx.write_gexf(G, filename)
            print(f"Grafo exportado para Gephi: {filename}")
            return True
        except Exception as e:
            print(f"Erro ao exportar para Gephi: {str(e)}")
            return False
          
    def export_to_gephi(self, filename: str = 'social_graph.gexf'):
        """Exporta o grafo para formato Gephi (GEXF)"""
        if self.grafo is None:
            raise Exception("Grafo não construído. Execute build_graph() primeiro.")
        
        G = nx.DiGraph()
        
        # Add nodes with attributes
        for v in self.grafo.vertices:
            G.add_node(v, 
                      weight=self.grafo.pesos_vertices.get(v, 1),
                      label=self.grafo.rotulos_vertices.get(v, v))
        
        # Add edges with weights
        for (u, v), weight in self.grafo.pesos_arestas.items():
            G.add_edge(u, v, weight=weight)
        
        # Write GEXF file
        nx.write_gexf(G, filename)
        print(f"Grafo exportado para Gephi: {filename}")
    
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

if __name__ == "__main__":
    try:
        load_dotenv()
        social_graph = SocialGraph()
        social_graph.build_graph()
        
        if social_graph.grafo and social_graph.grafo.quantidade_vertices() > 0:
            social_graph.export_to_csv()
            social_graph.plot_graph()
        else:
            print("Nenhum dado foi coletado. Verifique:")
            print("1. Se o token GITHUB_KEY no arquivo .env é válido")
            print("2. Se o repositório possui issues ou pull requests")
            print("3. Se você tem permissão para acessar este repositório")
    
    except Exception as e:
        print(f"\nErro durante a execução: {str(e)}")
        print("Verifique seu arquivo .env e as permissões do token GitHub")