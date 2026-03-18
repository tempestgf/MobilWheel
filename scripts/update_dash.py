# -*- coding: utf-8 -*-
import re

with open('android-client/app/src/main/java/com/tempestgf/steeringwheel/DashboardActivity.kt', 'r', encoding='utf-8') as f:
    kt = f.read()

if 'SensorEventListener' not in kt:
    kt = kt.replace('class DashboardActivity : AppCompatActivity() {', 'import android.hardware.Sensor\nimport android.hardware.SensorEvent\nimport android.hardware.SensorEventListener\nimport android.hardware.SensorManager\nimport android.content.Context\n\nclass DashboardActivity : AppCompatActivity(), SensorEventListener {\n')

    kt = kt.replace('// HUD Views', '// Sensors\n    private lateinit var sensorManager: SensorManager\n    private var accelerometer: Sensor? = null\n    private var smoothedHudAngle = 0f\n    private val HUD_ALPHA = 0.18f\n    private var lastRawAngle = 0f\n    private var continuousAngle = 0f\n    private var isFirstReading = true\n\n    private lateinit var centerGearBlock: View\n    private lateinit var rpmContainer: View\n\n    // HUD Views')

    kt = kt.replace('initializeUIElements()', 'initializeUIElements()\n        setupSensors()')

    kt = kt.replace('private fun initializeUIElements() {', 'private fun setupSensors() {\n        sensorManager = getSystemService(Context.SENSOR_SERVICE) as SensorManager\n        accelerometer = sensorManager.getDefaultSensor(Sensor.TYPE_ACCELEROMETER)\n        accelerometer?.let { sensorManager.registerListener(this, it, SensorManager.SENSOR_DELAY_GAME) }\n    }\n\n    override fun onSensorChanged(event: SensorEvent?) {\n        event?.let {\n            if (it.sensor.type == Sensor.TYPE_ACCELEROMETER) {\n                val rawY = it.values[1]\n                val rawX = it.values[0]\n                val rawAngle = Math.toDegrees(Math.atan2(rawY.toDouble(), rawX.toDouble())).toFloat()\n\n                if (isFirstReading) {\n                    lastRawAngle = rawAngle\n                    continuousAngle = rawAngle\n                    isFirstReading = false\n                } else {\n                    var delta = rawAngle - lastRawAngle\n                    if (delta > 180f) delta -= 360f\n                    else if (delta < -180f) delta += 360f\n                    continuousAngle += delta\n                    lastRawAngle = rawAngle\n                }\n\n                val steeringAngle = continuousAngle\n                smoothedHudAngle = HUD_ALPHA * steeringAngle + (1f - HUD_ALPHA) * smoothedHudAngle\n                runOnUiThread { \n                    centerGearBlock.rotation = -smoothedHudAngle\n                    rpmContainer.rotation = -smoothedHudAngle \n                }\n            }\n        }\n    }\n\n    override fun onAccuracyChanged(sensor: Sensor?, accuracy: Int) {}\n\n    private fun initializeUIElements() {')

    kt = kt.replace('gearIndicatorView  = findViewById(R.id.gearIndicator)', 'gearIndicatorView  = findViewById(R.id.gearIndicator)\n        centerGearBlock = findViewById(R.id.centerGearBlock)\n        rpmContainer = findViewById(R.id.rpmContainer)')

    kt = kt.replace('override fun onDestroy() {', 'override fun onDestroy() {\n        sensorManager.unregisterListener(this)')

    with open('android-client/app/src/main/java/com/tempestgf/steeringwheel/DashboardActivity.kt', 'w', encoding='utf-8') as f:
        f.write(kt)
    print("Added SensorEventListener to DashboardActivity")
else:
    print("Already added")