package com.tempestgf.steeringwheel

import android.os.Bundle
import android.widget.SeekBar
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity

class SettingsActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_settings)

        // Inicializar los elementos de la UI
        val steeringAngle: SeekBar = findViewById(R.id.steering_angle)
        val steeringAngleValue: TextView = findViewById(R.id.steering_angle_value)
        val swipeThreshold: SeekBar = findViewById(R.id.swipe_threshold)
        val swipeThresholdValue: TextView = findViewById(R.id.swipe_threshold_value)
        val clickTimeLimit: SeekBar = findViewById(R.id.click_time_limit)
        val clickTimeLimitValue: TextView = findViewById(R.id.click_time_limit_value)
        val acceleratorSensitivity: SeekBar = findViewById(R.id.accelerator_sensitivity)
        val acceleratorValue: TextView = findViewById(R.id.accelerator_value)
        val brakeSensitivity: SeekBar = findViewById(R.id.brake_sensitivity)
        val brakeValue: TextView = findViewById(R.id.brake_value)
        val switchMuteVideo: android.widget.Switch = findViewById(R.id.switch_mute_video)
        val switchTelemetry: android.widget.Switch = findViewById(R.id.switch_telemetry)
        val backButton: android.widget.Button = findViewById(R.id.button_back)
        val resetDefaultsButton: android.widget.Button = findViewById(R.id.button_reset_defaults)

        // Cargar valores guardados
        val sharedPrefs = getSharedPreferences("steering_prefs", MODE_PRIVATE)
        val savedAngle = sharedPrefs.getInt("steering_angle", 365)
        val savedSwipeThreshold = sharedPrefs.getFloat(PREF_SWIPE_THRESHOLD, DEFAULT_SWIPE_THRESHOLD)
        val savedClickTimeLimit = sharedPrefs.getFloat(PREF_CLICK_TIME_LIMIT, DEFAULT_CLICK_TIME_LIMIT)
        val savedAcceleratorSensitivity = sharedPrefs.getFloat(PREF_ACCELERATOR_SENSITIVITY, DEFAULT_ACCELERATOR_SENSITIVITY)
        val savedBrakeSensitivity = sharedPrefs.getFloat(PREF_BRAKE_SENSITIVITY, DEFAULT_BRAKE_SENSITIVITY)
        val savedMuteVideo = sharedPrefs.getBoolean(PREF_MUTE_VIDEO, DEFAULT_MUTE_VIDEO)
        val savedTelemetryEnabled = sharedPrefs.getBoolean(PREF_TELEMETRY_ENABLED, DEFAULT_TELEMETRY_ENABLED)

        // Establecer valores guardados en los SeekBar y TextView
        steeringAngle.progress = savedAngle
        steeringAngleValue.text = "$savedAngle°"

        swipeThreshold.progress = (savedSwipeThreshold * 10).toInt() // Convertir a decenas para más precisión
        swipeThresholdValue.text = String.format("%.1f mm", savedSwipeThreshold)

        clickTimeLimit.progress = (savedClickTimeLimit * 100).toInt() // Convertir a centésimas para más precisión
        clickTimeLimitValue.text = String.format("%.2f sec", savedClickTimeLimit)

        acceleratorSensitivity.progress = (savedAcceleratorSensitivity * 10).toInt()
        acceleratorValue.text = String.format("%.1f", savedAcceleratorSensitivity)

        brakeSensitivity.progress = (savedBrakeSensitivity * 10).toInt()
        brakeValue.text = String.format("%.1f", savedBrakeSensitivity)
        
        switchMuteVideo.isChecked = savedMuteVideo
        switchTelemetry.isChecked = savedTelemetryEnabled

        // Manejar cambios en el SeekBar de ángulo
        steeringAngle.setOnSeekBarChangeListener(object : SeekBar.OnSeekBarChangeListener {
            override fun onProgressChanged(seekBar: SeekBar?, progress: Int, fromUser: Boolean) {
                steeringAngleValue.text = "$progress°"
                saveSteeringAngle(progress)
            }

            override fun onStartTrackingTouch(seekBar: SeekBar?) {}
            override fun onStopTrackingTouch(seekBar: SeekBar?) {}
        })

        // Manejar cambios en el SeekBar de Swipe Threshold
        swipeThreshold.setOnSeekBarChangeListener(object : SeekBar.OnSeekBarChangeListener {
            override fun onProgressChanged(seekBar: SeekBar?, progress: Int, fromUser: Boolean) {
                val newValue = progress / 10.0f
                swipeThresholdValue.text = String.format("%.1f mm", newValue)
                saveSwipeThreshold(newValue)
            }

            override fun onStartTrackingTouch(seekBar: SeekBar?) {}
            override fun onStopTrackingTouch(seekBar: SeekBar?) {}
        })

        // Manejar cambios en el SeekBar de Click Time Limit
        clickTimeLimit.setOnSeekBarChangeListener(object : SeekBar.OnSeekBarChangeListener {
            override fun onProgressChanged(seekBar: SeekBar?, progress: Int, fromUser: Boolean) {
                val newValue = progress / 100.0f
                clickTimeLimitValue.text = String.format("%.2f sec", newValue)
                saveClickTimeLimit(newValue)
            }

            override fun onStartTrackingTouch(seekBar: SeekBar?) {}
            override fun onStopTrackingTouch(seekBar: SeekBar?) {}
        })

        // Manejar cambios en el SeekBar de Accelerator Sensitivity
        acceleratorSensitivity.setOnSeekBarChangeListener(object : SeekBar.OnSeekBarChangeListener {
            override fun onProgressChanged(seekBar: SeekBar?, progress: Int, fromUser: Boolean) {
                val newValue = progress / 10.0f
                acceleratorValue.text = String.format("%.1f", newValue)
                saveAcceleratorSensitivity(newValue)
            }

            override fun onStartTrackingTouch(seekBar: SeekBar?) {}
            override fun onStopTrackingTouch(seekBar: SeekBar?) {}
        })

        // Manejar cambios en el SeekBar de Brake Sensitivity
        brakeSensitivity.setOnSeekBarChangeListener(object : SeekBar.OnSeekBarChangeListener {
            override fun onProgressChanged(seekBar: SeekBar?, progress: Int, fromUser: Boolean) {
                val newValue = progress / 10.0f
                brakeValue.text = String.format("%.1f", newValue)
                saveBrakeSensitivity(newValue)
            }

            override fun onStartTrackingTouch(seekBar: SeekBar?) {}
            override fun onStopTrackingTouch(seekBar: SeekBar?) {}
        })

        // Manejar cambios en el Switch de Mute Video
        switchMuteVideo.setOnCheckedChangeListener { _, isChecked ->
            saveMuteVideo(isChecked)
        }

        // Manejar cambios en el Switch de Telemetría
        switchTelemetry.setOnCheckedChangeListener { _, isChecked ->
            saveTelemetryEnabled(isChecked)
        }

        // Manejar botón de regreso
        backButton.setOnClickListener {
            finish()
        }

        // Manejar botón de reset
        resetDefaultsButton.setOnClickListener {
            // Restore actual values
            steeringAngle.progress = 365
            steeringAngleValue.text = "365°"
            saveSteeringAngle(365)

            swipeThreshold.progress = (DEFAULT_SWIPE_THRESHOLD * 10).toInt()
            swipeThresholdValue.text = String.format("%.1f mm", DEFAULT_SWIPE_THRESHOLD)
            saveSwipeThreshold(DEFAULT_SWIPE_THRESHOLD)

            clickTimeLimit.progress = (DEFAULT_CLICK_TIME_LIMIT * 100).toInt()
            clickTimeLimitValue.text = String.format("%.2f sec", DEFAULT_CLICK_TIME_LIMIT)
            saveClickTimeLimit(DEFAULT_CLICK_TIME_LIMIT)

            acceleratorSensitivity.progress = (DEFAULT_ACCELERATOR_SENSITIVITY * 10).toInt()
            acceleratorValue.text = String.format("%.1f", DEFAULT_ACCELERATOR_SENSITIVITY)
            saveAcceleratorSensitivity(DEFAULT_ACCELERATOR_SENSITIVITY)

            brakeSensitivity.progress = (DEFAULT_BRAKE_SENSITIVITY * 10).toInt()
            brakeValue.text = String.format("%.1f", DEFAULT_BRAKE_SENSITIVITY)
            saveBrakeSensitivity(DEFAULT_BRAKE_SENSITIVITY)

            switchMuteVideo.isChecked = DEFAULT_MUTE_VIDEO
            saveMuteVideo(DEFAULT_MUTE_VIDEO)

            switchTelemetry.isChecked = DEFAULT_TELEMETRY_ENABLED
            saveTelemetryEnabled(DEFAULT_TELEMETRY_ENABLED)
        }
    }

    private fun saveSteeringAngle(angle: Int) {
        val sharedPrefs = getSharedPreferences("steering_prefs", MODE_PRIVATE)
        with(sharedPrefs.edit()) {
            putInt("steering_angle", angle)
            apply()
        }
    }

    private fun saveSwipeThreshold(threshold: Float) {
        val sharedPrefs = getSharedPreferences("steering_prefs", MODE_PRIVATE)
        with(sharedPrefs.edit()) {
            putFloat(PREF_SWIPE_THRESHOLD, threshold)
            apply()
        }
    }

    private fun saveClickTimeLimit(timeLimit: Float) {
        val sharedPrefs = getSharedPreferences("steering_prefs", MODE_PRIVATE)
        with(sharedPrefs.edit()) {
            putFloat(PREF_CLICK_TIME_LIMIT, timeLimit)
            apply()
        }
    }

    private fun saveAcceleratorSensitivity(sensitivity: Float) {
        val sharedPrefs = getSharedPreferences("steering_prefs", MODE_PRIVATE)
        with(sharedPrefs.edit()) {
            putFloat(PREF_ACCELERATOR_SENSITIVITY, sensitivity)
            apply()
        }
    }

    private fun saveBrakeSensitivity(sensitivity: Float) {
        val sharedPrefs = getSharedPreferences("steering_prefs", MODE_PRIVATE)
        with(sharedPrefs.edit()) {
            putFloat(PREF_BRAKE_SENSITIVITY, sensitivity)
            apply()
        }
    }

    private fun saveMuteVideo(mute: Boolean) {
        val sharedPrefs = getSharedPreferences("steering_prefs", MODE_PRIVATE)
        with(sharedPrefs.edit()) {
            putBoolean(PREF_MUTE_VIDEO, mute)
            apply()
        }
    }

    private fun saveTelemetryEnabled(enabled: Boolean) {
        val sharedPrefs = getSharedPreferences("steering_prefs", MODE_PRIVATE)
        with(sharedPrefs.edit()) {
            putBoolean(PREF_TELEMETRY_ENABLED, enabled)
            apply()
        }
    }

    companion object {
        // Definir las claves para las preferencias
        const val PREF_SWIPE_THRESHOLD = "pref_swipe_threshold"
        const val PREF_CLICK_TIME_LIMIT = "pref_click_time_limit"
        const val PREF_ACCELERATOR_SENSITIVITY = "pref_accelerator_sensitivity"
        const val PREF_BRAKE_SENSITIVITY = "pref_brake_sensitivity"
        const val PREF_MUTE_VIDEO = "pref_mute_video"
        const val PREF_TELEMETRY_ENABLED = "pref_telemetry_enabled"

        // Valores predeterminados
        const val DEFAULT_SWIPE_THRESHOLD = 4.0f // en mm
        const val DEFAULT_CLICK_TIME_LIMIT = 0.25f // en segundos
        const val DEFAULT_ACCELERATOR_SENSITIVITY = 0.3f // sensibilidad predeterminada
        const val DEFAULT_BRAKE_SENSITIVITY = 0.3f // sensibilidad predeterminada
        const val DEFAULT_MUTE_VIDEO = true // muteado por defecto
        const val DEFAULT_TELEMETRY_ENABLED = true
    }
}

