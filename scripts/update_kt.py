import sys
import re

kt_path = r"android-client/app/src/main/java/com/tempestgf/steeringwheel/DashboardActivity.kt"

with open(kt_path, 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Properties
if "private lateinit var tvLapTime: TextView" not in text:
    prop_insert = """    private lateinit var speedValueView: TextView
    private lateinit var tvLapTime: TextView
    private lateinit var tvBestLap: TextView
    private lateinit var tvFuel: TextView
    private lateinit var tvTyreFL: TextView
    private lateinit var tvTyreFR: TextView
    private lateinit var tvTyreRL: TextView
    private lateinit var tvTyreRR: TextView
    private lateinit var tvPosition: TextView"""
    text = re.sub(r'private lateinit var speedValueView: TextView', prop_insert, text)

# 2. Initialization
if "tvLapTime = findViewById(R.id.tvLapTime)" not in text:
    init_insert = """        speedValueView     = findViewById(R.id.speedValue)
        tvLapTime = findViewById(R.id.tvLapTime)
        tvBestLap = findViewById(R.id.tvBestLap)
        tvFuel = findViewById(R.id.tvFuel)
        tvTyreFL = findViewById(R.id.tvTyreFL)
        tvTyreFR = findViewById(R.id.tvTyreFR)
        tvTyreRL = findViewById(R.id.tvTyreRL)
        tvTyreRR = findViewById(R.id.tvTyreRR)
        tvPosition = findViewById(R.id.tvPosition)"""
    text = re.sub(r'speedValueView\s*=\s*findViewById\(R\.id\.speedValue\)', init_insert, text)

# 3. Update JSON
if "updateDashboard(json: JSONObject)" in text and "tvLapTime.text =" not in text:
    old_update = """        runOnUiThread {
            speedValueView.text = speed.toString()"""
    new_update = """        runOnUiThread {
            speedValueView.text = speed.toString()

            // Advanced Telemetry (SmoothOperator integration)
            fun formatMs(ms: Int): String {
                if (ms <= 0) return "--:--.---"
                val min = ms / 60000
                val sec = (ms % 60000) / 1000
                val mil = ms % 1000
                return String.format("%02d:%02d.%03d", min, sec, mil)
            }
            
            // Fuel
            val fuel = json.optDouble("fuel", 0.0)
            tvFuel.text = String.format("FUEL %.1f L", fuel)
            
            // Laps (Use either camelCase or snake_case depending on backend version)
            val currentLap = json.optInt("currentLapMs", json.optInt("current_lap_ms", 0))
            val bestLap = json.optInt("bestLapMs", json.optInt("best_lap_ms", 0))
            tvLapTime.text = "LAP " + formatMs(currentLap)
            tvBestLap.text = "BEST " + formatMs(bestLap)

            // Tyres
            val tyreTemps = json.optJSONArray("tyre_core_temperature") ?: json.optJSONArray("tyreTemp")
            if (tyreTemps != null && tyreTemps.length() >= 4) {
                tvTyreFL.text = tyreTemps.optInt(0).toString()
                tvTyreFR.text = tyreTemps.optInt(1).toString()
                tvTyreRL.text = tyreTemps.optInt(2).toString()
                tvTyreRR.text = tyreTemps.optInt(3).toString()
                
                // Color code tyres based on optimal temps (AC GT3 ~ 80C)
                fun setTyreColor(tv: TextView, temp: Int) {
                    if (temp < 60) tv.setTextColor(0xFF7AA2F7.toInt()) // Cold (Blue)
                    else if (temp > 105) tv.setTextColor(0xFFFF6B6B.toInt()) // Hot (Red)
                    else tv.setTextColor(0xFF9ECE6A.toInt()) // Optimum (Green)
                }
                setTyreColor(tvTyreFL, tyreTemps.optInt(0))
                setTyreColor(tvTyreFR, tyreTemps.optInt(1))
                setTyreColor(tvTyreRL, tyreTemps.optInt(2))
                setTyreColor(tvTyreRR, tyreTemps.optInt(3))
            }
            
            // Position
            val pos = json.optInt("position", 0)
            val numCars = json.optInt("numCars", json.optInt("num_cars", 0))
            if (pos > 0) {
                tvPosition.text = "POS $pos / ${if (numCars>0) numCars else "--"}"
            }"""
    text = text.replace(old_update, new_update)

with open(kt_path, 'w', encoding='utf-8') as f:
    f.write(text)

print("Kotlin updated!")
