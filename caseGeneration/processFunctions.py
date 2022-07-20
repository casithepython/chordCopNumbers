import multiprocessing as mp

from caseGeneration.compression import compress_graph
from caseGeneration.generation import generate_chordal_graph
from caseGeneration.isomorphism import isIsomorphicDuplicate


class GraphCruncher(mp.Process):

    def __init__(self, processID, n):
        super().__init__()
        self.n = n
        self.uniqueGraphs = []
        self.processID = processID

    def n(self):
        return self.n

    def compute_unique_graphs(self, queue):
        chordSetsChunk = queue.get()
        for chordSet in chordSetsChunk:
            # Create and compress graph
            graph = compress_graph(generate_chordal_graph(self.n(), chordSet))
            # Check for isomorphism
            isNew = True
            if self.get_num_unique_graphs() != 0:
                for uniqueGraph in self.get_unique_graphs():
                    if isIsomorphicDuplicate(uniqueGraph, graph):
                        isNew = False
                        break
            if isNew:
                self.add_unique_graph(graph)

    def get_unique_graphs(self):
        return self.uniqueGraphs

    def add_unique_graph(self, graph):
        self.uniqueGraphs.append(graph)

    def get_num_unique_graphs(self):
        return len(self.get_unique_graphs())

    def send_unique_graphs(self, queue):
        queue.put(self.get_unique_graphs())
        self.terminate()

    def get_new_graphs_and_merge(self, queue):
        newSet = queue.get()
        self.add_unique_graphs_without_duplicates(newSet)

    def add_unique_graphs_without_duplicates(self, newUniqueGraphs):
        # NOTE: this assumes that all graphs in secondUniqueGraphs are non-isomorphic to each other
        print("First length", self.get_num_unique_graphs(), "Second length", len(newUniqueGraphs))
        newGraphsNotDuplicates = []
        for newUniqueGraph in newUniqueGraphs:
            isUnique = True
            for oldUniqueGraph in self.get_unique_graphs():
                if isIsomorphicDuplicate(newUniqueGraph, oldUniqueGraph):
                    isUnique = False
                    break
            if isUnique:
                newGraphsNotDuplicates.append(newUniqueGraph)
        print("New graphs found in new list", len(newGraphsNotDuplicates))
        for graph in newGraphsNotDuplicates:
            self.add_unique_graph(graph)
