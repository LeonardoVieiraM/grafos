import os
from dotenv import load_dotenv
import requests
import json
import time
from typing import Dict, List, Optional
from grafo import Grafo  # Importando nossa biblioteca de grafos

load_dotenv()  # Carrega variáveis do .env

class SocialGraph:
    def __init__(self):
        self.github_key = os.getenv('GITHUB_KEY')
        self.repositorio = os.getenv('REPOSITORIO')
        self.owner, self.repo = self._parse_repo_url()
        self.graphql_url = 'https://api.github.com/graphql'
        self.headers = {
            'Authorization': f'Bearer {self.github_key}',
            'Content-Type': 'application/json'
        }
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
        
        response = requests.post(
            self.graphql_url,
            headers=self.headers,
            data=json.dumps(payload)
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Query failed: {response.status_code} - {response.text}")
    
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
                id
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
                id
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
        Formato: {'usuario1': {'usuario2': peso, 'usuario3': peso}, ...}
        """
        interactions = {}
        
        def add_interaction(source, target):
            if source is None or target is None:
                return
            
            if source['login'] == target['login']:
                return  # Ignora auto-interações
            
            if source['login'] not in interactions:
                interactions[source['login']] = {}
            
            if target['login'] not in interactions[source['login']]:
                interactions[source['login']][target['login']] = 0
            
            interactions[source['login']][target['login']] += 1
        
        # Processa issues
        for issue in data['data']['repository']['issues']['nodes']:
            author = issue['author']
            for comment in issue['comments']['nodes']:
                comment_author = comment['author']
                add_interaction(author, comment_author)
                add_interaction(comment_author, author)  # Interação bidirecional
        
        # Processa PRs
        for pr in data['data']['repository']['pullRequests']['nodes']:
            author = pr['author']
            
            # Comentários no PR
            for comment in pr['comments']['nodes']:
                comment_author = comment['author']
                add_interaction(author, comment_author)
                add_interaction(comment_author, author)
            
            # Reviews no PR
            for review in pr['reviews']['nodes']:
                review_author = review['author']
                add_interaction(author, review_author)
                add_interaction(review_author, author)
        
        return interactions
    
    def build_graph(self):
        """Constrói o grafo social a partir das interações no repositório"""
        print("Iniciando construção do grafo social...")
        
        # Inicializa estruturas para coleta de dados
        all_interactions = {}
        cursor = None
        has_next_page = True
        request_count = 0
        
        # Loop de paginação
        while has_next_page and request_count < 10:  # Limite para evitar rate limit
            request_count += 1
            print(f"Realizando requisição {request_count}...")
            
            try:
                data = self._get_issues_and_prs(cursor)
                batch_interactions = self._process_interactions(data)
                
                # Merge dos resultados
                for user, interactions in batch_interactions.items():
                    if user not in all_interactions:
                        all_interactions[user] = {}
                    
                    for target, weight in interactions.items():
                        if target not in all_interactions[user]:
                            all_interactions[user][target] = 0
                        all_interactions[user][target] += weight
                
                # Verifica paginação para issues (assumindo mesma paginação para PRs)
                issues_page_info = data['data']['repository']['issues']['pageInfo']
                has_next_page = issues_page_info['hasNextPage']
                cursor = issues_page_info['endCursor']
                
                # Espera para evitar rate limit
                time.sleep(1)
                
            except Exception as e:
                print(f"Erro durante a coleta de dados: {str(e)}")
                break
        
        # Cria o grafo
        users = set()
        for source, targets in all_interactions.items():
            users.add(source)
            users.update(targets.keys())
        
        self.grafo = Grafo(representacao='lista')
        
        # Mapeia usuários para índices (opcional, dependendo da sua implementação)
        user_index = {user: idx for idx, user in enumerate(users)}
        
        # Adiciona vértices (usuários) com pesos baseados no total de interações
        for user in users:
            total_interactions = sum(all_interactions.get(user, {}).values())
            self.grafo.definir_peso_vertice(user, total_interactions)
            self.grafo.definir_rotulo_vertice(user, user)
        
        # Adiciona arestas (interações)
        for source, targets in all_interactions.items():
            for target, weight in targets.items():
                self.grafo.adicionar_aresta(source, target, peso=weight)
        
        print("Grafo social construído com sucesso!")
        print(f"Total de usuários: {self.grafo.quantidade_vertices()}")
        print(f"Total de interações: {self.grafo.quantidade_arestas()}")
    
    def export_to_csv(self, filename: str = 'SocialGraph.csv'):
        """Exporta o grafo social para CSV"""
        if self.grafo is None:
            raise Exception("Grafo não construído. Execute build_graph() primeiro.")
        
        self.grafo.exportar_csv(filename)
        print(f"Grafo exportado para {filename}")
    
    def plot_graph(self):
        """Plota o grafo social (usando nossa implementação, não NetworkX)"""
        if self.grafo is None:
            raise Exception("Grafo não construído. Execute build_graph() primeiro.")
        
        self.grafo.plotar()

# Exemplo de uso
if __name__ == "__main__":
    load_dotenv()
    if not os.getenv('GITHUB_KEY'):
        print("Erro: GITHUB_KEY não encontrada no arquivo .env")
        exit(1)
    if not os.getenv('REPOSITORIO'):
        print("Erro: REPOSITORIO não encontrado no arquivo .env")
        exit(1)
    
    SocialGraph = SocialGraph()
    SocialGraph.build_graph()
    SocialGraph.export_to_csv()
    SocialGraph.plot_graph()