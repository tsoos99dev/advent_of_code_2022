from itertools import islice, takewhile, groupby, pairwise


def batched(iterable, n):
    """Batch data into lists of length n. The last batch may be shorter."""
    # batched('ABCDEFG', 3) --> ABC DEF G

    if n < 1:
        raise ValueError('n must be at least one')

    it = iter(iterable)
    while batch := tuple(islice(it, n)):
        yield batch


def triplewise(iterable):
    "Return overlapping triplets from an iterable"
    # triplewise('ABCDEFG') --> ABC BCD CDE DEF EFG
    for (a, _), (b, c) in pairwise(pairwise(iterable)):
        yield a, b, c


def isplit(iterable, sep):
    """Split data based on the provided separator"""
    it = iter(iterable)

    for _, group in groupby(it, lambda item: item == sep):
        yield filter(lambda item: item != sep, group)
