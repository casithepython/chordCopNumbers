import gc
import multiprocessing as mp

from compression import compress_graph
from generation import generate_chordal_graph
from isomorphism import isIsomorphicDuplicate


class GraphCruncher(mp.Process):

    def __init__(self, processID, n):
        super().__init__()
        self.n = n
        self.uniqueGraphs = []
        self.processID = processID

    def get_n(self):
        return self.n

    def get_processID(self):
        return self.processID

    def compute_unique_graphs(self, queue):
        chordSetsChunk = queue.get() # Get a chunk of chord sets from the queue
        for chordSet in chordSetsChunk: # Go through each chord set
            # Create and compress graph
            graph = compress_graph(generate_chordal_graph(self.get_n(), chordSet))
            # Check for isomorphism
            isNew = True

            # If the graph is unique, add it to the list of unique graphs
            for uniqueGraph in self.get_unique_graphs():
                if isIsomorphicDuplicate(uniqueGraph, graph):
                    isNew = False
                    break
            if isNew:
                self.add_unique_graph(graph)
        gc.collect()

    def get_unique_graphs(self):
        return self.uniqueGraphs

    def add_unique_graph(self, graph):
        self.uniqueGraphs.append(graph)

    def get_num_unique_graphs(self):
        return len(self.get_unique_graphs())

    def send_unique_graphs(self, queue):
        queue.put(self.get_unique_graphs())


    def get_new_graphs_and_merge(self, queue):
        newSet = queue.get()
        self.add_unique_graphs_without_duplicates(newSet)

    def add_unique_graphs_without_duplicates(self, newUniqueGraphs):
        # NOTE: this assumes that all graphs in secondUniqueGraphs are non-isomorphic to each other
        newGraphsNotDuplicates = []
        for newUniqueGraph in newUniqueGraphs: # For each new graph
            # If it's unique, we add it to the newGraphsNotDuplicates list
            # We don't add it to the unique graphs immediately, because then
            # we would be checking new graphs against it when we know they're already distinct.
            isUnique = True
            for oldUniqueGraph in self.get_unique_graphs():
                if isIsomorphicDuplicate(newUniqueGraph, oldUniqueGraph):
                    isUnique = False
                    break
            if isUnique:
                newGraphsNotDuplicates.append(newUniqueGraph)
        # Shift over all the newGraphsNotDuplicates to the unique graph list
        for graph in newGraphsNotDuplicates:
            self.add_unique_graph(graph)
        del newGraphsNotDuplicates
        gc.collect()
