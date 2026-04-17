#!/usr/bin/env python3
import networkx as nx
import matplotlib.pyplot as plt
import sys
import random
from collections import Counter

def load_graph(edge_file):
    print(f"Loading graph edges from {edge_file}...")
    G = nx.read_edgelist(edge_file, nodetype=int)
    return G

def load_communities(community_file):
    print(f"Loading communities from {community_file}...")
    node_to_comm = {}
    with open(community_file, 'r') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) == 2:
                node_to_comm[int(parts[0])] = int(parts[1])
    return node_to_comm

def calculate_modularity(G, node_to_comm):
    print("Calculating true modularity score (this takes intense O(E) math)...")
    try:
        from networkx.algorithms.community import modularity
        # Group nodes by community ID
        comm_id_to_nodes = {}
        for node, comm in node_to_comm.items():
            if node in G:
                comm_id_to_nodes.setdefault(comm, []).append(node)
        communities = list(comm_id_to_nodes.values())
        mod_score = modularity(G, communities)
        print(f"=========================================")
        print(f"  🏆 TRUE MODULARITY SCORE: {mod_score:.4f}")
        print(f"=========================================")
        return mod_score
    except Exception as e:
        print(f"Modularity calculation failed (usually graph formatting missing isolated nodes): {e}")
        return None

def visualize(edge_file, community_file):
    G = load_graph(edge_file)
    node_to_comm = load_communities(community_file)
    
    # Check if we have communities, else fallback to 1 community
    if not node_to_comm:
        print("No communities found, defaulting all to 0.")
        node_to_comm = {n: 0 for n in G.nodes()}

    # Print out distribution stats
    comm_sizes = Counter(node_to_comm.values())
    print("\n--- Community Statistics ---")
    print(f"Total Unique Communities Detected: {len(comm_sizes)}")
    
    # Filter out empty communities or nodes not in graph
    valid_comm_sizes = {c: s for c, s in comm_sizes.items() if s > 1}
    print(f"Communities with >1 user: {len(valid_comm_sizes)}")
    
    largest = comm_sizes.most_common(5)
    print("\nLargest Communities by User Count:")
    for i, (comm, size) in enumerate(largest, 1):
        print(f"  {i}. Community [{comm}] -> {size} users")
    print("---------------------------\n")

    calculate_modularity(G, node_to_comm)

    # 1. Plot Histogram of sizes
    plt.figure(figsize=(10, 6))
    sizes = list(comm_sizes.values())
    plt.hist(sizes, bins=50, color='#3F2965', alpha=0.7)
    plt.yscale('log')
    plt.title("Community Size Distribution (Log-Scale)")
    plt.xlabel("Number of Users in Community")
    plt.ylabel("Number of Communities")
    plt.tight_layout()
    plt.savefig("community_histogram.png", dpi=200)
    print("Saved histogram to 'community_histogram.png'")

    # 2. Plot Network Diagram
    communities = set(node_to_comm.values())
    
    random.seed(42)
    comm_colors = {c: [random.random(), random.random(), random.random()] for c in communities}
    node_colors = [comm_colors[node_to_comm.get(node, 0)] for node in G.nodes()]

    print("Computing force-directed network layout...")
    
    # Subgraph for dense network rendering to save time
    if len(G) > 3000:
        print("Taking a 2500-node subgraph to speed up drawing process...")
        nodes = list(G.nodes())[:2500]
        G = G.subgraph(nodes)
        node_colors = [comm_colors[node_to_comm.get(node, 0)] for node in G.nodes()]

    pos = nx.spring_layout(G, seed=42)
    
    plt.figure(figsize=(12, 12))
    nx.draw_networkx_nodes(G, pos, node_size=20, node_color=node_colors, alpha=0.8)
    nx.draw_networkx_edges(G, pos, alpha=0.1)
    
    plt.title("Parallel Louvain Community Clusters")
    plt.axis("off")
    plt.tight_layout()
    
    plt.savefig("graph_clusters.png", dpi=300)
    print("Saved network map to 'graph_clusters.png'")
    print("\nVisualizations completed!")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <edges.txt> <output_communities.txt>")
        sys.exit(1)
        
    visualize(sys.argv[1], sys.argv[2])
