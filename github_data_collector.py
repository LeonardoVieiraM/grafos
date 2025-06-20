import requests
import csv
import time
from datetime import datetime
import os

class GitHubDataCollector:
    def __init__(self, owner, repo, token, max_issues=200, delay=1.0):
        self.owner = owner
        self.repo = repo
        self.token = token
        self.max_issues = max_issues
        self.delay = delay
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
        self.base_url = f"https://api.github.com/repos/{owner}/{repo}"
        self.data_dir = "data"
        os.makedirs(self.data_dir, exist_ok=True)
    
    def is_bot(self, user):
        return user.get('type') == 'Bot' or '[bot]' in user.get('login', '')
    
    def fetch_issues(self):
        issues = []
        page = 1
        while len(issues) < self.max_issues:
            url = f"{self.base_url}/issues?state=all&per_page=100&page={page}"
            response = requests.get(url, headers=self.headers)
            if response.status_code != 200:
                print(f"Error fetching issues: {response.status_code}")
                break
            
            page_issues = response.json()
            if not page_issues:
                break
            
            for issue in page_issues:
                if len(issues) >= self.max_issues:
                    break
                
                # Pular issues de bots
                if not self.is_bot(issue['user']):
                    issues.append(issue)
            
            page += 1
            time.sleep(self.delay)
        
        return issues
    
    def fetch_comments(self, comments_url):
        comments = []
        page = 1
        while True:
            url = f"{comments_url}?per_page=100&page={page}"
            response = requests.get(url, headers=self.headers)
            if response.status_code != 200:
                print(f"Error fetching comments: {response.status_code}")
                break
            
            page_comments = response.json()
            if not page_comments:
                break
            
            for comment in page_comments:
                if not self.is_bot(comment['user']):
                    comments.append(comment)
            
            page += 1
            time.sleep(self.delay)
        
        return comments
    
    def fetch_reviews(self, pr_url):
        reviews = []
        review_url = f"{pr_url}/reviews"
        response = requests.get(review_url, headers=self.headers)
        if response.status_code == 200:
            for review in response.json():
                if not self.is_bot(review['user']):
                    reviews.append(review)
            time.sleep(self.delay)
        return reviews
    
    def collect_and_save(self):
        # Coletar issues
        issues = self.fetch_issues()
        
        # Criar arquivos CSV
        with open(f"{self.data_dir}/nodes.csv", 'w', newline='', encoding='utf-8') as nodes_file, \
             open(f"{self.data_dir}/edges.csv", 'w', newline='', encoding='utf-8') as edges_file:
            
            nodes_writer = csv.writer(nodes_file)
            edges_writer = csv.writer(edges_file)
            
            nodes_writer.writerow(['id', 'label'])
            edges_writer.writerow(['source', 'target', 'type', 'weight'])
            
            users = set()
            interactions = {}
            
            for issue in issues:
                # Processar autor da issue
                author = issue['user']['login']
                users.add(author)
                
                # Determinar tipo de interação
                is_pr = 'pull_request' in issue
                interaction_type = 'pr' if is_pr else 'issue'
                
                # Processar comentários
                comments = self.fetch_comments(issue['comments_url'])
                for comment in comments:
                    commenter = comment['user']['login']
                    users.add(commenter)
                    
                    # Registrar interação autor-comentarista
                    key = (author, commenter)
                    interactions[key] = interactions.get(key, 0) + 1
                
                # Processar reviews para PRs
                if is_pr:
                    reviews = self.fetch_reviews(issue['pull_request']['url'])
                    for review in reviews:
                        reviewer = review['user']['login']
                        users.add(reviewer)
                        
                        # Registrar interação autor-reviewer
                        key = (author, reviewer)
                        interactions[key] = interactions.get(key, 0) + 1
                        
                        # Registrar interação entre reviewers (se houver discussão)
                        for other_review in reviews:
                            if review['id'] != other_review['id']:
                                other_reviewer = other_review['user']['login']
                                key = (reviewer, other_reviewer)
                                interactions[key] = interactions.get(key, 0) + 0.5
            
            # Escrever nós
            for user in users:
                nodes_writer.writerow([user, user])
            
            # Escrever arestas
            for (source, target), weight in interactions.items():
                edges_writer.writerow([source, target, 'interaction', weight])
        
        print(f"Data collection complete. Saved {len(users)} users and {len(interactions)} interactions.")

if __name__ == '__main__':
    # Configurações
    TOKEN = "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"  # Substitua pelo seu token
    OWNER = "yt-dlp"
    REPO = "yt-dlp"
    
    collector = GitHubDataCollector(OWNER, REPO, TOKEN, max_issues=200, delay=1.5)
    collector.collect_and_save()