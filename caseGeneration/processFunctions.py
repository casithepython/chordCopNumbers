import multiprocessing

from caseGeneration.compression import compress_graph
from caseGeneration.generation import generate_chordal_graph
from caseGeneration.isomorphism import isIsomorphicDuplicate

def compute_unique_graphs(n,chordSets):
    counter = 0
    for chordSet in chordSets:
        counter += 1
    print(counter)
    uniqueGraphs = []
    for chordSet in chordSets:
        counter += 1
        # Create and compress graph
        graph = compress_graph(generate_chordal_graph(n, chordSet))
        # Check for isomorphism
        isNew = True
        if len(uniqueGraphs) != 0:
            for uniqueGraph in uniqueGraphs:
                if isIsomorphicDuplicate(uniqueGraph, graph):
                    isNew = False
                    break
        if isNew:
            uniqueGraphs.append(graph)
    return uniqueGraphs

def get_and_merge(iterable):
    firstSet = next(iterable)
    if not iterable.empty():
        secondSet = next(iterable)
    else:
        secondSet = []
    return merge_lists(firstSet,secondSet)

def merge_lists(uniqueGraphs, secondUniqueGraphs):
    # NOTE: this assumes that all graphs in secondUniqueGraphs are non-isomorphic to each other
    print("First length", len(uniqueGraphs), "Second length", len(secondUniqueGraphs))
    newGraphsInNewList = []
    for newUniqueGraph in secondUniqueGraphs:
        isUnique = True
        for oldUniqueGraph in uniqueGraphs:
            if isIsomorphicDuplicate(newUniqueGraph, oldUniqueGraph):
                isUnique = False
                break
        if isUnique:
            newGraphsInNewList.append(newUniqueGraph)
    print("New graphs found in new list", len(newGraphsInNewList))
    for graph in uniqueGraphs:
        newGraphsInNewList.append(graph)
    return newGraphsInNewList