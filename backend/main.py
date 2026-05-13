# SMART CITY TRAFFIC & EMERGENCY RESPONSE AI SYSTEM
# This system models a city's intelligent traffic and emergency
# management infrastructure using seven AI/CS techniques:
# Each request flows through only the modules relevant to its category,
# keeping processing efficient and outputs focused.

from inputPreprocessing import preprocessRequest
from router             import requestRouter
from finalResponse      import generateFinalResponse

def buildDemoRequests():
    # Standard civilian route request 
    # A resident wants to get from the Stadium to the Industrial Zone.
    # No emergency qualifiers , just plain navigation via BFS.
    requestA = {
        "request_id":       "REQ-001",
        "vehicle_type":     "civilian",
        "request_category": "Route_Request",
        "current_location": "Stadium",
        "destination":      "Industrial_Zone",
        "severity":         "low",
        "time_sensitive":   False,
        "passenger_count":  2,
        "notes":            "Standard commute route."
    }

    # Critical ambulance emergency response 
    # An ambulance at North_Station has a cardiac patient bound for City_Hospital.
    # Timecritical, high severity , full pipeline: ANN + KB + A* navigation.
    requestB = {
        "request_id":       "REQ-002",
        "vehicle_type":     "ambulance",
        "request_category": "Emergency_Response_Request",
        "current_location": "North_Station",
        "destination":      "City_Hospital",
        "severity":         "critical",
        "time_sensitive":   True,
        "passenger_count":  3,
        "notes":            "Cardiac arrest patient on board. Requesting emergency corridor."
    }

    # Intersection control allocation request 
    # Traffic Control Center requests a safe signal phase schedule for the
    # main city junctions to prevent conflicting green lights.
    requestC = {
        "request_id":       "REQ-003",
        "vehicle_type":     "civilian",
        "request_category": "Control_Allocation_Request",
        "current_location": "Traffic_Control_Center",
        "destination":      "Traffic_Control_Center",
        "severity":         "low",
        "time_sensitive":   False,
        "passenger_count":  1,
        "notes":            "Daily signal reallocation cycle."
    }

    # Integrated city service , fire truck to south residential 
    # A fire truck is responding to a building fire. All modules run:
    # ANN estimates urgency, KB grants route authorization, CSP
    # reschedules affected intersections, UCS finds leastcost path.
    requestD = {
        "request_id":       "REQ-004",
        "vehicle_type":     "fire_truck",
        "request_category": "Integrated_City_Service_Request",
        "current_location": "Fire_Station",
        "destination":      "South_Residential",
        "severity":         "high",
        "time_sensitive":   True,
        "passenger_count":  5,
        "notes":            "Structure fire reported. Full city coordination required."
    }

    return [requestA, requestB, requestC, requestD]

def processRequest(rawRequest):
    requestId = rawRequest.get("request_id", "UNKNOWN")

    print("\n\nPROCESSING REQUEST : %s" % requestId)
    print("Category           : %s" % rawRequest.get("request_category", "N/A"))

    try:
        # Validate and normalize the raw input
        cleanRequest = preprocessRequest(rawRequest)

    except ValueError as validationError:
        print("INPUT ERROR for %s: %s" % (requestId, str(validationError)))
        print("Request skipped due to validation failure.\n")
        return

    try:
        # Route the clean request through the appropriate AI modules
        results = requestRouter(cleanRequest)

    except Exception as routingError:
        print("ROUTING ERROR for %s: %s" % (requestId, str(routingError)))
        print("Request skipped due to routing failure.\n")
        return

    try:
        # Print the formatted operational response
        generateFinalResponse(results)

    except Exception as responseError:
        print("RESPONSE ERROR for %s: %s" % (requestId, str(responseError)))
        print("Results were computed but could not be displayed cleanly.\n")

def main():
    print("=" * 60)
    print("  SMART CITY TRAFFIC & EMERGENCY RESPONSE AI SYSTEM")
    print("=" * 60)
    print("\nInitializing city graph data and mock requests...")
    print("4 demonstration requests queued for processing.\n")

    demoRequests = buildDemoRequests()

    # Process each request in sequence
    for rawRequest in demoRequests:
        processRequest(rawRequest)

    print("\n")
    print("All demonstration requests have been processed.")
    print("Smart City AI System shutdown complete.")
    print("\n")

# Standard Python entrypoint guard , ensures main only runs when this
# file is executed directly, not when it is imported as a module.
if __name__ == "__main__":
    main()
