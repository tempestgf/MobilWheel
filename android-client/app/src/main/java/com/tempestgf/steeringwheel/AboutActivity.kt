package com.tempestgf.steeringwheel

import android.content.Intent
import android.media.MediaPlayer
import android.net.Uri
import android.os.Bundle
import android.widget.Button
import android.widget.LinearLayout
import android.widget.TextView
import android.widget.VideoView
import androidx.appcompat.app.AppCompatActivity
import java.util.Calendar
import com.tempestgf.steeringwheel.R

class AboutActivity : AppCompatActivity() {

    private var videoView: VideoView? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_about)

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
        
        val appVersionText: TextView = findViewById(R.id.app_version)
        try {
            val pInfo = packageManager.getPackageInfo(packageName, 0)
            appVersionText.text = "Versión " + pInfo.versionName
        } catch (e: Exception) {
            e.printStackTrace()
        }
        
        appVersionText.setOnClickListener {
            AppUpdater(this).checkForUpdates(manual = true)
        }

        // Configuración del botón de regreso
        val backButton: Button = findViewById(R.id.button_back)
        backButton.setOnClickListener {
            finish()  // Cierra la actividad y vuelve al menú principal
            overridePendingTransition(android.R.anim.fade_in, android.R.anim.fade_out)
        }

        // Configuración de enlaces sociales/web
        val discordLink: LinearLayout = findViewById(R.id.link_discord)
        val githubLink: LinearLayout = findViewById(R.id.link_github)
        val webLink: LinearLayout = findViewById(R.id.link_web)

        discordLink.setOnClickListener {
            openExternalUrl(getString(R.string.about_url_discord))
        }
        githubLink.setOnClickListener {
            openExternalUrl(getString(R.string.about_url_github))
        }
        webLink.setOnClickListener {
            openExternalUrl(getString(R.string.about_url_web))
        }
    }

    private fun openExternalUrl(url: String) {
        val intent = Intent(Intent.ACTION_VIEW, Uri.parse(url))
        startActivity(intent)
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
