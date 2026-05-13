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

    # Initialize a results container , every field defaults to None/False
    # so generateFinalResponse can check what actually ran.
    results = {
        "request_id":              request.get("request_id", "N/A"),
        "request_category":        category,
        "vehicle_type":            request.get("vehicle_type", "unknown"),
        "origin":                  startNode,
        "destination":             endNode,

        # Module outputs , populated below depending on category
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

    # BRANCH 1 , Route Request
    # A standard navigation request. Civilians get BFS hopoptimal,
    # while emergency vehicles get A* costoptimal with heuristic.
    if category == "Route_Request":
        results["modules_invoked"].append("searchNavigation")

        vehicleType = request.get("vehicle_type", "civilian")

        if vehicleType == "civilian":
            algorithm = "BFS"
            path, cost = findRoute("BFS", unweightedGraph, startNode, endNode)
        else:
            # Emergency vehicles use A* on the weighted graph for fastest route
            algorithm = "ASTAR"
            path, cost = findRoute("ASTAR", weightedGraph, startNode, endNode,
                                   heuristicFn=getHeuristic)

        results["route_algorithm"] = algorithm
        results["route_path"]      = path
        results["route_cost"]      = cost

    # BRANCH 2 , Policy Check
    # Only the Knowledge Base is needed. No navigation is requested.
    elif category == "Policy_Check":
        results["modules_invoked"].append("knowledgeBase")
        results["kb_result"] = checkPolicies(request)

    # BRANCH 3 , Control Allocation Request
    # The intersection scheduler is asked to assign safe signal phases.
    elif category == "Control_Allocation_Request":
        results["modules_invoked"].append("cspScheduler")
        results["csp_schedule"] = allocateControl()

    # BRANCH 4 , Emergency Response Request
    # Full emergency pipeline: ANN predicts urgency, KB validates policy,
    # A* finds the fastest weighted route to the destination.
    elif category == "Emergency_Response_Request":
        results["modules_invoked"].extend(["annPriority", "knowledgeBase", "searchNavigation"])

        # , ANN urgency prediction
        annLabel, annConf = predictPriority(featureVector)
        results["ann_priority"]   = annLabel
        results["ann_confidence"] = annConf

        # , KB policy validation
        results["kb_result"] = checkPolicies(request)

        # , A* route on weighted graph emergency always needs fastest path
        algorithm = "ASTAR"
        path, cost = findRoute("ASTAR", weightedGraph, startNode, endNode,
                               heuristicFn=getHeuristic)
        results["route_algorithm"] = algorithm
        results["route_path"]      = path
        results["route_cost"]      = cost

    # BRANCH 5 , Integrated City Service Request
    # Every module is invoked: ANN, KB, CSP, and navigation.
    # Used for complex scenarios that affect multiple city systems at once.
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

        # UCS navigation balanced option for citywide service management
        algorithm = "UCS"
        path, cost = findRoute("UCS", weightedGraph, startNode, endNode)
        results["route_algorithm"] = algorithm
        results["route_path"]      = path
        results["route_cost"]      = cost

    else:
        # Unknown category , record the error and return gracefully
        results["error"] = "Unknown request_category: '%s'" % category

    return results
