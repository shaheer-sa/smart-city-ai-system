# Unweighted City Graph 
# Used by BFS, which only cares about connectivity, not cost.
# Each key is a node, and its value is a list of directly reachable neighbors.
unweightedGraph = {
    "Police_HQ":              ["Traffic_Control_Center", "Central_Junction"],
    "Stadium":                ["Airport_Road", "North_Station"],
    "Airport_Road":           ["Stadium", "North_Station", "West_Terminal"],
    "North_Station":          ["Stadium", "Airport_Road", "River_Bridge", "Central_Junction"],
    "River_Bridge":           ["North_Station", "East_Market", "Central_Junction"],
    "East_Market":            ["River_Bridge", "Industrial_Zone", "South_Residential"],
    "Traffic_Control_Center": ["Police_HQ", "Central_Junction", "Fire_Station"],
    "Central_Junction":       ["Police_HQ", "North_Station", "River_Bridge",
                                "Traffic_Control_Center", "West_Terminal", "City_Hospital"],
    "West_Terminal":          ["Airport_Road", "Central_Junction", "South_Residential"],
    "Fire_Station":           ["Traffic_Control_Center", "South_Residential", "City_Hospital"],
    "South_Residential":      ["East_Market", "West_Terminal", "Fire_Station", "Industrial_Zone"],
    "Industrial_Zone":        ["East_Market", "South_Residential"],
    "City_Hospital":          ["Central_Junction", "Fire_Station"]
}

# Weighted City Graph 
# Used by UCS and A*. Each neighbor is paired with a travel cost.
# Costs represent approximate distances in city blocks / minutes.
# Bidirectional edges are listed explicitly for both directions.
weightedGraph = {
    "Police_HQ": {
        "Traffic_Control_Center": 2,
        "Central_Junction":       4
    },
    "Stadium": {
        "Airport_Road":  5,
        "North_Station": 3
    },
    "Airport_Road": {
        "Stadium":        5,
        "North_Station":  4,
        "West_Terminal":  6
    },
    "North_Station": {
        "Stadium":        3,
        "Airport_Road":   4,
        "River_Bridge":   5,
        "Central_Junction": 3
    },
    "River_Bridge": {
        "North_Station":    5,
        "East_Market":      4,
        "Central_Junction": 2
    },
    "East_Market": {
        "River_Bridge":      4,
        "Industrial_Zone":   3,
        "South_Residential": 2
    },
    "Traffic_Control_Center": {
        "Police_HQ":        2,
        "Central_Junction": 3,
        "Fire_Station":     4
    },
    "Central_Junction": {
        "Police_HQ":              4,
        "North_Station":          3,
        "River_Bridge":           2,
        "Traffic_Control_Center": 3,
        "West_Terminal":          5,
        "City_Hospital":          2
    },
    "West_Terminal": {
        "Airport_Road":      6,
        "Central_Junction":  5,
        "South_Residential": 4
    },
    "Fire_Station": {
        "Traffic_Control_Center": 4,
        "South_Residential":      3,
        "City_Hospital":          2
    },
    "South_Residential": {
        "East_Market":   2,
        "West_Terminal": 4,
        "Fire_Station":  3,
        "Industrial_Zone": 5
    },
    "Industrial_Zone": {
        "East_Market":       3,
        "South_Residential": 5
    },
    "City_Hospital": {
        "Central_Junction": 2,
        "Fire_Station":     2
    }
}

# Mock StraightLine Heuristic Distances to City_Hospital 
# Used as the A* heuristic. These are not real GPS coordinates;
# they are rough "as the crow flies" estimates toward City_Hospital.
# A good heuristic is always < real cost admissible, so we keep these
# slightly conservative on purpose.
heuristicToHospital = {
    "Police_HQ":              6,
    "Stadium":                9,
    "Airport_Road":           10,
    "North_Station":          5,
    "River_Bridge":           3,
    "East_Market":            6,
    "Traffic_Control_Center": 5,
    "Central_Junction":       2,
    "West_Terminal":          7,
    "Fire_Station":           2,
    "South_Residential":      5,
    "Industrial_Zone":        7,
    "City_Hospital":          0
}

# A generic zero heuristic , turns A* into plain UCS for nonhospital destinations.
# Allows the A* function to still work even when a destinationspecific
# heuristic table is not available.
def getHeuristic(node, destination):
    if destination == "City_Hospital":
        return heuristicToHospital.get(node, 0)
    # No special heuristic for other destinations , fall back to 0
    return 0
