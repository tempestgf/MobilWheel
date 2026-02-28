package com.tempestgf.steeringwheel

import android.content.Intent
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.widget.ImageView
import androidx.appcompat.app.AppCompatActivity

class SplashActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.splash_screen)

        val splashLogo: ImageView = findViewById(R.id.splash_logo)
        
        // Configurar estado inicial para la animación
        splashLogo.alpha = 0f
        splashLogo.scaleX = 0.5f
        splashLogo.scaleY = 0.5f
        
        // Iniciar animación suave (fade in + scale up)
        splashLogo.animate()
            .alpha(1f)
            .scaleX(1f)
            .scaleY(1f)
            .setDuration(1200)
            .withEndAction {
                // Esperar un poco después de la animación antes de ir a MainActivity
                Handler(Looper.getMainLooper()).postDelayed({
                    val intent = Intent(this, MainActivity::class.java)
                    startActivity(intent)
                    finish()
                    // Transición suave entre activities
                    overridePendingTransition(android.R.anim.fade_in, android.R.anim.fade_out)
                }, 500)
            }
            .start()
    }
}
