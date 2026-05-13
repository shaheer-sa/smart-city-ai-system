MANAGED_INTERSECTIONS = ["Central_Junction", "North_Station", "River_Bridge"]

# Available signal phases think of these as "time slots" for green lights.
SIGNAL_PHASES = ["Phase_A", "Phase_B", "Phase_C"]

# Conflict pairs: two intersections in the same pair share a direct road link.
# They cannot run the same phase simultaneously , that would give conflicting
# traffic streams a green light at the same moment.
CONFLICT_PAIRS = [
    ("Central_Junction", "North_Station"),   # Linked via the main corridor
    ("Central_Junction", "River_Bridge"),    # Linked via the bridge approach
    ("North_Station",    "River_Bridge")     # Linked via the riverside route
]

def isConsistent(intersection, phase, currentAssignment):
    for (nodeA, nodeB) in CONFLICT_PAIRS:
        # Find which node in the pair is our target and which is its neighbor
        if nodeA == intersection:
            neighbor = nodeB
        elif nodeB == intersection:
            neighbor = nodeA
        else:
            # This pair does not involve our target intersection at all
            continue

        # If the neighbor already has a phase AND it's the same phase we want,
        # that would create conflicting green lights , constraint violated.
        if neighbor in currentAssignment and currentAssignment[neighbor] == phase:
            return False

    # Passed all conflict checks , this assignment is locally consistent
    return True

def backtrack(unassigned, assignment):
    # Base case , every intersection has been assigned successfully
    if len(unassigned) == 0:
        return assignment

    # Pick the next intersection to work on simple lefttoright ordering
    current = unassigned[0]
    remaining = unassigned[1:]

    for phase in SIGNAL_PHASES:
        if isConsistent(current, phase, assignment):
            # Tentatively assign this phase
            assignment[current] = phase

            # Recurse into the rest of the unassigned list
            result = backtrack(remaining, assignment)

            if result is not None:
                return result  # A solution was found further down the tree

            # Backtrack: undo the tentative assignment and try the next phase
            del assignment[current]

    # No phase worked for 'current' , signal failure to the caller
    return None

def allocateControl(intersections=None):
    if intersections is None:
        intersections = MANAGED_INTERSECTIONS

    # Start with an empty assignment , nothing is decided yet
    initialAssignment = {}

    solution = backtrack(list(intersections), initialAssignment)

    if solution is None:
        # This should not happen with our current graph, but we handle it cleanly
        print("CSP Scheduler: WARNING — no valid phase allocation found.\n")
        return {}

    return solution
