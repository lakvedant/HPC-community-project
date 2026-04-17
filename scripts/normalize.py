#!/usr/bin/env python3
import sys

def normalize(input_file, output_file):
    print(f"Normalizing nodes in {input_file} to be contiguous...")
    node_map = {}
    next_id = 0
    
    with open(input_file, 'r') as fin, open(output_file, 'w') as fout:
        for line in fin:
            if line.startswith("#"):
                continue
            parts = line.strip().split()
            if len(parts) >= 2:
                u, v = int(parts[0]), int(parts[1])
                
                if u not in node_map:
                    node_map[u] = next_id
                    next_id += 1
                if v not in node_map:
                    node_map[v] = next_id
                    next_id += 1
                    
                fout.write(f"{node_map[u]} {node_map[v]}\n")
                
    print(f"Done! Mapped {next_id} unique nodes. Saved to {output_file}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <input.txt> <output.txt>")
        sys.exit(1)
    normalize(sys.argv[1], sys.argv[2])
