# These vehicle types are legally classified as emergency responders.
# Any vehicle not in this set is treated as civilian for rule purposes.
EMERGENCY_VEHICLE_TYPES = {"ambulance", "fire_truck", "police_car"}

def checkPolicies(request):
    vehicleType  = request.get("vehicle_type", "civilian")
    severity     = request.get("severity", "low")
    timeSensitive= request.get("time_sensitive", False)
    destination  = request.get("destination", "")

    # Determine if this is an emergency vehicle caseinsensitive check
    isEmergencyVehicle = (vehicleType in EMERGENCY_VEHICLE_TYPES)

    # Collect which rules fire 
    rulesFired              = []
    overridePriority        = None
    emergencyRouteAuth      = False
    signalOverrideAllowed   = False

    # RULE 1: Emergency Vehicle + High Severity > Critical Priority
    # Rationale: A fire truck responding to a 5alarm fire or an ambulance
    # at a mass casualty event must be treated as maximum priority.
    if isEmergencyVehicle and severity in ("high", "critical"):
        overridePriority = "Critical"
        rulesFired.append("R1: Emergency Vehicle + High Severity gives Critical Priority")

    # RULE 2: Emergency Vehicle + Time Sensitive > High Priority
    # Rationale: Even without a severe incident, an emergency vehicle racing
    # against time e.g., early stroke treatment window earns High Priority.
    # Only applies if R1 didn't already escalate to Critical.
    if isEmergencyVehicle and timeSensitive and overridePriority != "Critical":
        overridePriority = "High"
        rulesFired.append("R2: Emergency Vehicle + Time Sensitive gives High Priority")

    # RULE 3: Civilian Vehicle > Normal Priority
    # Rationale: Without any emergency qualifier, a private vehicle gets the
    # standard routing treatment , no special permissions granted.
    if not isEmergencyVehicle:
        if overridePriority is None:
            overridePriority = "Normal"
        rulesFired.append("R3: Civilian Vehicle gives Normal Priority")

    # RULE 4: Emergency Vehicle + Destination Hospital > Emergency Route Auth
    # Rationale: Rushing a patient to City_Hospital is exactly the scenario
    # the emergency lane network was designed for. Access is granted here.
    if isEmergencyVehicle and destination == "City_Hospital":
        emergencyRouteAuth = True
        rulesFired.append("R4: Emergency Vehicle + Destination Hospital gives Emergency Route Authorized")

    # Rationale: Only when both conditions are true simultaneously can we
    # justify preempting civilian traffic signals , it is a disruptive action.
    if overridePriority == "Critical" and emergencyRouteAuth:
        signalOverrideAllowed = True
        rulesFired.append("R5: Critical Priority + Authorized Route gives Signal Override ALLOWED")

    # Build humanreadable KB notes 
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
