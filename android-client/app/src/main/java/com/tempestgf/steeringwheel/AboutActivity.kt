package com.tempestgf.steeringwheel

import android.os.Bundle
import android.widget.Button
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import java.util.Calendar
import com.tempestgf.steeringwheel.R

class AboutActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_about)

        // Configurar copyright dinámico
        val footerText: TextView = findViewById(R.id.footer_text)
        val currentYear = Calendar.getInstance().get(Calendar.YEAR)
        footerText.text = "© $currentYear Tempestgf"

        // Configuración del botón de regreso
        val backButton: Button = findViewById(R.id.button_back)
        backButton.setOnClickListener {
            finish()  // Cierra la actividad y vuelve al menú principal
        }
    }
}
