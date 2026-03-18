package com.tempestgf.steeringwheel

import android.app.AlertDialog
import android.app.DownloadManager
import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.content.IntentFilter
import android.net.Uri
import android.os.Environment
import android.os.Handler
import android.os.Looper
import android.util.Log
import android.widget.Toast
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.GlobalScope
import kotlinx.coroutines.launch
import org.json.JSONObject
import java.net.HttpURLConnection
import java.net.URL

class AppUpdater(private val context: Context) {

    private val UPDATE_URL = "https://mobilwheel.com/update/android-manifest.json"
    private var downloadId: Long = -1

    fun checkForUpdates(manual: Boolean = false) {
        if (manual) {
            Toast.makeText(context, "Buscando actualizaciones...", Toast.LENGTH_SHORT).show()
        }
        GlobalScope.launch(Dispatchers.IO) {
            try {
                val url = URL(UPDATE_URL)
                val connection = url.openConnection() as HttpURLConnection
                connection.requestMethod = "GET"
                connection.connectTimeout = 5000
                connection.readTimeout = 5000

                if (connection.responseCode == 200) {
                    val stream = connection.inputStream
                    val jsonStr = stream.bufferedReader().use { it.readText() }
                    val json = JSONObject(jsonStr)

                    val onlineVersion = json.getString("version")
                    val downloadUrl = json.getString("download_url")
                    val notes = json.optString("notes", "")

                    val currentVersion = context.packageManager.getPackageInfo(context.packageName, 0).versionName

                    if (isNewerVersion(onlineVersion, currentVersion)) {
                        Handler(Looper.getMainLooper()).post {
                            showUpdateDialog(onlineVersion, notes, downloadUrl)
                        }
                    } else if (manual) {
                        Handler(Looper.getMainLooper()).post {
                            Toast.makeText(context, "Ya tienes la última versión: $currentVersion", Toast.LENGTH_SHORT).show()
                        }
                    }
                } else if (manual) {
                    Handler(Looper.getMainLooper()).post {
                        Toast.makeText(context, "Error conectando al servidor de actualizaciones.", Toast.LENGTH_SHORT).show()
                    }
                }
            } catch (e: Exception) {
                Log.e("Updater", "Error checking for updates", e)
                if (manual) {
                    Handler(Looper.getMainLooper()).post {
                        Toast.makeText(context, "Error buscando actualizaciones: ${e.message}", Toast.LENGTH_SHORT).show()
                    }
                }
            }
        }
    }

    private fun isNewerVersion(onlineVersion: String, currentVersion: String): Boolean {
        val onlineParts = onlineVersion.split(".").map { it.toIntOrNull() ?: 0 }
        val currentParts = currentVersion.split(".").map { it.toIntOrNull() ?: 0 }

        val maxLen = maxOf(onlineParts.size, currentParts.size)
        for (i in 0 until maxLen) {
            val ov = if (i < onlineParts.size) onlineParts[i] else 0
            val cv = if (i < currentParts.size) currentParts[i] else 0
            if (ov > cv) return true
            if (ov < cv) return false
        }
        return false
    }

    private fun showUpdateDialog(newVersion: String, notes: String, downloadUrl: String) {
        AlertDialog.Builder(context, android.R.style.Theme_DeviceDefault_Dialog_Alert)
            .setTitle("Actualización Disponible ($newVersion)")
            .setMessage("Hay una nueva versión disponible.\n\nNovedades:\n$notes\n\n¿Deseas descargarla e instalarla ahora?")
            .setPositiveButton("Actualizar") { _, _ ->
                startDownload(downloadUrl, newVersion)
            }
            .setNegativeButton("Más tarde", null)
            .show()
    }

    private fun startDownload(downloadUrl: String, newVersion: String) {
        try {
            val request = DownloadManager.Request(Uri.parse(downloadUrl))
                .setTitle("MobileWheel Client")
                .setDescription("Descargando la versión $newVersion")
                .setNotificationVisibility(DownloadManager.Request.VISIBILITY_VISIBLE_NOTIFY_COMPLETED)
                // Use clear filename without spaces
                .setDestinationInExternalPublicDir(Environment.DIRECTORY_DOWNLOADS, "MobileWheelClient-update-$newVersion.apk")
                .setAllowedOverMetered(true)
                .setAllowedOverRoaming(true)
                .setMimeType("application/vnd.android.package-archive")

            val dm = context.getSystemService(Context.DOWNLOAD_SERVICE) as DownloadManager
            downloadId = dm.enqueue(request)

            Toast.makeText(context, "Descargando actualización en segundo plano...", Toast.LENGTH_LONG).show()

            val onComplete = object : BroadcastReceiver() {
                override fun onReceive(ctxt: Context, intent: Intent) {
                    val id = intent.getLongExtra(DownloadManager.EXTRA_DOWNLOAD_ID, -1)
                    if (id == downloadId) {
                        try {
                            val uri = dm.getUriForDownloadedFile(downloadId)
                            if (uri != null) {
                                installApk(uri)
                            } else {
                                Toast.makeText(context, "Descarga completada, abre Notificaciones para instalar.", Toast.LENGTH_LONG).show()
                            }
                        } catch (e: Exception) {
                            Log.e("Updater", "Error getting URI", e)
                        }
                        context.unregisterReceiver(this)
                    }
                }
            }

            if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.TIRAMISU) {
                context.registerReceiver(onComplete, IntentFilter(DownloadManager.ACTION_DOWNLOAD_COMPLETE), Context.RECEIVER_EXPORTED)
            } else {
                context.registerReceiver(onComplete, IntentFilter(DownloadManager.ACTION_DOWNLOAD_COMPLETE))
            }
        } catch (e: Exception) {
            Log.e("Updater", "Failed to start download via DownloadManager", e)
            // Fallback: Open URL in browser
            Toast.makeText(context, "Abriendo navegador para descargar...", Toast.LENGTH_SHORT).show()
            val browserIntent = Intent(Intent.ACTION_VIEW, Uri.parse(downloadUrl))
            context.startActivity(browserIntent)
        }
    }

    private fun installApk(apkUri: Uri) {
        try {
            val intent = Intent(Intent.ACTION_VIEW).apply {
                setDataAndType(apkUri, "application/vnd.android.package-archive")
                flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_GRANT_READ_URI_PERMISSION
            }
            context.startActivity(intent)
        } catch (e: Exception) {
            Log.e("Updater", "Error installing APK", e)
            Toast.makeText(context, "Toca la notificación de descarga para instalar manualmente.", Toast.LENGTH_LONG).show()
        }
    }
}