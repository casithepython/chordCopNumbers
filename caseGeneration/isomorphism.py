import networkx as nx


def isIsomorphicDuplicate(graph1, graph2):
    if nx.faster_could_be_isomorphic(graph1, graph2):
        if nx.fast_could_be_isomorphic(graph1, graph2):
            if nx.is_isomorphic(graph1, graph2):
                return True
    return False