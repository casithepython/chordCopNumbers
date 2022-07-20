import networkx as nx


def generate_chordal_graph(n, chordSet):
    """generate_chordal_graph(n, chordSet) -> NetworkX.Graph
    Returns a cyclic graph of order n with all chords as
    specified in chordSet"""
    G = nx.Graph()
    # Add all vertices
    for vertex in range(1, 4 * n + 1):
        G.add_node(vertex)

    # Add edges between each consecutive vertex
    for vertex in range(1, 4 * n):
        G.add_edge(vertex, vertex + 1)
    G.add_edge(4 * n, 1)

    G.add_edges_from(chordSet)
    return G