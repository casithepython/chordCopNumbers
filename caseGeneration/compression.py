import networkx as nx

def get_previous_node(graph, vertexIndex):
    """get_previous_node(Graph, int) -> int
    Returns the node before vertexIndex on the cycle,
    looping back around to the end if necessary"""
    vertices = list(graph.nodes())
    if vertexIndex == 0:
        previousVertex = vertices[len(vertices) - 1]
    else:
        previousVertex = vertices[vertexIndex - 1]
    return previousVertex


def get_next_node(graph, vertexIndex):
    """get_next_node(Graph, int) -> int
        Returns the node after vertexIndex on the cycle,
        looping back around to the beginning if necessary"""
    vertices = list(graph.nodes())
    if vertexIndex == len(vertices) - 1:
        nextVertex = vertices[0]
    else:
        nextVertex = vertices[vertexIndex + 1]
    return nextVertex


def get_vertices_to_remove(graph):
    """get_adjacent_degree_twos(Graph) -> list
    Returns a list of all vertices to remove
    These are all vertices x such that deg(x) = 2 and
    the next vertex x_2 on the cycle has deg(x_2) = 2."""
    verticesToRemove = []
    degrees = list(nx.degree(graph))
    degrees.sort()
    vertices = list(nx.nodes(graph))
    vertices.sort()

    # Go through all the degrees
    for degreeIndex in range(len(degrees)):
        if degreeIndex == len(degrees) - 1:  # If we're looping around, set the second index to 0
            secondDegreeIndex = 0
        else:  # Otherwise pick the next index
            secondDegreeIndex = degreeIndex + 1

        # If both vertices have degree 2, we should remove the first
        if 2 == degrees[degreeIndex][1] == degrees[secondDegreeIndex][1]:
            verticesToRemove.append(vertices[degreeIndex])
    return verticesToRemove


def remove_and_rejoin(graph, vertex):
    """remove_and_rejoin(Graph, int) -> None
    Removes vertex from graph and draws an edge
    between the vertices behind and in front of vertex
    on the cycle"""
    vertices = list(nx.nodes(graph))
    vertices.sort()
    vertexIndex = vertices.index(vertex)

    # Add the edge
    graph.add_edge(get_previous_node(graph, vertexIndex), get_next_node(graph, vertexIndex))

    # Remove the vertex
    # DO NOT reverse this and the previous step, since then it draws an edge between the
    # wrong vertices
    graph.remove_node(vertex)


def compress_graph(chordGraph):
    """compress_graph(chordGraph) -> NetworkX.Graph
    Identifies all pairs of adjacent vertices where
    both vertices have degree 2"""
    indicesToModify = get_vertices_to_remove(chordGraph) # Get indices to remove
    for vertex in indicesToModify:
        remove_and_rejoin(chordGraph, vertex)
    return chordGraph