import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;

class GrafoListaAdjacencia implements Grafo {
    private List<List<Integer>> listaAdjacencia;
    private int numeroVertices;
    private int numeroArestas;
    private String[] rotulosVertices;
    private int[] pesosVertices;
    private Map<String, String> rotulosArestas; 
    private Map<String, Integer> pesosArestas; 

    public GrafoListaAdjacencia(int numeroVertices) {
        this.numeroVertices = numeroVertices;
        this.numeroArestas = 0;
        this.listaAdjacencia = new ArrayList<>(numeroVertices);
        this.rotulosVertices = new String[numeroVertices];
        this.pesosVertices = new int[numeroVertices];
        this.rotulosArestas = new HashMap<>();
        this.pesosArestas = new HashMap<>();

        for (int i = 0; i < numeroVertices; i++) {
            listaAdjacencia.add(new LinkedList<>());
        }
    }

    @Override
    public void adicionarAresta(int origem, int destino) {
        if (origem >= 0 && origem < numeroVertices && destino >= 0 && destino < numeroVertices) {
            if (!listaAdjacencia.get(origem).contains(destino)) {
                listaAdjacencia.get(origem).add(destino);
                numeroArestas++;
            }
        }
    }

    @Override
    public void removerAresta(int origem, int destino) {
        if (origem >= 0 && origem < numeroVertices && destino >= 0 && destino < numeroVertices) {
            if (listaAdjacencia.get(origem).remove(Integer.valueOf(destino))) {
                numeroArestas--;
                rotulosArestas.remove(origem + "-" + destino);
                pesosArestas.remove(origem + "-" + destino);
            }
        }
    }

    @Override
    public void adicionarArestaPonderada(int origem, int destino, int peso) {
        if (origem >= 0 && origem < numeroVertices && destino >= 0 && destino < numeroVertices) {
            if (!listaAdjacencia.get(origem).contains(destino)) {
                listaAdjacencia.get(origem).add(destino);
                pesosArestas.put(origem + "-" + destino, peso);
                numeroArestas++;
            }
        }
    }

    @Override
    public boolean existeAresta(int origem, int destino) {
        if (origem >= 0 && origem < numeroVertices && destino >= 0 && destino < numeroVertices) {
            return listaAdjacencia.get(origem).contains(destino);
        }
        return false;
    }

    @Override
    public boolean saoAdjacentes(int vertice1, int vertice2) {
        if (vertice1 >= 0 && vertice1 < numeroVertices && vertice2 >= 0 && vertice2 < numeroVertices) {
            return listaAdjacencia.get(vertice1).contains(vertice2) ||
                    listaAdjacencia.get(vertice2).contains(vertice1);
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
        return false;
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
            if (listaAdjacencia.get(origem).contains(destino)) {
                rotulosArestas.put(origem + "-" + destino, rotulo);
            }
        }
    }

    @Override
    public String getRotuloAresta(int origem, int destino) {
        if (origem >= 0 && origem < numeroVertices && destino >= 0 && destino < numeroVertices) {
            if (listaAdjacencia.get(origem).contains(destino)) {
                return rotulosArestas.get(origem + "-" + destino);
            }
        }
        return null;
    }

    @Override
    public void setPesoAresta(int origem, int destino, int peso) {
        if (origem >= 0 && origem < numeroVertices && destino >= 0 && destino < numeroVertices) {
            if (listaAdjacencia.get(origem).contains(destino)) {
                pesosArestas.put(origem + "-" + destino, peso);
            }
        }
    }

    @Override
    public int getPesoAresta(int origem, int destino) {
        if (origem >= 0 && origem < numeroVertices && destino >= 0 && destino < numeroVertices) {
            if (listaAdjacencia.get(origem).contains(destino)) {
                Integer peso = pesosArestas.get(origem + "-" + destino);
                return peso != null ? peso : 0;
            }
        }
        return 0;
    }

    @Override
    public void imprimirGrafo() {
        System.out.println("Lista de Adjacência:");
        for (int i = 0; i < numeroVertices; i++) {
            System.out.print("Vértice " + i + ": ");
            for (Integer vizinho : listaAdjacencia.get(i)) {
                System.out.print(vizinho + " ");
            }
            System.out.println();
        }

        System.out.println("\nRótulos dos Vértices:");
        for (int i = 0; i < numeroVertices; i++) {
            System.out
                    .println("Vértice " + i + ": " + (rotulosVertices[i] != null ? rotulosVertices[i] : "Sem rótulo"));
        }

        System.out.println("\nPesos e Rótulos das Arestas:");
        for (int i = 0; i < numeroVertices; i++) {
            for (Integer j : listaAdjacencia.get(i)) {
                String chave = i + "-" + j;
                System.out.println("Aresta " + i + "->" + j + ": Peso = " +
                        (pesosArestas.containsKey(chave) ? pesosArestas.get(chave) : 0) +
                        ", Rótulo = " + (rotulosArestas.containsKey(chave) ? rotulosArestas.get(chave) : "Sem rótulo"));
            }
        }
    }
}