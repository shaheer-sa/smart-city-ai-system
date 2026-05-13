from data               import weightedGraph, unweightedGraph, getHeuristic
from annPriority        import predictPriority
from knowledgeBase      import checkPolicies
from cspScheduler       import allocateControl
from searchNavigation   import findRoute

def requestRouter(request):
    category     = request.get("request_category", "")
    startNode    = request.get("current_location", "")
    endNode      = request.get("destination", "")
    featureVector= request.get("feature_vector", [0.2, 0.25, 0.0, 0.1])

    # Initialize defaults
    results = {
        "request_id":              request.get("request_id", "N/A"),
        "request_category":        category,
        "vehicle_type":            request.get("vehicle_type", "unknown"),
        "origin":                  startNode,
        "destination":             endNode,

        # Module outputs
        "ann_priority":            None,
        "ann_confidence":          None,
        "kb_result":               None,
        "csp_schedule":            None,
        "route_algorithm":         None,
        "route_path":              None,
        "route_cost":              None,

        # Meta
        "modules_invoked":         [],
        "error":                   None
    }

    # Branch 1: Route
    if category == "Route_Request":
        results["modules_invoked"].append("searchNavigation")

        vehicleType = request.get("vehicle_type", "civilian")

        if vehicleType == "civilian":
            algorithm = "BFS"
            path, cost = findRoute("BFS", unweightedGraph, startNode, endNode)
        else:
            # A* for emergency
            algorithm = "ASTAR"
            path, cost = findRoute("ASTAR", weightedGraph, startNode, endNode,
                                   heuristicFn=getHeuristic)

        results["route_algorithm"] = algorithm
        results["route_path"]      = path
        results["route_cost"]      = cost

    # Branch 2: Policy
    elif category == "Policy_Check":
        results["modules_invoked"].append("knowledgeBase")
        results["kb_result"] = checkPolicies(request)

    elif category == "Control_Allocation_Request":
        results["modules_invoked"].extend(["knowledgeBase", "cspScheduler"])

        results["kb_result"] = checkPolicies(request)

        results["csp_schedule"] = allocateControl()

    elif category == "Emergency_Response_Request":
        results["modules_invoked"].extend(["annPriority", "knowledgeBase", "cspScheduler", "searchNavigation"])

        annLabel, annConf = predictPriority(featureVector)
        results["ann_priority"]   = annLabel
        results["ann_confidence"] = annConf

        results["kb_result"] = checkPolicies(request)

        results["csp_schedule"] = allocateControl()

        algorithm = "ASTAR"
        path, cost = findRoute("ASTAR", weightedGraph, startNode, endNode,
                               heuristicFn=getHeuristic)
        results["route_algorithm"] = algorithm
        results["route_path"]      = path
        results["route_cost"]      = cost

    # Branch 5: Integrated
    elif category == "Integrated_City_Service_Request":
        results["modules_invoked"].extend(
            ["annPriority", "knowledgeBase", "cspScheduler", "searchNavigation"]
        )

        # ANN priority
        annLabel, annConf = predictPriority(featureVector)
        results["ann_priority"]   = annLabel
        results["ann_confidence"] = annConf

        # KB policy
        results["kb_result"] = checkPolicies(request)

        # CSP intersection scheduling
        results["csp_schedule"] = allocateControl()

        # UCS navigation
        algorithm = "UCS"
        path, cost = findRoute("UCS", weightedGraph, startNode, endNode)
        results["route_algorithm"] = algorithm
        results["route_path"]      = path
        results["route_cost"]      = cost

    else:
        # Handle unknown
        results["error"] = "Unknown request_category: '%s'" % category

    return results
