#ifndef LOUVAIN_H
#define LOUVAIN_H

#include "graph.h"

// Computes community structure sequentially
float louvain_serial(Graph *g, int *communities);

// Computes community structure using OpenMP + MPI
// Note: rank and size should be passed after MPI_Init
float louvain_parallel(Graph *g, int *communities, int rank, int size);

#endif
