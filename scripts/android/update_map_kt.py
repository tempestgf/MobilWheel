import sys
import re

kt_path = r"app/src/main/java/com/tempestgf/steeringwheel/DashboardActivity.kt"

with open(kt_path, 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Properties
if "private lateinit var trackMapView: TrackMapView" not in text:
    prop_insert = """    private lateinit var tvPosition: TextView
    private lateinit var trackMapView: TrackMapView"""
    text = re.sub(r'private lateinit var tvPosition: TextView', prop_insert, text)

# 2. Initialization
if "trackMapView = findViewById(R.id.trackMapView)" not in text:
    init_insert = """        tvPosition = findViewById(R.id.tvPosition)
        trackMapView = findViewById(R.id.trackMapView)"""
    text = re.sub(r'tvPosition\s*=\s*findViewById\(R\.id\.tvPosition\)', init_insert, text)

# 3. Update Map
if "trackMapView.updatePosition(" not in text:
    map_update = """
            if (pos > 0) {
                tvPosition.text = "POS $pos / ${if (numCars>0) numCars else "--"}"
            }
            
            // Map Position Update
            val mapCoords = json.optJSONArray("tyre_contact_point")
            if (mapCoords != null && mapCoords.length() >= 3) {
                // FL tyre is [0, 1, 2] -> X, Y, Z
                val carX = mapCoords.getDouble(0).toFloat()
                val carZ = mapCoords.getDouble(2).toFloat()
                trackMapView.updatePosition(carX, carZ)
            }
"""
    text = re.sub(r'if \(pos > 0\) \{\s+tvPosition\.text = "POS \$pos / \$\{if \(numCars>0\) numCars else "--"\}".*?\}', map_update, text, flags=re.DOTALL)

with open(kt_path, 'w', encoding='utf-8') as f:
    f.write(text)

print("Kotlin Map binding updated!")
