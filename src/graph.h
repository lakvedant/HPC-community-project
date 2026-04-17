#ifndef GRAPH_H
#define GRAPH_H

#include <stdint.h>
#include <stdio.h>

typedef struct {
    int v;
    float weight;
} Edge;

typedef struct {
    int num_nodes;
    int num_edges;
    int *row_ptr;      // CSR row pointers (size: num_nodes + 1)
    Edge *col_idx;     // CSR column indices & weights (size: num_edges)
    float *node_weights; // Weighted degree of each node
    float total_weight;
} Graph;

// Function prototypes
Graph* load_graph(const char *filename);
void free_graph(Graph *g);

#endif
