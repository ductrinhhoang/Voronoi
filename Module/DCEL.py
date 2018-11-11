import heapq
import itertools


class Point:
    x = 0.0
    y = 0.0
   
    def __init__(self, x, y):
        self.x = x
        self.y = y


class CircleEvent:
    x = 0.0
    point = None
    arc = None
    valid = True
    
    def __init__(self, x, point, arc):
        self.x = x
        self.point = point
        self.arc = arc
        self.valid = True


class Arc:
    site = None
    pprev = None
    pnext = None
    e = None
    
    def __init__(self, site, pprev=None, pnext=None):
        self.site = site
        self.pprev = pprev
        self.pnext = pnext
        self.e = None
        self.hedge0 = None
        self.hedge1 = None


# half edge
class Hedge:
    start = None
    end = None
    done = False
    
    def __init__(self, p):
        self.start = p
        self.end = None
        self.done = False

    def finish(self, p):
        if self.done:
            return
        self.end = p
        self.done = True        


class PriorityQueue:
    def __init__(self):
        self.pq = []
        self.entry_finder = {}
        self.counter = itertools.count()

    def push(self, item):
        # check for duplicate
        if item in self.entry_finder: return
        count = next(self.counter)
        # use x-coordinate as a primary key (heapq in python is min-heap)
        entry = [item.x, count, item]
        self.entry_finder[item] = entry
        heapq.heappush(self.pq, entry)

    def remove_entry(self, item):
        entry = self.entry_finder.pop(item)
        entry[-1] = 'Removed'

    def pop(self):
        while self.pq:
            __, __, item = heapq.heappop(self.pq)
            if item is not 'Removed':
                del self.entry_finder[item]
                return item
        raise KeyError('pop from an empty priority queue')

    def top(self):
        while self.pq:
            __, __, item = heapq.heappop(self.pq)
            if item is not 'Removed':
                del self.entry_finder[item]
                self.push(item)
                return item
        raise KeyError('top from an empty priority queue')

    def empty(self):
        return not self.pq