# Get a lock
# Spawn processes
# For each process: wait for lock to be unlocked. When unlocked, grab k/processes graphs from the generator, then unlock
# Each process maintains a list of unique graphs
# Within each process: for each graph, create it, compress it, and check it against the list of unique graphs

# Once all processes have finished isolating their unique graphs:
# Recursively:
# Half the processes send unique graphs to the other half of the processes
# The sending processes close
# The receiving processes merge the lists while checking for isomorphism
# Repeat until there's only one list remaining

# ------------------------
# Imports
# ------------------------
import itertools
import math
import multiprocessing

from processFunctions import *
from utility import chunks


def init(n, numProcesses):
    # ------------------------
    # Creating generator
    # ------------------------
    # We only allow edges to be drawn between every other vertex so we never have two adjacent chord vertices
    chordVertices = list(range(1, 4 * n + 1, 2))

    # Generate all possible chord sets
    # Each chord set contains exactly three distinct chords
    possibleChords = iter(itertools.combinations(chordVertices, 2))
    possibleChordSets = iter(itertools.combinations(possibleChords, n))

    numSets = math.comb(2 * (n ** 2) - n, n)  # ((2n^2 - n) CHOOSE n) happens to be the working formula

    chunkSize = math.ceil(numSets / numProcesses)
    print("Chunk size: ", chunkSize)

    chordSetsChunks = iter(chunks(possibleChordSets, chunkSize))
    return chordSetsChunks


# ------------------------
# Creating the processes and assigning lists
# ------------------------

def generate_unique(n, chordSetsChunks, numProcesses):
    processes = []
    for processIndex in range(numProcesses):
        newProcess = GraphCruncher(processID=processIndex, n=n)
        processes.append(newProcess)

    queue = mp.Queue()

    for process in processes:
        process.start()

    for chunk in chordSetsChunks:
        queue.put(list(chunk))

    for process in processes:
        process.compute_unique_graphs(queue)

    for process in processes:
        print("Chunk", process.get_processID(), "completed, found", process.get_num_unique_graphs(), "unique graphs")
    gc.collect()
    return processes


# Merging code
# ------------------------

# Send graphs from half the processes to the other half

def merge_unique_graph_lists(processes):
    numProcessesToKeep = len(processes)
    howOftenToTake = 2
    counter = 1
    queue = multiprocessing.Queue()
    while howOftenToTake < numProcessesToKeep + 1:
        print("Iteration", counter, " of merging beginning.")
        for process in processes:
            if process.get_processID() % howOftenToTake != 0:
                process.send_unique_graphs(queue)
                process.join()
                processes.remove(process)
        for process in processes:
            process.get_new_graphs_and_merge(queue)
        howOftenToTake *= 2
        gc.collect()
        print("Iteration", counter, " of merging completed.")
        counter += 1
    return processes[0].get_unique_graphs()


# Close sending processes

# Merge lists on receiving processes

# Repeat recursively

# ------------------------
# Run
# ------------------------
if __name__ == "__main__":
    # ------------------------
    # Configuration
    # ------------------------
    n = 3
    numProcesses = mp.cpu_count()
    print("Processes: ", numProcesses)

    chordSetsChunks = init(n, numProcesses)

    processes = generate_unique(n, chordSetsChunks, numProcesses)
    print("Finished initial graph generation and checking. Commencing merging.")
    results = merge_unique_graph_lists(processes)
    print("Completed merging.")
    print(len(results))
