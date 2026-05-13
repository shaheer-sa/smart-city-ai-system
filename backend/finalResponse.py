def generateFinalResponse(results):
    # REPORT HEADER
    print("\n")
    print("SMART CITY AI  |  OPERATIONAL RESPONSE REPORT")
    print("Request ID       : %s" % results.get("request_id", "N/A"))
    print("Category         : %s" % results.get("request_category", "N/A"))
    print("Vehicle Type     : %s" % results.get("vehicle_type", "N/A").upper())
    print("Origin           : %s" % results.get("origin", "N/A"))
    print("Destination      : %s" % results.get("destination", "N/A"))
    print("Modules Invoked  : %s" % ", ".join(results.get("modules_invoked", [])))

    # ERROR SECTION if routing failed
    if results.get("error"):
        print("\n[ERROR] %s" % results["error"])
        print("No further processing was completed for this request.\n")
        return

    # ANN PRIORITY PREDICTION
    # Only printed if the ANN module was invoked.
    if results.get("ann_priority") is not None:
        print("\nAI PRIORITY ASSESSMENT (Neural Network)")
        print("  Predicted Priority  : %s" % results["ann_priority"])
        print("  Model Confidence    : %.2f%%" % (results["ann_confidence"] * 100))

    # KNOWLEDGE BASE POLICY EVALUATION
    # Only printed if the KB module was invoked.
    kbResult = results.get("kb_result")
    if kbResult is not None:
        print("\nPOLICY ENGINE EVALUATION (Knowledge Base)")
        print("  Final Priority      : %s" % str(kbResult.get("override_priority", "N/A")))
        print("  Emergency Route     : %s" % ("AUTHORIZED" if kbResult.get("emergency_route_auth") else "Not Authorized"))
        print("  Signal Override     : %s" % ("ALLOWED" if kbResult.get("signal_override_allowed") else "Not Permitted"))
        print("  KB Notes            : %s" % kbResult.get("kb_notes", ""))

        rulesFired = kbResult.get("rules_fired", [])
        if len(rulesFired) > 0:
            print("  Rules Triggered     :")
            for rule in rulesFired:
                print("       %s" % rule)

    # CSP SIGNAL PHASE ALLOCATION
    # Only printed if the CSP scheduler was invoked.
    cspSchedule = results.get("csp_schedule")
    if cspSchedule is not None:
        print("\nINTERSECTION CONTROL SCHEDULE (CSP Solver)")
        if len(cspSchedule) == 0:
            print("  WARNING: Scheduler could not produce a valid phase allocation.")
        else:
            for intersection, phase in cspSchedule.items():
                print("  %-30s : %s" % (intersection, phase))

    # NAVIGATION ROUTE
    # Only printed if a search algorithm was invoked.
    routePath = results.get("route_path")
    if routePath is not None:
        routeCost      = results.get("route_cost", 0)
        routeAlgorithm = results.get("route_algorithm", "N/A")

        print("\nNAVIGATION RESULT (Algorithm: %s)" % routeAlgorithm)
        print("  Waypoints           : %s" % " to ".join(routePath))
        print("  Total Nodes in Path : %d" % len(routePath))

        # Show "hops" for BFS unweighted and "cost units" for weighted searches
        if routeAlgorithm == "BFS":
            print("  Hops (BFS)          : %d" % routeCost)
        else:
            print("  Total Route Cost    : %d units" % routeCost)

    elif results.get("route_algorithm") is not None:
        # A navigation was attempted but failed no path found
        print("\nNAVIGATION RESULT (Algorithm: %s)" % results.get("route_algorithm"))
        print("  STATUS: No valid path found between the specified locations.")

    # FINAL OPERATIONAL DECISION
    # Synthesizes the most important outcome into a single action line.
    print("\nOPERATIONAL DECISION")

    kbResult     = results.get("kb_result") or {}
    finalPriority= kbResult.get("override_priority") or results.get("ann_priority") or "Normal"
    sigOverride  = kbResult.get("signal_override_allowed", False)
    emgRoute     = kbResult.get("emergency_route_auth", False)

    print("  Effective Priority  : %s" % finalPriority)

    if sigOverride:
        print("  Action              : SIGNAL OVERRIDE ACTIVATED. Clear all lanes for emergency unit.")
    elif emgRoute:
        print("  Action              : Emergency route authorized. Dispatch on priority corridor.")
    elif finalPriority == "Critical":
        print("  Action              : Critical priority routing engaged. All units expedite, clear path.")
    elif finalPriority == "High":
        print("  Action              : High priority routing engaged. Expedite movement.")
    else:
        print("  Action              : Standard routing. Process through normal traffic flow.")

    print("\nEND OF REPORT\n")
