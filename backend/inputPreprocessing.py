def preprocessRequest(requestDict):
    # Presence Check 
    # These five fields are the absolute minimum to process any request.
    # If any are missing, we raise early , garbage in means garbage out.
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

    # String Normalization 
    # Strip stray whitespace and unify casing so comparisons
    # downstream never fail due to "Ambulance" vs "ambulance".
    normalizedRequest = {}
    normalizedRequest["request_id"]        = str(requestDict["request_id"]).strip()
    normalizedRequest["vehicle_type"]      = str(requestDict["vehicle_type"]).strip().lower()
    normalizedRequest["request_category"]  = str(requestDict["request_category"]).strip()
    normalizedRequest["current_location"]  = str(requestDict["current_location"]).strip()
    normalizedRequest["destination"]       = str(requestDict["destination"]).strip()

    # Optional Fields with Safe Defaults 
    # Not every request carries severity or timesensitivity data.
    # We provide conservative defaults so no module crashes on a missing key.
    normalizedRequest["severity"]         = str(requestDict.get("severity", "low")).strip().lower()
    normalizedRequest["time_sensitive"]   = bool(requestDict.get("time_sensitive", False))
    normalizedRequest["passenger_count"]  = int(requestDict.get("passenger_count", 1))
    normalizedRequest["notes"]            = str(requestDict.get("notes", "")).strip()

    # Feature Vector for the ANN 
    # The ANN cannot read strings , it needs numbers.
    # We encode each relevant attribute as a float in 0.0, 1.0.
    featureVector = prepareFeatureVector(normalizedRequest)
    normalizedRequest["feature_vector"] = featureVector

    return normalizedRequest

def prepareFeatureVector(normalizedRequest):
    # Map vehicle types to an urgency coefficient.
    # Emergency vehicles score high because their missions are lifecritical.
    vehicleTypeMap = {
        "ambulance":  1.00,
        "fire_truck": 0.90,
        "police_car": 0.80,
        "civilian":   0.20
    }

    # Map severity labels to numeric scores.
    severityMap = {
        "critical": 1.00,
        "high":     0.75,
        "medium":   0.50,
        "low":      0.25
    }

    # Retrieve scores; default to lowest possible if the value is unrecognized.
    vehicleScore    = vehicleTypeMap.get(normalizedRequest["vehicle_type"], 0.20)
    severityScore   = severityMap.get(normalizedRequest["severity"], 0.25)

    # Boolean , 1.0 or 0.0
    timeSensitiveScore = 1.0 if normalizedRequest["time_sensitive"] else 0.0

    # Scale passenger count to 0.0, 1.0, capping at 10 people.
    # A bus full of 10+ people is treated as maximum passenger urgency.
    passengerScore = min(normalizedRequest["passenger_count"] / 10.0, 1.0)

    return [vehicleScore, severityScore, timeSensitiveScore, passengerScore]
