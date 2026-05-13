# BFS Unweighted Graph
unweightedGraph = {
    "Police_HQ":              ["Traffic_Control_Center", "River_Bridge"],
    "Stadium":                ["Airport_Road", "East_Market"],
    "Airport_Road":           ["Stadium", "South_Residential"],
    "North_Station":          ["Traffic_Control_Center", "River_Bridge", "Central_Junction"],
    "River_Bridge":           ["Police_HQ", "North_Station"],
    "East_Market":            ["Stadium", "Central_Junction", "City_Hospital"],
    "Traffic_Control_Center": ["Police_HQ", "North_Station"],
    "Central_Junction":       ["North_Station", "South_Residential", "West_Terminal", "East_Market"],
    "West_Terminal":          ["Central_Junction", "Fire_Station", "Industrial_Zone"],
    "Fire_Station":           ["West_Terminal"],
    "South_Residential":      ["Airport_Road", "Central_Junction"],
    "Industrial_Zone":        ["West_Terminal"],
    "City_Hospital":          ["East_Market"]
}

# UCS/A* Weighted Graph
weightedGraph = {
    "Police_HQ": {
        "Traffic_Control_Center": 2,
        "River_Bridge":           2
    },
    "Stadium": {
        "Airport_Road": 5,
        "East_Market":  2
    },
    "Airport_Road": {
        "Stadium":            5,
        "South_Residential":  2
    },
    "North_Station": {
        "Traffic_Control_Center": 2,
        "River_Bridge":           4,
        "Central_Junction":       3
    },
    "River_Bridge": {
        "Police_HQ":     2,
        "North_Station":  4
    },
    "East_Market": {
        "Stadium":          2,
        "Central_Junction": 3,
        "City_Hospital":    3
    },
    "Traffic_Control_Center": {
        "Police_HQ":     2,
        "North_Station":  2
    },
    "Central_Junction": {
        "North_Station":     3,
        "South_Residential": 4,
        "West_Terminal":     3,
        "East_Market":       3
    },
    "West_Terminal": {
        "Central_Junction": 3,
        "Fire_Station":     2,
        "Industrial_Zone":  4
    },
    "Fire_Station": {
        "West_Terminal": 2
    },
    "South_Residential": {
        "Airport_Road":     2,
        "Central_Junction": 4
    },
    "Industrial_Zone": {
        "West_Terminal": 4
    },
    "City_Hospital": {
        "East_Market": 3
    }
}

# A* Heuristic (Hospital)
heuristicToHospital = {
    "Police_HQ":              11,
    "Stadium":                4,
    "Airport_Road":           8,
    "North_Station":          7,
    "River_Bridge":           11,
    "East_Market":            2,
    "Traffic_Control_Center": 9,
    "Central_Junction":       5,
    "West_Terminal":          7,
    "Fire_Station":           9,
    "South_Residential":      8,
    "Industrial_Zone":        11,
    "City_Hospital":          0
}

# Generic heuristic function
def getHeuristic(node, destination):
    if destination == "City_Hospital":
        return heuristicToHospital.get(node, 0)
    # Fallback to UCS
    return 0

