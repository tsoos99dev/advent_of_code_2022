import collections
from itertools import islice, takewhile, groupby, pairwise, chain, repeat
from typing import TypeVar, Callable, Iterable

_T = TypeVar('_T')


def batched(iterable, n):
    """Batch data into lists of length n. The last batch may be shorter."""
    # batched('ABCDEFG', 3) --> ABC DEF G

    if n < 1:
        raise ValueError('n must be at least one')

    it = iter(iterable)
    while batch := list(islice(it, n)):
        yield batch


def triplewise(iterable):
    "Return overlapping triplets from an iterable"
    # triplewise('ABCDEFG') --> ABC BCD CDE DEF EFG
    for (a, _), (b, c) in pairwise(pairwise(iterable)):
        yield a, b, c


def isplit(iterable, sep):
    """Split data based on the provided separator"""
    it = iter(iterable)

    for key, group in groupby(it, lambda item: item == sep):
        if not key:
            yield list(group)


def window(iterable, n):
    # sliding_window('ABCDEFG', 4) --> ABCD BCDE CDEF DEFG
    it = iter(iterable)
    window = collections.deque(islice(it, n), maxlen=n)
    if len(window) == n:
        yield tuple(window)
    for x in it:
        window.append(x)
        yield tuple(window)


def first(iterable, default=False, pred=None):
    """Returns the first true value in the iterable.

    If no true value is found, returns *default*

    If *pred* is not None, returns the first item
    for which pred(item) is true.

    """
    # first_true([a,b,c], x) --> a or b or c or x
    # first_true([a,b], x, f) --> a if f(a) else b if f(b) else x
    return next(filter(pred, iterable), default)


def takewhile_inclusive(predicate, iterable):
    # takewhile(lambda x: x<5, [1,4,6,4,1]) --> 1 4
    for x in iterable:
        yield x

        if not predicate(x):
            break


def prepend(value, iterator):
    "Prepend a single value in front of an iterator"
    # prepend(1, [2, 3, 4]) --> 1 2 3 4
    return chain([value], iterator)


def tail(n, iterable):
    "Return an iterator over the last n items"
    # tail(3, 'ABCDEFG') --> E F G
    return iter(collections.deque(iterable, maxlen=n))


def flatten(list_of_lists):
    "Flatten one level of nesting"
    return chain.from_iterable(list_of_lists)


def iter_except(func: Callable[[], _T], exception: type[Exception], first=None) -> Iterable[_T]:
    """ Call a function repeatedly until an exception is raised.

    Converts a call-until-exception interface to an iterator interface.
    Like builtins.iter(func, sentinel) but uses an exception instead
    of a sentinel to end the loop.

    Examples:
        iter_except(functools.partial(heappop, h), IndexError)   # priority queue iterator
        iter_except(d.popitem, KeyError)                         # non-blocking dict iterator
        iter_except(d.popleft, IndexError)                       # non-blocking deque iterator
        iter_except(q.get_nowait, Queue.Empty)                   # loop over a producer Queue
        iter_except(s.pop, KeyError)                             # non-blocking set iterator

    """
    try:
        if first is not None:
            yield first()            # For database APIs needing an initial cast to db.first()
        while True:
            yield func()
    except exception:
        pass


def ncycles(iterable, n):
    "Returns the sequence elements n times"
    return chain.from_iterable(repeat(tuple(iterable), n))


def iter_index(iterable, value, start=0):
    "Return indices where a value occurs in a sequence or iterable."
    # iter_index('AABCADEAF', 'A') --> 0 1 4 7
    try:
        seq_index = iterable.index
    except AttributeError:
        # Slow path for general iterables
        it = islice(iterable, start, None)
        for i, element in enumerate(it, start):
            if element is value or element == value:
                yield i
    else:
        # Fast path for sequences
        i = start - 1
        try:
            while True:
                yield (i := seq_index(value, i+1))
        except ValueError:
            pass
