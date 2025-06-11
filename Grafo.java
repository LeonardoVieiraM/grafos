interface Grafo {
    void adicionarAresta(int origem, int destino);

    void removerAresta(int origem, int destino);

    void adicionarArestaPonderada(int origem, int destino, int peso);

    boolean existeAresta(int origem, int destino);

    boolean saoAdjacentes(int vertice1, int vertice2);

    boolean arestasSaoAdjacentes(int aresta1Origem, int aresta1Destino, int aresta2Origem, int aresta2Destino);

    boolean arestaIncideEmVertice(int arestaOrigem, int arestaDestino, int vertice);

    int getNumeroVertices();

    int getNumeroArestas();

    boolean isVazio();

    boolean isCompleto();

    void setRotuloVertice(int vertice, String rotulo);

    String getRotuloVertice(int vertice);

    void setPesoVertice(int vertice, int peso);

    int getPesoVertice(int vertice);

    void setRotuloAresta(int origem, int destino, String rotulo);

    String getRotuloAresta(int origem, int destino);

    void setPesoAresta(int origem, int destino, int peso);

    int getPesoAresta(int origem, int destino);

    void imprimirGrafo();
}