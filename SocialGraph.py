import os
from dotenv import load_dotenv
import requests
import json
import time
from typing import Dict, List, Optional
from grafo import Grafo

load_dotenv()

class SocialGraph:
    def __init__(self):
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
    
    def build_graph(self):
        """Constrói o grafo social a partir das interações no repositório"""
        print("Iniciando construção do grafo social...")
        
        all_interactions = {}
        cursor = None
        has_next_page = True
        request_count = 0
        
        while has_next_page and request_count < 10:
            request_count += 1
            print(f"Realizando requisição {request_count}...")
            
            try:
                data = self._get_issues_and_prs(cursor)
                batch_interactions = self._process_interactions(data)
                
                # Merge batch results
                for user, targets in batch_interactions.items():
                    if user not in all_interactions:
                        all_interactions[user] = {}
                    for target, weight in targets.items():
                        all_interactions[user][target] = all_interactions[user].get(target, 0) + weight
                
                # Update pagination info
                issues_page_info = data['data']['repository']['issues']['pageInfo']
                has_next_page = issues_page_info['hasNextPage']
                cursor = issues_page_info['endCursor']
                
                time.sleep(1)
                
            except Exception as e:
                print(f"Erro durante a coleta de dados: {str(e)}")
                break
        
        # Create graph
        self.grafo = Grafo(representacao='lista')
        
        # Collect all users
        all_users = set(all_interactions.keys())
        for targets in all_interactions.values():
            all_users.update(targets.keys())
        
        if not all_users:
            print("Nenhum dado de usuário encontrado. Verifique se o repositório tem issues/PRs.")
            return
        
        # Add vertices
        for user in all_users:
            # Calculate total activity (outgoing + incoming)
            out_degree = sum(all_interactions.get(user, {}).values())
            in_degree = sum(interactions.get(user, 0) 
                          for interactions in all_interactions.values())
            total_activity = out_degree + in_degree
            
            self.grafo.adicionar_vertice(user, peso=total_activity, rotulo=user)
        
        # Add edges
        for source, targets in all_interactions.items():
            for target, weight in targets.items():
                self.grafo.adicionar_aresta(source, target, peso=weight)
        
        print("\nGrafo social construído com sucesso!")
        print(f"Total de usuários: {self.grafo.quantidade_vertices()}")
        print(f"Total de interações: {self.grafo.quantidade_arestas()}\n")
    
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