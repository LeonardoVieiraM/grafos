import java.util.Scanner;

public class BibliotecaGrafos {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        Grafo grafo = null;

        System.out.println("Bem-vindo à Biblioteca de Grafos!");
        System.out.println("Escolha o tipo de representação do grafo:");
        System.out.println("1 - Matriz de Adjacência");
        System.out.println("2 - Lista de Adjacência");
        int tipoGrafo = scanner.nextInt();

        System.out.println("Digite o número de vértices do grafo:");
        int numeroVertices = scanner.nextInt();

        if (tipoGrafo == 1) {
            grafo = new GrafoMatrizAdjacencia(numeroVertices);
        } else if (tipoGrafo == 2) {
            grafo = new GrafoListaAdjacencia(numeroVertices);
        } else {
            System.out.println("Opção inválida!");
            System.exit(0);
        }

        while (true) {
            System.out.println("\nMenu de Operações:");
            System.out.println("1 - Adicionar aresta");
            System.out.println("2 - Remover aresta");
            System.out.println("3 - Adicionar aresta ponderada");
            System.out.println("4 - Verificar existência de aresta");
            System.out.println("5 - Verificar adjacência entre vértices");
            System.out.println("6 - Verificar adjacência entre arestas");
            System.out.println("7 - Verificar incidência entre aresta e vértice");
            System.out.println("8 - Definir rótulo de vértice");
            System.out.println("9 - Obter rótulo de vértice");
            System.out.println("10 - Definir peso de vértice");
            System.out.println("11 - Obter peso de vértice");
            System.out.println("12 - Definir rótulo de aresta");
            System.out.println("13 - Obter rótulo de aresta");
            System.out.println("14 - Definir peso de aresta");
            System.out.println("15 - Obter peso de aresta");
            System.out.println("16 - Verificar se grafo é vazio");
            System.out.println("17 - Verificar se grafo é completo");
            System.out.println("18 - Obter número de vértices");
            System.out.println("19 - Obter número de arestas");
            System.out.println("20 - Imprimir grafo");
            System.out.println("0 - Sair");

            System.out.print("Escolha uma opção: ");
            int opcao = scanner.nextInt();

            switch (opcao) {
                case 1:
                    System.out.println("Digite o vértice de origem e o vértice de destino:");
                    int origem = scanner.nextInt();
                    int destino = scanner.nextInt();
                    grafo.adicionarAresta(origem, destino);
                    break;

                case 2:
                    System.out.println("Digite o vértice de origem e o vértice de destino:");
                    origem = scanner.nextInt();
                    destino = scanner.nextInt();
                    grafo.removerAresta(origem, destino);
                    break;

                case 3:
                    System.out.println("Digite o vértice de origem, o vértice de destino e o peso:");
                    origem = scanner.nextInt();
                    destino = scanner.nextInt();
                    int peso = scanner.nextInt();
                    grafo.adicionarArestaPonderada(origem, destino, peso);
                    break;

                case 4:
                    System.out.println("Digite o vértice de origem e o vértice de destino:");
                    origem = scanner.nextInt();
                    destino = scanner.nextInt();
                    System.out.println("Aresta existe? " + grafo.existeAresta(origem, destino));
                    break;

                case 5:
                    System.out.println("Digite os dois vértices para verificar adjacência:");
                    int vertice1 = scanner.nextInt();
                    int vertice2 = scanner.nextInt();
                    System.out.println("Vértices são adjacentes? " + grafo.saoAdjacentes(vertice1, vertice2));
                    break;

                case 6:
                    System.out.println("Digite a primeira aresta (origem e destino):");
                    int a1Origem = scanner.nextInt();
                    int a1Destino = scanner.nextInt();
                    System.out.println("Digite a segunda aresta (origem e destino):");
                    int a2Origem = scanner.nextInt();
                    int a2Destino = scanner.nextInt();
                    System.out.println("Arestas são adjacentes? " +
                            grafo.arestasSaoAdjacentes(a1Origem, a1Destino, a2Origem, a2Destino));
                    break;

                case 7:
                    System.out.println("Digite a aresta (origem e destino):");
                    int aOrigem = scanner.nextInt();
                    int aDestino = scanner.nextInt();
                    System.out.println("Digite o vértice para verificar incidência:");
                    int v = scanner.nextInt();
                    System.out.println("Aresta incide no vértice? " +
                            grafo.arestaIncideEmVertice(aOrigem, aDestino, v));
                    break;

                case 8:
                    System.out.println("Digite o vértice e o rótulo:");
                    vertice1 = scanner.nextInt();
                    scanner.nextLine(); 
                    String rotulo = scanner.nextLine();
                    grafo.setRotuloVertice(vertice1, rotulo);
                    break;

                case 9:
                    System.out.println("Digite o vértice:");
                    vertice1 = scanner.nextInt();
                    System.out.println("Rótulo: " + grafo.getRotuloVertice(vertice1));
                    break;

                case 10:
                    System.out.println("Digite o vértice e o peso:");
                    vertice1 = scanner.nextInt();
                    peso = scanner.nextInt();
                    grafo.setPesoVertice(vertice1, peso);
                    break;

                case 11:
                    System.out.println("Digite o vértice:");
                    vertice1 = scanner.nextInt();
                    System.out.println("Peso: " + grafo.getPesoVertice(vertice1));
                    break;

                case 12:
                    System.out.println("Digite a aresta (origem e destino) e o rótulo:");
                    origem = scanner.nextInt();
                    destino = scanner.nextInt();
                    scanner.nextLine(); 
                    rotulo = scanner.nextLine();
                    grafo.setRotuloAresta(origem, destino, rotulo);
                    break;

                case 13:
                    System.out.println("Digite a aresta (origem e destino):");
                    origem = scanner.nextInt();
                    destino = scanner.nextInt();
                    System.out.println("Rótulo: " + grafo.getRotuloAresta(origem, destino));
                    break;

                case 14:
                    System.out.println("Digite a aresta (origem e destino) e o peso:");
                    origem = scanner.nextInt();
                    destino = scanner.nextInt();
                    peso = scanner.nextInt();
                    grafo.setPesoAresta(origem, destino, peso);
                    break;

                case 15:
                    System.out.println("Digite a aresta (origem e destino):");
                    origem = scanner.nextInt();
                    destino = scanner.nextInt();
                    System.out.println("Peso: " + grafo.getPesoAresta(origem, destino));
                    break;

                case 16:
                    System.out.println("Grafo é vazio? " + grafo.isVazio());
                    break;

                case 17:
                    System.out.println("Grafo é completo? " + grafo.isCompleto());
                    break;

                case 18:
                    System.out.println("Número de vértices: " + grafo.getNumeroVertices());
                    break;

                case 19:
                    System.out.println("Número de arestas: " + grafo.getNumeroArestas());
                    break;

                case 20:
                    grafo.imprimirGrafo();
                    break;

                case 0:
                    System.out.println("Saindo...");
                    scanner.close();
                    System.exit(0);
                    break;

                default:
                    System.out.println("Opção inválida!");
            }
        }
    }
}