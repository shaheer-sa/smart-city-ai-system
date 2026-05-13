def preprocessRequest(requestDict):
    # Validate required fields
    requiredFields = [
        "request_id",
        "vehicle_type",
        "request_category",
        "current_location",
        "destination"
    ]

    for field in requiredFields:
        if field not in requestDict:
            raise ValueError("Preprocessing failed: missing required field '%s'" % field)

    # Normalize strings
    normalizedRequest = {}
    normalizedRequest["request_id"]        = str(requestDict["request_id"]).strip()
    normalizedRequest["vehicle_type"]      = str(requestDict["vehicle_type"]).strip().lower()
    normalizedRequest["request_category"]  = str(requestDict["request_category"]).strip()
    normalizedRequest["current_location"]  = str(requestDict["current_location"]).strip()
    normalizedRequest["destination"]       = str(requestDict["destination"]).strip()

    # Apply defaults
    normalizedRequest["severity"]         = str(requestDict.get("severity", "low")).strip().lower()
    normalizedRequest["time_sensitive"]   = bool(requestDict.get("time_sensitive", False))
    normalizedRequest["notes"]            = str(requestDict.get("notes", "")).strip()

    # Encode ANN features
    featureVector = prepareFeatureVector(normalizedRequest)
    normalizedRequest["feature_vector"] = featureVector

    return normalizedRequest

def prepareFeatureVector(normalizedRequest):
    # Vehicle scores
    vehicleTypeMap = {
        "ambulance":  1.00,
        "fire_truck": 0.90,
        "police_car": 0.80,
        "civilian":   0.20
    }

    # Severity scores
    severityMap = {
        "critical": 1.00,
        "high":     0.75,
        "medium":   0.50,
        "low":      0.25
    }

    # Map input values
    vehicleScore    = vehicleTypeMap.get(normalizedRequest["vehicle_type"], 0.20)
    severityScore   = severityMap.get(normalizedRequest["severity"], 0.25)

    # Boolean score
    timeSensitiveScore = 1.0 if normalizedRequest["time_sensitive"] else 0.0

    # Category scores
    categoryMap = {
        "Emergency_Response_Request": 1.00,
        "Integrated_City_Service_Request": 0.80,
        "Control_Allocation_Request": 0.60,
        "Policy_Check": 0.40,
        "Route_Request": 0.20
    }
    categoryScore = categoryMap.get(normalizedRequest["request_category"], 0.20)

    return [vehicleScore, severityScore, timeSensitiveScore, categoryScore]
