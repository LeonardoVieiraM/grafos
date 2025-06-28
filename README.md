# Grafo e SocialGraph - Documentação Completa

Este repositório contém duas classes principais para manipulação e análise de grafos em Python: `Grafo` (um grafo genérico) e `SocialGraph` (especializado para redes sociais).

## Índice

1. [Classe Grafo](#classe-grafo)
   - [Funcionalidades](#funcionalidades-grafo)
   - [Métodos Principais](#métodos-principais-grafo)

2. [Classe SocialGraph](#classe-socialgraph)
   - [Funcionalidades](#funcionalidades-socialgraph)
   - [Métodos Principais](#métodos-principais-socialgraph)

---

## Classe Grafo

A classe `Grafo` implementa uma estrutura de dados para grafos com suporte a múltiplas representações e operações básicas.

### Funcionalidades Grafo

- **Representações suportadas**:
  - Lista de adjacência (padrão)
  - Matriz de adjacência

- **Operações básicas**:
  - Adição/remoção de vértices e arestas
  - Atribuição de pesos e rótulos a vértices e arestas
  - Verificação de adjacência
  - Cálculo de grau de vértices
  - Obtenção de vizinhos

- **Visualização**:
  - Plotagem do grafo usando matplotlib
  - Layout circular automático

- **Persistência**:
  - Importação/exportação de/para arquivos CSV

### Métodos Principais Grafo

| Método | Descrição |
|--------|-----------|
| `__init__(representacao='lista')` | Inicializa um grafo vazio |
| `adicionar_vertice(v, peso=1, rotulo='')` | Adiciona um vértice ao grafo |
| `adicionar_aresta(u, v, peso=1, rotulo='')` | Adiciona uma aresta entre vértices |
| `remover_vertice(v)` | Remove um vértice e suas arestas |
| `remover_aresta(u, v)` | Remove uma aresta específica |
| `sao_adjacentes_vertices(u, v)` | Verifica se dois vértices são adjacentes |
| `obter_vizinhos(v)` | Retorna os vizinhos de um vértice |
| `grau_vertice(v)` | Calcula o grau de um vértice |
| `quantidade_vertices()` | Retorna o número de vértices |
| `quantidade_arestas()` | Retorna o número de arestas |
| `e_vazio()` | Verifica se o grafo não tem arestas |
| `e_completo()` | Verifica se o grafo é completo |
| `exportar_csv(nome_arquivo)` | Salva o grafo em um arquivo CSV |
| `importar_csv(nome_arquivo)` | Carrega um grafo de um arquivo CSV |
| `plotar()` | Visualiza o grafo graficamente |


---

## Classe SocialGraph

A classe `SocialGraph` estende a funcionalidade básica do `Grafo` para aplicações específicas em redes sociais, com foco em análise de interações em repositórios GitHub.

### Funcionalidades SocialGraph

- **Coleta de dados**:
  - Integração com API do GitHub via GraphQL
  - Coleta de interações em issues e pull requests
  - Paginação automática de resultados

- **Métricas de rede social**:
  - Identificação de usuários influentes
  - Detecção de fragmentação na rede
  - Análise de comunidades/grupos naturais
  - Cálculo de níveis de conexão

- **Visualização e exportação**:
  - Plotagem do grafo social
  - Exportação para Gephi (formato GEXF)
  - Exportação para CSV

- **Interface interativa**:
  - Menu de análise com múltiplas opções

### Métodos Principais SocialGraph

| Método | Descrição |
|--------|-----------|
| `__init__(representation='matriz')` | Inicializa com credenciais do GitHub |
| `build_graph(min_interactions=50)` | Constrói o grafo a partir dos dados do GitHub |
| `run_analysis_menu()` | Menu interativo para análise do grafo |
| `usuarios_mais_influentes(top_n=5)` | Retorna os usuários mais influentes |
| `remover_maior_fragmentador()` | Remove o vértice que mais fragmenta o grafo |
| `grupos_naturais(n_grupos=3)` | Identifica comunidades no grafo |
| `nivel_conexao()` | Calcula o percentual de conexão da rede |
| `usuarios_proximos(usuario, n=5)` | Encontra usuários próximos a um dado usuário |
| `export_to_gephi(filename)` | Exporta para formato Gephi (GEXF) |
| `export_to_csv(filename)` | Exporta para arquivo CSV |
| `plot_graph()` | Visualiza o grafo social |


### Requisitos

- Python 3.8+
- Pacotes necessários:
  ```
  python-dotenv
  requests
  matplotlib
  ```

### Configuração

1. Crie um arquivo `.env` na raiz do projeto com:
   ```
   GITHUB_KEY=seu_token_github
   REPOSITORIO=owner/nome_repositorio
   ```
2. O token GitHub precisa ter permissões para ler repositórios públicos (ou privados, se for o caso)

### Análises Disponíveis no Menu

1. **Usuários mais influentes**: Identifica os membros com maior impacto na rede
2. **Fragmentação**: Detecta e remove nós que causam maior divisão na rede
3. **Grupos naturais**: Revela comunidades que se formam organicamente
4. **Nível de conexão**: Mede quão conectada está a comunidade
5. **Usuários próximos**: Encontra relações indiretas entre membros
