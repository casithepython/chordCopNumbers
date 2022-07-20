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
    # Create the processes
    processes = []
    for processIndex in range(numProcesses):
        newProcess = GraphCruncher(processID=processIndex, n=n)
        processes.append(newProcess)

    queue = mp.Queue()

    # Start all processes
    for process in processes:
        process.start()

    # Put the chunks in the queue
    for chunk in chordSetsChunks:
        queue.put(list(chunk))

    # Compute the unique graphs
    for process in processes:
        process.compute_unique_graphs(queue)

    # Bit of user output to make sure everything is A-OK
    for process in processes:
        print("Chunk", process.get_processID(), "completed, found", process.get_num_unique_graphs(), "unique graphs")
    gc.collect() # Cleanup

    return processes


# Merging code
# ------------------------

# Send graphs from half the processes to the other half

def merge_unique_graph_lists(processes):
    numProcessesToKeep = len(processes)
    howOftenToTake = 2  # If this is 2, we take every other, and so on and so forth

    counter = 1  # This is just so the user knows that the program is working

    queue = multiprocessing.Queue()

    while howOftenToTake < numProcessesToKeep + 1:  # They are equal in the last iteration
        print("Iteration", counter, " of merging beginning.")

        # For every other process
        # Send its graphs into the queue, join it, and remove it from the list
        for process in processes:  # For some reason, using [::2] is slower than using modulo. idk
            if process.get_processID() % howOftenToTake != 0:  # Select every other (using process ID)
                process.send_unique_graphs(queue)
                process.join()
                processes.remove(process)

        # For every remaining process
        # Take a new set of graphs from the queue and merge them with the existing set in the process
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

    # Create the chords
    chordSetsChunks = init(n, numProcesses)

    # Generate the unique graphs lists
    processes = generate_unique(n, chordSetsChunks, numProcesses)
    print("Finished initial graph generation and checking. Commencing merging.")

    # Merge all the unique graph lists
    results = merge_unique_graph_lists(processes)
    print("Completed merging.")
    print(len(results))
