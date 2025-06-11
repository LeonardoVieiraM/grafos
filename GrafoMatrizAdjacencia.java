class GrafoMatrizAdjacencia implements Grafo {
    private int[][] matrizAdjacencia;
    private int numeroVertices;
    private int numeroArestas;
    private String[] rotulosVertices;
    private int[] pesosVertices;
    private String[][] rotulosArestas;
    private int[][] pesosArestas;

    public GrafoMatrizAdjacencia(int numeroVertices) {
        this.numeroVertices = numeroVertices;
        this.numeroArestas = 0;
        this.matrizAdjacencia = new int[numeroVertices][numeroVertices];
        this.rotulosVertices = new String[numeroVertices];
        this.pesosVertices = new int[numeroVertices];
        this.rotulosArestas = new String[numeroVertices][numeroVertices];
        this.pesosArestas = new int[numeroVertices][numeroVertices];

        // Inicializa a matriz com zeros (sem arestas)
        for (int i = 0; i < numeroVertices; i++) {
            for (int j = 0; j < numeroVertices; j++) {
                matrizAdjacencia[i][j] = 0;
                pesosArestas[i][j] = 0;
            }
        }
    }

    @Override
    public void adicionarAresta(int origem, int destino) {
        if (origem >= 0 && origem < numeroVertices && destino >= 0 && destino < numeroVertices) {
            if (matrizAdjacencia[origem][destino] == 0) {
                matrizAdjacencia[origem][destino] = 1;
                numeroArestas++;
            }
        }
    }

    @Override
    public void removerAresta(int origem, int destino) {
        if (origem >= 0 && origem < numeroVertices && destino >= 0 && destino < numeroVertices) {
            if (matrizAdjacencia[origem][destino] == 1) {
                matrizAdjacencia[origem][destino] = 0;
                rotulosArestas[origem][destino] = null;
                pesosArestas[origem][destino] = 0;
                numeroArestas--;
            }
        }
    }

    @Override
    public void adicionarArestaPonderada(int origem, int destino, int peso) {
        if (origem >= 0 && origem < numeroVertices && destino >= 0 && destino < numeroVertices) {
            if (matrizAdjacencia[origem][destino] == 0) {
                matrizAdjacencia[origem][destino] = 1;
                pesosArestas[origem][destino] = peso;
                numeroArestas++;
            }
        }
    }

    @Override
    public boolean existeAresta(int origem, int destino) {
        if (origem >= 0 && origem < numeroVertices && destino >= 0 && destino < numeroVertices) {
            return matrizAdjacencia[origem][destino] == 1;
        }
        return false;
    }

    @Override
    public boolean saoAdjacentes(int vertice1, int vertice2) {
        if (vertice1 >= 0 && vertice1 < numeroVertices && vertice2 >= 0 && vertice2 < numeroVertices) {
            return matrizAdjacencia[vertice1][vertice2] == 1 || matrizAdjacencia[vertice2][vertice1] == 1;
        }
        return false;
    }

    @Override
    public boolean arestasSaoAdjacentes(int aresta1Origem, int aresta1Destino, int aresta2Origem, int aresta2Destino) {
        if (!existeAresta(aresta1Origem, aresta1Destino) || !existeAresta(aresta2Origem, aresta2Destino)) {
            return false;
        }

        return aresta1Origem == aresta2Origem || aresta1Origem == aresta2Destino ||
                aresta1Destino == aresta2Origem || aresta1Destino == aresta2Destino;
    }

    @Override
    public boolean arestaIncideEmVertice(int arestaOrigem, int arestaDestino, int vertice) {
        if (!existeAresta(arestaOrigem, arestaDestino)) {
            return false;
        }
        return arestaOrigem == vertice || arestaDestino == vertice;
    }

    @Override
    public int getNumeroVertices() {
        return numeroVertices;
    }

    @Override
    public int getNumeroArestas() {
        return numeroArestas;
    }

    @Override
    public boolean isVazio() {
        return numeroArestas == 0;
    }

    @Override
    public boolean isCompleto() {
        int maxArestas = numeroVertices * (numeroVertices - 1);
        return numeroArestas == maxArestas;
    }

    @Override
    public void setRotuloVertice(int vertice, String rotulo) {
        if (vertice >= 0 && vertice < numeroVertices) {
            rotulosVertices[vertice] = rotulo;
        }
    }

    @Override
    public String getRotuloVertice(int vertice) {
        if (vertice >= 0 && vertice < numeroVertices) {
            return rotulosVertices[vertice];
        }
        return null;
    }

    @Override
    public void setPesoVertice(int vertice, int peso) {
        if (vertice >= 0 && vertice < numeroVertices) {
            pesosVertices[vertice] = peso;
        }
    }

    @Override
    public int getPesoVertice(int vertice) {
        if (vertice >= 0 && vertice < numeroVertices) {
            return pesosVertices[vertice];
        }
        return 0;
    }

    @Override
    public void setRotuloAresta(int origem, int destino, String rotulo) {
        if (origem >= 0 && origem < numeroVertices && destino >= 0 && destino < numeroVertices) {
            if (matrizAdjacencia[origem][destino] == 1) {
                rotulosArestas[origem][destino] = rotulo;
            }
        }
    }

    @Override
    public String getRotuloAresta(int origem, int destino) {
        if (origem >= 0 && origem < numeroVertices && destino >= 0 && destino < numeroVertices) {
            if (matrizAdjacencia[origem][destino] == 1) {
                return rotulosArestas[origem][destino];
            }
        }
        return null;
    }

    @Override
    public void setPesoAresta(int origem, int destino, int peso) {
        if (origem >= 0 && origem < numeroVertices && destino >= 0 && destino < numeroVertices) {
            if (matrizAdjacencia[origem][destino] == 1) {
                pesosArestas[origem][destino] = peso;
            }
        }
    }

    @Override
    public int getPesoAresta(int origem, int destino) {
        if (origem >= 0 && origem < numeroVertices && destino >= 0 && destino < numeroVertices) {
            if (matrizAdjacencia[origem][destino] == 1) {
                return pesosArestas[origem][destino];
            }
        }
        return 0;
    }

    @Override
    public void imprimirGrafo() {
        System.out.println("Matriz de Adjacência:");
        for (int i = 0; i < numeroVertices; i++) {
            for (int j = 0; j < numeroVertices; j++) {
                System.out.print(matrizAdjacencia[i][j] + " ");
            }
            System.out.println();
        }

        System.out.println("\nRótulos dos Vértices:");
        for (int i = 0; i < numeroVertices; i++) {
            System.out
                    .println("Vértice " + i + ": " + (rotulosVertices[i] != null ? rotulosVertices[i] : "Sem rótulo"));
        }

        System.out.println("\nPesos das Arestas:");
        for (int i = 0; i < numeroVertices; i++) {
            for (int j = 0; j < numeroVertices; j++) {
                if (matrizAdjacencia[i][j] == 1) {
                    System.out.println("Aresta " + i + "->" + j + ": Peso = " + pesosArestas[i][j] +
                            ", Rótulo = " + (rotulosArestas[i][j] != null ? rotulosArestas[i][j] : "Sem rótulo"));
                }
            }
        }
    }
}