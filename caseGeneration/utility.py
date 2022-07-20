from itertools import chain, islice


def chunks(iterable, size=10):
    iterator = iter(iterable)
    for first in iterator:    # stops when iterator is depleted
        def chunk():          # construct generator for next chunk
            yield first       # yield element from for loop
            for more in islice(iterator, size - 1):
                yield more    # yield more elements from the iterator
        yield chunk()         # in outer generator, yield next chunk
