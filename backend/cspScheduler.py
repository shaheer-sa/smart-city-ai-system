MANAGED_INTERSECTIONS = ["Central_Junction", "North_Station", "River_Bridge", "Airport_Road"]

SIGNAL_PHASES = ["Phase_A", "Phase_B", "Phase_C"]

CONFLICT_PAIRS = [
    ("Central_Junction", "North_Station"),
    ("North_Station", "River_Bridge")
]

def isConsistent(intersection, phase, currentAssignment):
    for (nodeA, nodeB) in CONFLICT_PAIRS:
        if nodeA == intersection:
            neighbor = nodeB
        elif nodeB == intersection:
            neighbor = nodeA
        else:
            continue

        # Check neighbor phase
        if neighbor in currentAssignment and currentAssignment[neighbor] == phase:
            return False

    return True

def backtrack(unassigned, assignment):
    # Base case reached
    if len(unassigned) == 0:
        return assignment

    current = unassigned[0]
    remaining = unassigned[1:]

    for phase in SIGNAL_PHASES:
        if isConsistent(current, phase, assignment):
            assignment[current] = phase
            result = backtrack(remaining, assignment)

            if result is not None:
                return result

            # Backtrack on failure
            del assignment[current]

    return None

def allocateControl(intersections=None):
    if intersections is None:
        intersections = MANAGED_INTERSECTIONS

    initialAssignment = {}
    solution = backtrack(list(intersections), initialAssignment)

    if solution is None:
        print("CSP Scheduler: WARNING — no valid phase allocation found.\n")
        return {}

    return solution
