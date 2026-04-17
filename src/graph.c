#include "graph.h"
#include <stdlib.h>
#include <string.h>

Graph* load_graph(const char *filename) {
    FILE *f = fopen(filename, "r");
    if (!f) {
        printf("Error opening %s\n", filename);
        exit(1);
    }
    
    // Simplistic parser for SNAP format. 
    // Two passes: first find max node ID to allocate memory, and count edges per node
    int max_node = -1;
    int u, v;
    int edge_count = 0;
    while (fscanf(f, "%d %d", &u, &v) == 2) {
        if (u > max_node) max_node = u;
        if (v > max_node) max_node = v;
        edge_count++;
    }
    
    int num_nodes = max_node + 1;
    
    // Sanity check to prevent massive Memory/Swap crash if run on unnormalized graph!
    // Example: Twitter node IDs go up to ~568M. This causes arrays of 568M variables to be
    // created, freezing standard machines.
    if (num_nodes > 10000000 && num_nodes > edge_count * 10) {
        printf("ERROR: Graph looks suspiciously sparse/unnormalized! Max Node ID (%d) is vastly larger than edge count (%d).\n", max_node, edge_count);
        printf("Allocating memory for this will likely crash your machine (OOM / swap thrash).\n");
        printf("Please run `python3 scripts/normalize.py <input> <output>` on your dataset before running ./louvain.\n");
        exit(1);
    }

    Graph *g = (Graph*)malloc(sizeof(Graph));
    g->num_nodes = num_nodes;
    g->total_weight = 0;
    
    // Using undirected graph: each edge added twice conceptually, but let's count degrees
    int *degrees = (int*)calloc(num_nodes, sizeof(int));
    rewind(f);
    while (fscanf(f, "%d %d", &u, &v) == 2) {
        degrees[u]++;
        if(u != v) degrees[v]++;
    }
    
    g->row_ptr = (int*)malloc((num_nodes + 1) * sizeof(int));
    g->row_ptr[0] = 0;
    for (int i = 0; i < num_nodes; i++) {
        g->row_ptr[i+1] = g->row_ptr[i] + degrees[i];
    }
    g->num_edges = g->row_ptr[num_nodes];
    g->col_idx = (Edge*)malloc(g->num_edges * sizeof(Edge));
    g->node_weights = (float*)calloc(num_nodes, sizeof(float));
    
    int *current_idx = (int*)malloc(num_nodes * sizeof(int));
    memcpy(current_idx, g->row_ptr, num_nodes * sizeof(int));
    
    rewind(f);
    while (fscanf(f, "%d %d", &u, &v) == 2) {
        int idxU = current_idx[u]++;
        g->col_idx[idxU].v = v;
        g->col_idx[idxU].weight = 1.0f;
        g->node_weights[u] += 1.0f;
        g->total_weight += 1.0f;
        
        if (u != v) {
            int idxV = current_idx[v]++;
            g->col_idx[idxV].v = u;
            g->col_idx[idxV].weight = 1.0f;
            g->node_weights[v] += 1.0f;
            g->total_weight += 1.0f;
        }
    }
    
    free(degrees);
    free(current_idx);
    fclose(f);
    return g;
}

void free_graph(Graph *g) {
    if(g) {
        if(g->row_ptr) free(g->row_ptr);
        if(g->col_idx) free(g->col_idx);
        if(g->node_weights) free(g->node_weights);
        free(g);
    }
}
