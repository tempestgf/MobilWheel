package com.tempestgf.steeringwheel

import android.content.Intent
import android.media.MediaPlayer
import android.net.Uri
import android.os.Bundle
import android.widget.Button
import android.widget.TextView
import android.widget.VideoView
import com.google.android.material.floatingactionbutton.FloatingActionButton
import androidx.appcompat.app.AppCompatActivity
import java.util.Calendar
import com.tempestgf.steeringwheel.R

class MainActivity : AppCompatActivity() {
    
    private var videoView: VideoView? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main_menu)  // Cargar el menú principal

        // Configurar video de fondo
        videoView = findViewById(R.id.video_background)
        val uri = Uri.parse("android.resource://" + packageName + "/" + R.raw.hero)
        videoView?.setVideoURI(uri)
        videoView?.setOnPreparedListener { mediaPlayer ->
            mediaPlayer.isLooping = true
            
            // Aplicar configuración de mute
            val sharedPrefs = getSharedPreferences("steering_prefs", MODE_PRIVATE)
            val isMuted = sharedPrefs.getBoolean(SettingsActivity.PREF_MUTE_VIDEO, SettingsActivity.DEFAULT_MUTE_VIDEO)
            if (isMuted) {
                mediaPlayer.setVolume(0f, 0f)
            } else {
                mediaPlayer.setVolume(1f, 1f)
            }

            // Ajustar el video para que llene la pantalla (Center Crop)
            val videoRatio = mediaPlayer.videoWidth / mediaPlayer.videoHeight.toFloat()
            val screenRatio = videoView!!.width / videoView!!.height.toFloat()
            val scaleX = videoRatio / screenRatio
            if (scaleX >= 1f) {
                videoView!!.scaleX = scaleX
            } else {
                videoView!!.scaleY = 1f / scaleX
            }
        }

        // Configurar copyright dinámico
        val footerText: TextView = findViewById(R.id.footer_text)
        val currentYear = Calendar.getInstance().get(Calendar.YEAR)
        footerText.text = "© $currentYear Geneon"

        val startButton: Button = findViewById(R.id.button_start)
        startButton.setOnClickListener {
            // Lanzar la actividad de la sección de volante
            val intent = Intent(this, SteeringWheelActivity::class.java)
            startActivity(intent)
        }

        val dashboardButton: Button = findViewById(R.id.button_dashboard)
        dashboardButton.setOnClickListener {
            // Lanzar la actividad de dashboard
            val intent = Intent(this, DashboardActivity::class.java)
            startActivity(intent)
        }

        // Otros botones del menú
        val settingsButton: Button = findViewById(R.id.button_settings)
        settingsButton.setOnClickListener {
            val intent = Intent(this, SettingsActivity::class.java)
            startActivity(intent)
        }

        val aboutButton: Button = findViewById(R.id.button_about)
        aboutButton.setOnClickListener {
            val intent = Intent(this, AboutActivity::class.java)
            startActivity(intent)
            overridePendingTransition(android.R.anim.fade_in, android.R.anim.fade_out)
        }

        // Configuración del botón de actualización
        val fabUpdate: FloatingActionButton = findViewById(R.id.fab_update)
        fabUpdate.setOnClickListener {
            AppUpdater(this).checkForUpdates(manual = true)
        }

        // Silent check for updates
        AppUpdater(this).checkForUpdates(manual = false)
    }

    override fun onResume() {
        super.onResume()
        videoView?.seekTo(VideoPlaybackManager.currentPosition)
        videoView?.start()
    }

    override fun onPause() {
        super.onPause()
        VideoPlaybackManager.currentPosition = videoView?.currentPosition ?: 0
        videoView?.pause()
    }
}
