import networkx as nx
import itertools
import concurrent.futures
import gc

from matplotlib import pyplot as plt


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def generate_chord_sets(G, possibleChordSets):
    chordGraphs = []
    for set in possibleChordSets:
        currentGraph = G.copy()
        currentGraph.add_edges_from(set)
        chordGraphs.append(currentGraph)
        del (currentGraph)  # for memory
    return chordGraphs


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


def compress_graphs(givenChordGraphs):
    for graph in givenChordGraphs:
        # Go through all the graphs
        # Once again, I'm puzzled but it appears that I need to
        # use the index of the graph rather than for looping through the graph
        indicesToModify = get_vertices_to_remove(graph)
        for vertex in indicesToModify:
            # print("Removing vertex " + str(vertexSet[1]))
            remove_and_rejoin(graph, vertex)
    return givenChordGraphs



    # This is a nice quick isomorphism check - it finds obvious non-isomorphisms quickly
    # Credit to StackOverflow, the source of all programming genius


def isIsomorphicDuplicate(graph1, graph2):
    if nx.faster_could_be_isomorphic(graph1, graph2):
        if nx.fast_could_be_isomorphic(graph1, graph2):
            if nx.is_isomorphic(graph1, graph2):
                return True
    return False


def main(n, threads):
    G = nx.Graph()
    # Configuration
    # ------------------------

    # ------------------------

    # Add all vertices
    for vertex in range(1, 4 * n + 1):
        G.add_node(vertex)

    # Add edges between each consecutive vertex
    for vertex in range(1, 4 * n):
        G.add_edge(vertex, vertex + 1)
    G.add_edge(4 * n, 1)

    # ------------------------
    # Chord drawing

    # We only allow edges to be drawn between every other vertex so we never have two adjacent chord vertices
    chordVertices = list(range(1, 4 * n + 1, 2))

    # Generate all possible chord sets
    # Each chord set contains exactly three distinct chords
    possibleChords = list(itertools.combinations(chordVertices, 2))
    possibleChordSets = list(itertools.combinations(possibleChords, n))

    print("Possible graphs: " + str(len(possibleChordSets)))
    print("\nCommencing graph generation.")
    # Generate the actual graphs from the chord sets
    chordGraphs = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        futures = []
        for subList in chunks(possibleChordSets, threads):
            futures.append(executor.submit(generate_chord_sets, G=G, possibleChordSets=subList))
        for future in concurrent.futures.as_completed(futures):
            for graph in future.result():
                chordGraphs.append(graph)

    print("Graphs generated.")

    originalGraphs = []
    for graph in chordGraphs:
        originalGraphs.append(
            graph.copy())  # Otherwise it just copies a reference. Don't ask me why, but this is the only way I could make this work


    # Compact the graph by identifying adjacent vertices on the cycle with degree 2
    print("\nBeginning graph modification algorithm.")
    # Run the graph identification algorithm
    print("Graphs to compress: ", len(chordGraphs))
    gc.collect()
    compressedGraphs = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        futures = []
        for subList in chunks(chordGraphs, threads):
            futures.append(executor.submit(compress_graphs, givenChordGraphs=subList))
        for future in concurrent.futures.as_completed(futures):
            for graph in future.result():
                compressedGraphs.append(graph)
                del (graph)

    print("Finished modifying graphs.")
    print("Graphs to check for isomorphism: ", len(compressedGraphs))

    # ------------------------
    # Checking for isomorphism

    print("\nBeginning to check isomorphism.")
    gc.collect()
    non_isomorphic = [compressedGraphs[0]]
    for newGraph in compressedGraphs[1:]:
        isNew = True
        for oldGraph in non_isomorphic:
            if isIsomorphicDuplicate(oldGraph, newGraph):
                isNew = False
        if isNew:
            non_isomorphic.append(newGraph)

    print("Checked for isomorphism.")
    # ------------------------
    # Display
    # ------------------------
    print(str(len(non_isomorphic)) + " unique graphs exist with " + str(n) + " chords.")
    return {"Number of unique graphs:": len(non_isomorphic)}

main(3,9)