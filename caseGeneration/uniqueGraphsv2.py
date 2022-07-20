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
import gc
import itertools
import math
import multiprocessing
import multiprocessing as mp
import random

import matplotlib.pyplot as plt
import more_itertools as mit
import networkx as nx

from utility import chunks
from compression import compress_graph
from generation import generate_chordal_graph
from isomorphism import isIsomorphicDuplicate
from processFunctions import *

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

    numSets = math.comb(2*(n**2)-n, n) # ((2n^2 - n) CHOOSE n) happens to be the working formula

    chunkSize = math.ceil(numSets / numProcesses)
    print("Chunk size: ", chunkSize)

    chordSetsChunks = iter(chunks(possibleChordSets, chunkSize))
    return chordSetsChunks

# ------------------------
# Creating the processes and assigning lists
# ------------------------

def generate_unique(n, chordSetsChunks,numProcesses):
    pool = multiprocessing.Pool(processes=numProcesses)
    uniqueGraphSetsSet = pool.imap(compute_unique_graphs, zip(itertools.repeat(n),chordSetsChunks))
    for item in uniqueGraphSetsSet:
        yield item
# ------------------------
# Merging code
# ------------------------

# Send graphs from half the processes to the other half

def merge_pairs(lock,queue,numProcessesToRun):
    processes = []
    manager = multiprocessing.Manager()
    newQueue = manager.Queue()
    for processIndex in range(numProcessesToRun):
        processes.append(multiprocessing.Process(target=get_and_merge,args=(lock,queue,newQueue)))
    for process in processes:
        process.start()
    for process in processes:
        process.join()
    print("Completed iteration with " + str(numProcessesToRun) + " processes")
    return lock, newQueue

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

    uniqueSets = generate_unique(n, chordSetsChunks,numProcesses)

    while numProcesses > 1:
        numProcesses = math.ceil(numProcesses / 2)
        print("Simplifying with " + str(numProcesses) + ' processes')
        uniqueSets = get_and_merge(uniqueSets)

    print(len(uniqueSets))