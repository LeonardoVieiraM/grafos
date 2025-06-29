# Grafo e SocialGraph - Documentação Completa

Este repositório contém duas classes principais para manipulação e análise de grafos em Python: `Grafo` (um grafo genérico) e `SocialGraph` (especializado para redes sociais).

Este repositório também possui o vídeo de apresentação da aplicação, respondendo as perguntas obrigatórias do projeto.

---

## Classe Grafo.py

A classe `Grafo` implementa uma estrutura de dados para grafos com suporte a múltiplas representações e operações básicas.

### Funcionalidades Grafo.py

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

### Métodos Principais Grafo.py

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

# Classe SocialGraph.py

A classe `SocialGraph` é uma implementação especializada para análise de redes sociais em repositórios GitHub, construída sobre a classe `Grafo` básica. Ela coleta dados de interações através da API do GitHub e fornece métodos avançados para análise de redes sociais.

## Funcionalidades SocialGraph.py
- **Coleta de Dados**:
  - Integração direta com a API GraphQL do GitHub
  - Coleta automática de interações em issues e pull requests
  - Paginação de resultados para coletar dados completos

- **Análise de Rede**:
  - Identificação de usuários influentes
  - Detecção de fragmentação na rede
  - Análise de comunidades/grupos naturais
  - Cálculo de métricas de conexão
  - Busca por relações próximas

- **Visualização e Exportação**:
  - Plotagem gráfica do grafo social
  - Exportação para formatos CSV e GEXF (Gephi)
  - Menu interativo para análise


## Métodos Principais SocialGraph.py

### Construção do Grafo

| Método | Descrição |
|--------|-----------|
| `__init__(representation='matriz')` | Inicializa com credenciais do GitHub |
| `build_graph(min_interactions=50)` | Constrói o grafo a partir dos dados do GitHub |

### Análise de Rede

| Método | Descrição |
|--------|-----------|
| `usuarios_mais_influentes(top_n=5)` | Retorna os usuários mais influentes |
| `remover_maior_fragmentador()` | Remove o vértice que mais fragmenta o grafo |
| `grupos_naturais(n_grupos=3)` | Identifica comunidades no grafo |
| `nivel_conexao()` | Calcula o percentual de conexão da rede |
| `usuarios_proximos(usuario, n=5)` | Encontra usuários próximos a um dado usuário |
| `usuarios_proximos_nao_interagem(usuario, n=5)` | Encontra conexões ausentes |

### Visualização e Exportação

| Método | Descrição |
|--------|-----------|
| `plot_graph()` | Visualiza o grafo social |
| `export_to_csv(filename)` | Exporta para arquivo CSV |
| `export_to_gephi(filename)` | Exporta para formato Gephi (GEXF) |

### Interface Interativa

| Método | Descrição |
|--------|-----------|
| `run_analysis_menu()` | Menu interativo para análise do grafo |

## Requisitos

- Python 3.8+
- Pacotes necessários:
  ```bash
  python-dotenv
  requests
  matplotlib
  ```

## Configuração

1. Crie um arquivo `.env` na raiz do projeto com:
   ```
   GITHUB_KEY=seu_token_github
   REPOSITORIO=owner/nome_repositorio
   ```
2. O token GitHub precisa ter permissões para ler repositórios

## Análises Disponíveis

1. **Influência**: Identifica membros com maior impacto na rede
2. **Fragmentação**: Detecta nós que dividem a rede
3. **Comunidades**: Revela grupos naturais de interação
4. **Conexão**: Mede o grau de conectividade da rede
5. **Proximidade**: Aponta usuários próximos no grafo, com ou sem conexões entre si



