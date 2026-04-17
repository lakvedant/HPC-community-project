#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <mpi.h>
#include <omp.h>
#include "graph.h"
#include "louvain.h"

int main(int argc, char **argv) {
    int rank = 0, size = 1;
    
    // Initialize MPI
    MPI_Init(&argc, &argv);
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);

    if (argc < 2) {
        if (rank == 0) {
            printf("Usage: %s <edge_list.txt>\n", argv[0]);
        }
        MPI_Finalize();
        return 1;
    }

    if (rank == 0) {
        printf("Loading graph from %s...\n", argv[1]);
    }

    Graph *g = load_graph(argv[1]);
    
    if (rank == 0) {
        printf("Graph loaded: %d nodes, %d edges\n", g->num_nodes, g->num_edges);
    }
    
    int *communities = (int*)malloc(g->num_nodes * sizeof(int));
    double start_time, end_time;

    // Run Serial Baseline (Rank 0 only and only for np=1 to avoid redundant heavy computation)
    if (rank == 0 && size == 1) {
        printf("\n--- Running Serial Louvain Baseline ---\n");
        start_time = omp_get_wtime();
        float mod_serial = louvain_serial(g, communities);
        end_time = omp_get_wtime();
        printf("Serial Runtime: %.3fs\n", end_time - start_time);
        printf("Serial Modularity: %.3f\n", mod_serial);
    }

    // Barrier before parallel
    MPI_Barrier(MPI_COMM_WORLD);
    
    int num_threads = 1;
    #pragma omp parallel
    {
        #pragma omp single
        num_threads = omp_get_num_threads();
    }

    if (rank == 0) {
        printf("\n--- Running Parallel Louvain (MPI + OpenMP) ---\n");
        printf("MPI Processes: %d | OpenMP Threads per process: %d\n", size, num_threads);
    }
    
    start_time = omp_get_wtime();
    float mod_parallel = louvain_parallel(g, communities, rank, size);
    end_time = omp_get_wtime();
    
    if (rank == 0) {
        printf("Parallel Runtime: %.3fs\n", end_time - start_time);
        printf("Parallel Modularity: %.3f\n", mod_parallel);
        
        // Write output communities
        FILE *out = fopen("output_communities.txt", "w");
        if (out) {
            for (int i = 0; i < g->num_nodes; i++) {
                fprintf(out, "%d %d\n", i, communities[i]);
            }
            fclose(out);
            printf("Saved community mapping to output_communities.txt\n");
        }
    }

    free(communities);
    free_graph(g);
    MPI_Finalize();
    return 0;
}
