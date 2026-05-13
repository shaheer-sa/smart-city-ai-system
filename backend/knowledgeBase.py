# Emergency vehicle classes
EMERGENCY_VEHICLE_TYPES = {"ambulance", "fire_truck", "police_car"}

def checkPolicies(request):
    vehicleType  = request.get("vehicle_type", "civilian")
    severity     = request.get("severity", "low")
    timeSensitive= request.get("time_sensitive", False)
    destination  = request.get("destination", "")

    # Check emergency status
    isEmergencyVehicle = (vehicleType in EMERGENCY_VEHICLE_TYPES)

    # Initialize rule states
    rulesFired              = []
    overridePriority        = None
    emergencyRouteAuth      = False
    signalOverrideAllowed   = False

    # Rule 1: Max priority
    if isEmergencyVehicle and severity in ("high", "critical"):
        overridePriority = "Critical"
        rulesFired.append("R1: Emergency Vehicle + High Severity gives Critical Priority")

    # Rule 2: High priority
    if isEmergencyVehicle and timeSensitive and overridePriority != "Critical":
        overridePriority = "High"
        rulesFired.append("R2: Emergency Vehicle + Time Sensitive gives High Priority")

    # Rule 3: Normal priority
    if not isEmergencyVehicle:
        if overridePriority is None:
            overridePriority = "Normal"
        rulesFired.append("R3: Civilian Vehicle gives Normal Priority")

    # Rule 4: Route auth
    if isEmergencyVehicle and destination == "City_Hospital":
        emergencyRouteAuth = True
        rulesFired.append("R4: Emergency Vehicle + Destination Hospital gives Emergency Route Authorized")

    # Rule 5: Signal override
    if overridePriority == "Critical" and emergencyRouteAuth:
        signalOverrideAllowed = True
        rulesFired.append("R5: Critical Priority + Authorized Route gives Signal Override ALLOWED")

    # Build summary notes
    if len(rulesFired) == 0:
        kbNotes = "No special rules triggered. Standard processing applies."
    else:
        kbNotes = "Policy engine matched %d rule(s)." % len(rulesFired)

    return {
        "override_priority":       overridePriority,
        "emergency_route_auth":    emergencyRouteAuth,
        "signal_override_allowed": signalOverrideAllowed,
        "rules_fired":             rulesFired,
        "kb_notes":                kbNotes
    }
