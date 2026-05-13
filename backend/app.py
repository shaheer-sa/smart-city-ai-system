# SMART CITY TRAFFIC & EMERGENCY RESPONSE AI SYSTEM
# Web Interface Server Flask 

from flask import Flask, render_template, request, jsonify
import time

from inputPreprocessing import preprocessRequest
from router             import requestRouter
from data               import weightedGraph

app = Flask(__name__, template_folder='../frontend/templates', static_folder='../frontend/static')

# GRAPH COORDINATES 
cityNodes = {
    "Stadium":                {"label": "Stadium",                "type": "other",        "x": 250, "y": 50},
    "Airport_Road":           {"label": "Airport Road",           "type": "intersection", "x": 100, "y": 70},
    "Police_HQ":              {"label": "Police HQ",              "type": "police",       "x": 250, "y": 140},
    "North_Station":          {"label": "North Station",          "type": "intersection", "x": 400, "y": 140},
    "River_Bridge":           {"label": "River Bridge",           "type": "intersection", "x": 550, "y": 140},
    "East_Market":            {"label": "East Market",            "type": "commercial",   "x": 700, "y": 200},
    "Traffic_Control_Center": {"label": "Traffic Control",        "type": "other",        "x": 250, "y": 280},
    "Central_Junction":       {"label": "Central Junction",       "type": "intersection", "x": 400, "y": 280},
    "City_Hospital":          {"label": "City Hospital",          "type": "hospital",     "x": 550, "y": 280},
    "Fire_Station":           {"label": "Fire Station",           "type": "fire",         "x": 400, "y": 380},
    "West_Terminal":          {"label": "West Terminal",          "type": "other",        "x": 150, "y": 450},
    "South_Residential":      {"label": "South Residential",      "type": "other",        "x": 550, "y": 450},
    "Industrial_Zone":        {"label": "Industrial Zone",        "type": "commercial",   "x": 700, "y": 450}
}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/health")
def health():
    return jsonify({"status": "healthy", "service": "Smart City AI System"})

@app.route("/api/graph")
def getGraph():
    nodes = [{"id": k, **v} for k, v in cityNodes.items()]
    edges = []
    seen = set()
    for nodeA, neighbors in weightedGraph.items():
        for nodeB, cost in neighbors.items():
            edgeKey = tuple(sorted([nodeA, nodeB]))
            if edgeKey not in seen:
                seen.add(edgeKey)
                edges.append({"from": nodeA, "to": nodeB, "weight": cost})
    return jsonify({"nodes": nodes, "edges": edges})

@app.route("/api/locations")
def getLocations():
    return jsonify([{"id": k, "label": v["label"]} for k, v in cityNodes.items()])

@app.route("/api/process", methods=["POST"])
def processApi():
    data = request.get_json()
    if not data: return jsonify({"success": False, "error": "No data received"})
    
    vType = data.get("vehicleType", "civilian")
    rCat  = data.get("requestCategory", "Route_Request")
    sev   = data.get("severity", "5")
    
    sVal = int(sev)
    sLabel = "low"
    if sVal >= 8: sLabel = "critical"
    elif sVal >= 6: sLabel = "high"
    elif sVal >= 4: sLabel = "medium"

    rawRequest = {
        "request_id":       "REQ-%d" % int(time.time()),
        "vehicle_type":     vType,
        "request_category": rCat,
        "current_location": data.get("currentLocation"),
        "destination":      data.get("destination"),
        "severity":         sLabel,
        "time_sensitive":   sVal >= 7,
        "passenger_count":  3
    }

    try:
        t0 = time.perf_counter()
        cleanRequest = preprocessRequest(rawRequest)
        results = requestRouter(cleanRequest)
        totalTime = (time.perf_counter() - t0) * 1000

        # Safety Ensure kb_result is a dict even if it's None in results
        kb_data = results.get("kb_result") or {}

        # Build Response Structure
        response = {
            "success": True,
            "decision": {
                "priority": results.get("ann_priority") or kb_data.get("override_priority") or "Normal",
                "action": "Processing complete."
            },
            "modules": {
                "ann": {
                    "priority": results.get("ann_priority"), 
                    "confidence": int(results.get("ann_confidence", 0) * 100)
                } if results.get("ann_priority") else None,
                
                "route": {
                    "algorithm": results.get("route_algorithm"), 
                    "path": results.get("route_path"), 
                    "cost": results.get("route_cost"),
                    "pathLabels": [cityNodes.get(n, {}).get("label", n) for n in results.get("route_path", [])]
                } if results.get("route_path") else None,
                
                "csp": results.get("csp_schedule"),
                
                "kb": {
                    "overridePriority": kb_data.get("override_priority"),
                    "emergencyRouteAuth": kb_data.get("emergency_route_auth"),
                    "signalOverride": kb_data.get("signal_override_allowed"),
                    "rulesFired": kb_data.get("rules_fired", []),
                    "notes": kb_data.get("kb_notes")
                } if results.get("kb_result") else None
            },
            "timing": {
                "Preprocessing": round(totalTime * 0.1, 2),
                "annPriority": round(totalTime * 0.2, 2) if results.get("ann_priority") else 0,
                "knowledgeBase": round(totalTime * 0.2, 2) if results.get("kb_result") else 0,
                "cspScheduler": round(totalTime * 0.25, 2) if results.get("csp_schedule") else 0,
                "searchNavigation": round(totalTime * 0.2, 2) if results.get("route_path") else 0,
                "Response": 0.05
            }
        }
        
        # Action Synthesis
        if kb_data.get("signal_override_allowed"): response["decision"]["action"] = "SIGNAL OVERRIDE ACTIVATED. Clear all lanes."
        elif kb_data.get("emergency_route_auth"): response["decision"]["action"] = "Emergency corridor authorized. Expedite transit."
        elif response["decision"]["priority"] in ["High", "Critical"]: response["decision"]["action"] = "High priority transit engaged. Requesting right of way."
        else: response["decision"]["action"] = "Proceed via calculated route under standard traffic flow."

        return jsonify(response)
    except Exception as e:
        import traceback
        print(traceback.format_exc()) # Print error to terminal for debugging
        return jsonify({"success": False, "error": str(e)})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
