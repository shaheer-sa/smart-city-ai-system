from collections import deque   # Python's built-in double-ended queue

# Simple priority queue

class SimplePriorityQueue:
    def __init__(self):
        self.items = []

    def push(self, priority, data):
        """Add item and sort"""
        self.items.append((priority, data))
        # Sort ascending by priority value
        self.items.sort(key=lambda pair: pair[0])

    def pop(self):
        """Pop lowest priority"""
        if self.isEmpty():
            raise IndexError("pop from empty priority queue")
        return self.items.pop(0)

    def isEmpty(self):
        return len(self.items) == 0

# BFS: Unweighted graphs

def bfsRoute(graph, startNode, endNode):
    if startNode not in graph:
        print("BFS Error: Start node '%s' not found in graph.\n" % startNode)
        return None, -1

    if endNode not in graph:
        print("BFS Error: End node '%s' not found in graph.\n" % endNode)
        return None, -1

    if startNode == endNode:
        return [startNode], 0

    # Queue: node, path
    queue = deque()
    queue.append((startNode, [startNode]))

    visited = set()
    visited.add(startNode)

    while len(queue) > 0:
        currentNode, currentPath = queue.popleft()

        # Explore neighbors
        for neighbor in graph[currentNode]:
            if neighbor in visited:
                continue  # Skip visited

            newPath = currentPath + [neighbor]

            # Destination reached
            if neighbor == endNode:
                return newPath, len(newPath) - 1  # hops = nodes - 1

            visited.add(neighbor)
            queue.append((neighbor, newPath))

    # No path found
    return None, -1

# UCS: Weighted graphs

def ucsRoute(graph, startNode, endNode):
    if startNode not in graph:
        print("UCS Error: Start node '%s' not found in graph.\n" % startNode)
        return None, -1

    if endNode not in graph:
        print("UCS Error: End node '%s' not found in graph.\n" % endNode)
        return None, -1

    if startNode == endNode:
        return [startNode], 0

    pq = SimplePriorityQueue()
    # Init pq
    pq.push(0, (startNode, [startNode]))

    visited = set()

    while not pq.isEmpty():
        cumulativeCost, (currentNode, currentPath) = pq.pop()

        # Skip visited
        if currentNode in visited:
            continue
        visited.add(currentNode)

        # Goal check
        if currentNode == endNode:
            return currentPath, cumulativeCost

        # Expand neighbors
        for neighbor, edgeCost in graph[currentNode].items():
            if neighbor not in visited:
                newCost = cumulativeCost + edgeCost
                newPath = currentPath + [neighbor]
                pq.push(newCost, (neighbor, newPath))

    return None, -1

# A* Search

def aStarRoute(graph, startNode, endNode, heuristicFn):
    if startNode not in graph:
        print("A* Error: Start node '%s' not found in graph.\n" % startNode)
        return None, -1

    if endNode not in graph:
        print("A* Error: End node '%s' not found in graph.\n" % endNode)
        return None, -1

    if startNode == endNode:
        return [startNode], 0

    pq = SimplePriorityQueue()

    # Calculate costs
    gStart = 0
    hStart = heuristicFn(startNode, endNode)
    fStart = gStart + hStart

    # Push initial state
    pq.push(fStart, (gStart, startNode, [startNode]))

    visited = set()

    while not pq.isEmpty():
        fCost, (gCost, currentNode, currentPath) = pq.pop()

        if currentNode in visited:
            continue
        visited.add(currentNode)

        # Goal check
        if currentNode == endNode:
            return currentPath, gCost

        for neighbor, edgeCost in graph[currentNode].items():
            if neighbor not in visited:
                newG = gCost + edgeCost
                newH = heuristicFn(neighbor, endNode)
                newF = newG + newH
                newPath = currentPath + [neighbor]
                pq.push(newF, (newG, neighbor, newPath))

    return None, -1

def findRoute(algorithm, graph, startNode, endNode, heuristicFn=None):
    algorithm = algorithm.upper()

    if algorithm == "BFS":
        return bfsRoute(graph, startNode, endNode)

    elif algorithm == "UCS":
        return ucsRoute(graph, startNode, endNode)

    elif algorithm == "ASTAR":
        if heuristicFn is None:
            # Default heuristic
            heuristicFn = lambda node, dest: 0
        return aStarRoute(graph, startNode, endNode, heuristicFn)

    else:
        print("findRoute Error: Unknown algorithm '%s'. Use BFS, UCS, or ASTAR.\n" % algorithm)
        return None, -1
