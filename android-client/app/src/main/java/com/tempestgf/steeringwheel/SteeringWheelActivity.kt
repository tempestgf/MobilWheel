package com.tempestgf.steeringwheel

import android.animation.Animator
import android.animation.AnimatorListenerAdapter
import android.animation.AnimatorSet
import android.animation.ObjectAnimator
import android.annotation.SuppressLint
import android.content.Context
import android.hardware.Sensor
import android.hardware.SensorEvent
import android.hardware.SensorEventListener
import android.hardware.SensorManager
import android.media.AudioAttributes
import android.media.SoundPool
import android.os.Build
import android.os.Bundle
import android.os.VibrationEffect
import android.os.Vibrator
import android.os.VibratorManager
import android.text.InputType
import android.util.Log
import android.view.KeyEvent
import android.view.MotionEvent
import android.view.View
import android.widget.ArrayAdapter
import android.widget.Button
import android.widget.EditText
import android.widget.LinearLayout
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.ContextCompat
import com.google.android.material.dialog.MaterialAlertDialogBuilder
import kotlinx.coroutines.*
import java.io.DataOutputStream
import java.io.IOException
import java.net.DatagramPacket
import java.net.DatagramSocket
import java.net.Inet4Address
import java.net.InetAddress
import java.net.NetworkInterface
import java.net.Socket
import java.net.SocketTimeoutException
import java.nio.ByteBuffer
import java.nio.ByteOrder
import java.util.concurrent.LinkedBlockingQueue
import android.content.Intent
import android.content.IntentFilter
import android.os.BatteryManager
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

class SteeringWheelActivity : AppCompatActivity(), SensorEventListener {

    // ── Sensores ──────────────────────────────────────────────────────────────
    private lateinit var sensorManager: SensorManager
    private var accelerometer: Sensor? = null

    // Suavizado de ángulo para la contra-rotación del HUD (estilo MOZA Vision GS)
    private var smoothedHudAngle = 0f
    private val HUD_ALPHA = 0.18f

    // ── Vistas funcionales ────────────────────────────────────────────────────
    private lateinit var accelerateIndicator: View
    private lateinit var brakeIndicator: View
    private lateinit var accelerateTopIndicator: View
    private lateinit var brakeTopIndicator: View
    private lateinit var buttonLeftTop: Button
    private lateinit var buttonLeftBottom: Button
    private lateinit var buttonRightTop: Button
    private lateinit var buttonRightBottom: Button

    // ── Vistas HUD ────────────────────────────────────────────────────────────
    private lateinit var gearContainer: LinearLayout
    private lateinit var gearIndicatorView: TextView
    private lateinit var speedValueView: TextView
    private lateinit var rpmDots: List<View>   // 15 LEDs: verde(1-5) → amarillo(6-10) → rojo(11-15, zona de cambio)
    private lateinit var ipAddressDisplay: TextView
    private lateinit var rpmIndicator: TextView
    private lateinit var connectionLabel: TextView
    private lateinit var connectionDot: View
    private lateinit var batteryStatusText: TextView
    private lateinit var timeStatusText: TextView
    private lateinit var wifiStatusText: TextView

    // ── Vistas Telemetría (para ocultar/mostrar) ──────────────────────────────
    private lateinit var cockpitGlow: View
    private lateinit var cockpitArcOuter: View
    private lateinit var cockpitArcInner: View
    private lateinit var horizonLine: View
    private lateinit var centerGearBlock: View
    private lateinit var speedContainer: View
    private lateinit var ffbContainer: View
    private lateinit var rpmContainer: View

    // ── Red TCP ───────────────────────────────────────────────────────────────
    private var serverAddress = "192.168.176.150"
    private val serverPort = 12345
    private var socket: Socket? = null
    private var outputStream: DataOutputStream? = null
    private val commandQueue = LinkedBlockingQueue<String>()

    // ── Telemetría AC (UDP) ───────────────────────────────────────────────────
    /**
     * Puerto UDP de telemetría de Assetto Corsa.
     * AC escucha en este puerto en el PC y envía RTCarInfo periódicamente.
     */
    private val AC_TELEMETRY_PORT = 9996
    private var acSocket: DatagramSocket? = null
    private var acJob: Job? = null

    // ── Parámetros de steering ────────────────────────────────────────────────
    private var lastY: Float = 0f
    private val threshold = 0.010f
    private var maxSteeringAngle: Float = 90f
    private var swipeThresholdInPx: Float = 0f
    private var accelerationSensitivity: Float = 0.5f
    private var brakeSensitivity: Float = 0.5f
    private var clickTimeLimit: Float = 0.25f

    // ── Audio y vibración ─────────────────────────────────────────────────────
    private lateinit var soundPool: SoundPool
    private var soundId: Int = 0
    private lateinit var vibrator: Vibrator

    private var isDialogShowing = false
    
    // ── Actualización de estado (Batería, Hora, Ping) ─────────────────────────
    private var statusUpdateJob: Job? = null
    private var lastPingTime: Long = 0
    private var currentPing: Long = 0

    // ─────────────────────────────────────────────────────────────────────────
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        initializeUIElements()
        setupTouchListeners()
        setupButtonListeners()

        sensorManager = getSystemService(SENSOR_SERVICE) as SensorManager
        accelerometer = sensorManager.getDefaultSensor(Sensor.TYPE_ACCELEROMETER)
        if (accelerometer != null) {
            sensorManager.registerListener(this, accelerometer, SensorManager.SENSOR_DELAY_GAME)
        } else {
            Toast.makeText(this, "Accelerometer not available", Toast.LENGTH_SHORT).show()
        }

        val audioAttributes = AudioAttributes.Builder()
            .setUsage(AudioAttributes.USAGE_GAME)
            .setContentType(AudioAttributes.CONTENT_TYPE_SONIFICATION)
            .build()
        soundPool = SoundPool.Builder().setMaxStreams(1).setAudioAttributes(audioAttributes).build()
        soundId = soundPool.load(this, R.raw.gear_shift, 1)

        vibrator = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
            val mgr = getSystemService(Context.VIBRATOR_MANAGER_SERVICE) as VibratorManager
            mgr.defaultVibrator
        } else {
            @Suppress("DEPRECATION")
            getSystemService(Context.VIBRATOR_SERVICE) as Vibrator
        }

        setConnectionState(false, null)
        showConnectionOptions()
        
        startStatusUpdates()
    }

    // ─────────────────────────────────────────────────────────────────────────
    // ACTUALIZACIÓN DE ESTADO (Batería, Hora, Ping)
    // ─────────────────────────────────────────────────────────────────────────
    private fun startStatusUpdates() {
        statusUpdateJob = CoroutineScope(Dispatchers.Main).launch {
            val timeFormat = SimpleDateFormat("HH:mm", Locale.getDefault())
            while (isActive) {
                // Actualizar hora
                timeStatusText.text = timeFormat.format(Date())
                
                // Actualizar batería
                val batteryStatus: Intent? = IntentFilter(Intent.ACTION_BATTERY_CHANGED).let { ifilter ->
                    applicationContext.registerReceiver(null, ifilter)
                }
                val level: Int = batteryStatus?.getIntExtra(BatteryManager.EXTRA_LEVEL, -1) ?: -1
                val scale: Int = batteryStatus?.getIntExtra(BatteryManager.EXTRA_SCALE, -1) ?: -1
                val batteryPct = if (level != -1 && scale != -1) (level * 100 / scale.toFloat()).toInt() else -1
                
                if (batteryPct != -1) {
                    batteryStatusText.text = "BAT: $batteryPct%"
                    // Cambiar color si la batería es baja
                    if (batteryPct <= 15) {
                        batteryStatusText.setTextColor(0xFFFF6B6B.toInt()) // Rojo
                    } else {
                        batteryStatusText.setTextColor(0x55FFFFFF.toInt()) // Blanco semi-transparente
                    }
                }
                
                // Actualizar ping (simulado o real si hay conexión)
                if (isConnected()) {
                    // Enviar un comando de ping ligero si es necesario, o usar el tiempo de respuesta de telemetría
                    // Por ahora mostramos un valor estimado basado en la conexión local
                    wifiStatusText.text = "PING: <5ms"
                    wifiStatusText.setTextColor(0xFF4ADE80.toInt()) // Verde
                } else {
                    wifiStatusText.text = "PING: --"
                    wifiStatusText.setTextColor(0x55FFFFFF.toInt())
                }
                
                delay(10000) // Actualizar cada 10 segundos
            }
        }
    }

    // ─────────────────────────────────────────────────────────────────────────
    // INICIALIZACIÓN DE VISTAS
    // ─────────────────────────────────────────────────────────────────────────
    private fun initializeUIElements() {
        accelerateIndicator    = findViewById(R.id.accelerateIndicator)
        brakeIndicator         = findViewById(R.id.brakeIndicator)
        accelerateTopIndicator = findViewById(R.id.accelerateTopIndicator)
        brakeTopIndicator      = findViewById(R.id.brakeTopIndicator)
        buttonLeftTop          = findViewById(R.id.button_left_top)
        buttonLeftBottom       = findViewById(R.id.button_left_bottom)
        buttonRightTop         = findViewById(R.id.button_right_top)
        buttonRightBottom      = findViewById(R.id.button_right_bottom)

        gearContainer      = findViewById(R.id.gearContainer)
        gearIndicatorView  = findViewById(R.id.gearIndicator)
        speedValueView     = findViewById(R.id.speedValue)
        ipAddressDisplay   = findViewById(R.id.ipAddressDisplay)
        rpmIndicator       = findViewById(R.id.rpmIndicator)
        connectionLabel    = findViewById(R.id.connectionLabel)
        connectionDot      = findViewById(R.id.connectionDot)
        batteryStatusText  = findViewById(R.id.batteryStatusText)
        timeStatusText     = findViewById(R.id.timeStatusText)
        wifiStatusText     = findViewById(R.id.wifiStatusText)

        cockpitGlow        = findViewById(R.id.cockpitGlow)
        cockpitArcOuter    = findViewById(R.id.cockpitArcOuter)
        cockpitArcInner    = findViewById(R.id.cockpitArcInner)
        horizonLine        = findViewById(R.id.horizonLine)
        centerGearBlock    = findViewById(R.id.centerGearBlock)
        speedContainer     = findViewById(R.id.speedContainer)
        ffbContainer       = findViewById(R.id.ffbContainer)
        rpmContainer       = findViewById(R.id.rpmContainer)

        rpmDots = listOf(
            R.id.rpmDot1,  R.id.rpmDot2,  R.id.rpmDot3,  R.id.rpmDot4,  R.id.rpmDot5,
            R.id.rpmDot6,  R.id.rpmDot7,  R.id.rpmDot8,  R.id.rpmDot9,  R.id.rpmDot10,
            R.id.rpmDot11, R.id.rpmDot12, R.id.rpmDot13, R.id.rpmDot14, R.id.rpmDot15
        ).map { id -> findViewById(id) }
    }

    // ─────────────────────────────────────────────────────────────────────────
    // ESTADO DE CONEXIÓN
    // ─────────────────────────────────────────────────────────────────────────
    private fun setConnectionState(connected: Boolean, ip: String?) {
        runOnUiThread {
            if (connected && ip != null) {
                connectionLabel.text = "CONNECTED"
                connectionLabel.setTextColor(0xFF4ADE80.toInt())
                connectionDot.setBackgroundResource(R.drawable.cockpit_dot_green)
                ipAddressDisplay.text = ip
            } else {
                connectionLabel.text = "OFFLINE"
                connectionLabel.setTextColor(0xFFFF6B6B.toInt())
                connectionDot.background = null
                connectionDot.setBackgroundColor(0x66FF6B6B.toInt())
                ipAddressDisplay.text = "-.-.-.−"
            }
        }
    }

    // ─────────────────────────────────────────────────────────────────────────
    // TELEMETRÍA ASSETTO CORSA (UDP port 9996)
    // ─────────────────────────────────────────────────────────────────────────

    /**
     * Inicia la recepción de telemetría UDP de Assetto Corsa con reintento automático.
     *
     * Protocolo AC UDP:
     *  1. Enviar HandshakerRequest(identifier=1, version=1, operationId=0) → puerto 9996
     *  2. Recibir HandshakerResponse (208 bytes): confirma que AC está activo en pista
     *  3. Enviar HandshakerRequest(operationId=1) para suscribirse a RTCarInfo
     *  4. AC envía RTCarInfo periódicamente. Campos que usamos:
     *       offset  8: float speedKmh
     *       offset 68: float engineRPM
     *       offset 76: int   gear  (0=R, 1=N, 2=1ª, 3=2ª...)
     *
     * Si AC no responde (menú, carga…), reintenta cada 5 segundos automáticamente.
     */
    private fun startAcTelemetry() {
        acJob?.cancel()
        acJob = CoroutineScope(Dispatchers.IO).launch {
            // Retry loop: reconecta si el handshake falla o la sesión se interrumpe
            while (isActive) {
                try {
                    runAcTelemetrySession()
                } catch (e: CancellationException) {
                    break
                } catch (e: SocketTimeoutException) {
                    Log.d("AC_Telemetry", "AC sin respuesta — reintentando en 5 s…")
                } catch (e: Exception) {
                    Log.d("AC_Telemetry", "Sesión AC terminada (${e.message}) — reintentando…")
                }
                if (isActive) {
                    try { delay(5000) } catch (_: CancellationException) { break }
                }
            }
        }
    }

    /**
     * Una sesión de telemetría: handshake → suscripción → bucle de recepción.
     * Lanza SocketTimeoutException si AC no responde al handshake (menú, no hay sesión).
     */
    private suspend fun runAcTelemetrySession() {
        acSocket?.close()
        val socket = DatagramSocket()
        acSocket = socket

        val pcAddress = InetAddress.getByName(serverAddress)

        // 1. Handshake inicial
        sendAcHandshake(pcAddress, operationId = 0)

        // 2. Esperar respuesta (lanza SocketTimeoutException si AC no está en pista)
        val hsBuffer = ByteArray(256)
        val hsPacket = DatagramPacket(hsBuffer, hsBuffer.size)
        socket.soTimeout = 3000
        socket.receive(hsPacket)
        Log.d("AC_Telemetry", "Handshake OK (${hsPacket.length} bytes) — conectado a AC")

        // 3. Suscribirse a RTCarInfo en tiempo real
        sendAcHandshake(pcAddress, operationId = 1)
        socket.soTimeout = 2000

        // 4. Bucle de recepción de RTCarInfo
        while (currentCoroutineContext().isActive) {
            val buf = ByteArray(1024)
            val pkt = DatagramPacket(buf, buf.size)
            try {
                socket.receive(pkt)
                parseAcRtCarInfo(pkt.data, pkt.length)
            } catch (e: SocketTimeoutException) {
                // AC pausado/en menú durante la sesión, seguir esperando
            }
        }
    }

    // ─────────────────────────────────────────────────────────────────────────
    // RECEPTOR TCP DE TELEMETRÍA (el servidor Python reenvía datos de AC)
    // ─────────────────────────────────────────────────────────────────────────

    /**
     * Arranca una corutina que lee líneas entrantes del socket TCP del servidor Python.
     * El servidor envía "T:velocidad:marcha:rpm\n" cuando recibe datos de AC.
     */
    private fun startTcpReceiver() {
        CoroutineScope(Dispatchers.IO).launch {
            try {
                val reader = socket?.getInputStream()?.bufferedReader() ?: return@launch
                while (isConnected()) {
                    try {
                        val line = reader.readLine() ?: break   // null = servidor cerró
                        if (line.startsWith("T:")) parseTelemetryLine(line)
                    } catch (e: java.net.SocketTimeoutException) {
                        // Sin datos aún, seguir esperando
                    } catch (e: IOException) {
                        break
                    }
                }
            } catch (e: Exception) {
                Log.e("TcpReceiver", "Error: ${e.message}")
            }
        }
    }

    /**
     * Parsea "T:velocidad:marcha:rpm" y actualiza el HUD.
     * Marcha:  0=R, 1=N, 2=1ª, 3=2ª, …  (igual que AC UDP)
     * 
     * 15 dots distribuidos en 3 zonas de color:
     *   Verde  (1-5):   30–62% del rango — zona segura
     *   Amarillo (6-10): 64–82% del rango — RPM altas, prepararse
     *   Rojo (11-15):    85–97% del rango — ¡ZONA DE CAMBIO!
     *
     * Cuando los 5 dots rojos estén encendidos → cambiar marcha AHORA.
     */
    private fun parseTelemetryLine(line: String) {
        val parts = line.split(":")
        if (parts.size != 4) return
        val speed   = parts[1].toIntOrNull() ?: return
        val gearRaw = parts[2].toIntOrNull() ?: return
        val rpm     = parts[3].toIntOrNull() ?: return

        // RPM adaptativo: detecta el rango máximo del coche
        val rpmMax = when {
            rpm > 13000 -> 16000f  // F1, LMP1 (muy alta revolución)
            rpm > 10000 -> 13000f  // GT3, prototipos modernos
            rpm > 8000  -> 10000f  // Deportivos de calle, GT4
            rpm > 6500  -> 8500f   // Deportivos clásicos
            else        -> 7000f   // Coches turismo, clásicos lentos
        }
        
        val rpmFraction = (rpm / rpmMax).coerceIn(0f, 1f)
        
        // Zona de cambio óptimo
        val optimalShiftStart = 0.85f
        val redlineStart = 0.95f

        runOnUiThread {
            gearIndicatorView.text = gearLabel(gearRaw)
            speedValueView.text    = speed.toString()
            
            // Actualizar RPM en barra superior con color dinámico
            rpmIndicator.text = "$rpm RPM"
            
            // Color del texto según zona
            rpmIndicator.setTextColor(when {
                rpmFraction >= redlineStart      -> 0xFFFF0000.toInt()  // Rojo brillante (limitador!)
                rpmFraction >= optimalShiftStart -> 0xFFf7768e.toInt()  // Rosa/Rojo (¡cambiar!)
                rpmFraction >= 0.70f             -> 0xFFe0af68.toInt()  // Amarillo (prepararse)
                else                             -> 0xFFff9e64.toInt()  // Naranja (normal)
            })
            
            // 15 dots con distribución no-lineal optimizada para shift lights
            // Verde (1-5):  30% → 62%  |  Amarillo (6-10): 64% → 82%  |  Rojo (11-15): 85% → 97%
            val thresholds = floatArrayOf(
                0.30f, 0.38f, 0.46f, 0.54f, 0.62f,  // Verde: zona segura
                0.64f, 0.68f, 0.72f, 0.77f, 0.82f,  // Amarillo: altas RPM
                0.85f, 0.88f, 0.91f, 0.94f, 0.97f   // Rojo: ¡CAMBIAR!
            )
            
            rpmDots.forEachIndexed { i, dot ->
                val lit = rpmFraction >= thresholds[i]
                dot.alpha = if (lit) 1.0f else 0.15f
            }
        }
    }

    /**
     * Envía un paquete de handshake al servidor de Assetto Corsa.
     * HandshakerRequest: { int identifier=1, int version=1, int operationId }
     */
    private fun sendAcHandshake(address: InetAddress, operationId: Int) {
        val buf = ByteBuffer.allocate(12).order(ByteOrder.LITTLE_ENDIAN)
        buf.putInt(1)           // identifier
        buf.putInt(1)           // version
        buf.putInt(operationId)
        val pkt = DatagramPacket(buf.array(), 12, address, AC_TELEMETRY_PORT)
        acSocket?.send(pkt)
    }

    /**
     * Parsea el struct RTCarInfo de Assetto Corsa (little-endian, Windows struct layout).
     *
     * Especificación oficial (docs.google.com/document/d/1KfkZiIluXZ6mMhLWfDX1qAGbvhGRC3ZUzjVIt5FQpp4):
     *
     *  +0   char     identifier   → 'a'  (1 byte)
     *  +1   byte[3]  padding      (alineación del int que sigue)
     *  +4   int      size
     *  +8   float    speed_Kmh    ← leemos aquí
     *  +12  float    speed_Mph
     *  +16  float    speed_Ms
     *  +20  bool[6]  flags (abs x2, tc x2, pit, limiter)
     *  +26  byte[2]  padding      (alineación del float que sigue)
     *  +28  float    accG_vertical
     *  +32  float    accG_horizontal
     *  +36  float    accG_frontal
     *  +40  int      lapTime
     *  +44  int      lastLap
     *  +48  int      bestLap
     *  +52  int      lapCount
     *  +56  float    gas
     *  +60  float    brake
     *  +64  float    clutch
     *  +68  float    engineRPM
     *  +72  float    steer
     *  +76  int      gear         ← leemos aquí (0=R, 1=N, 2=1ª, 3=2ª…)
     */
    private fun parseAcRtCarInfo(data: ByteArray, length: Int) {
        if (length < 80) return

        // byte 0 = 'a' (identificador char según spec AC)
        if (data[0] != 'a'.code.toByte()) return

        val buf = ByteBuffer.wrap(data).order(ByteOrder.LITTLE_ENDIAN)

        buf.position(8)
        val speedKmh = buf.getFloat()

        buf.position(68)
        val engineRPM = buf.getFloat()

        buf.position(76)
        val rawGear = buf.getInt()

        // Descartar paquetes con valores imposibles
        if (speedKmh < 0f || speedKmh > 500f) return
        if (engineRPM < 0f || engineRPM > 20000f) return

        val gearText    = gearLabel(rawGear)
        val speedText   = speedKmh.toInt().toString()
        val rpmFraction = (engineRPM / 9000f).coerceIn(0f, 1f)

        runOnUiThread {
            gearIndicatorView.text = gearText
            speedValueView.text    = speedText
            // Iluminar dots según RPM: dot i se activa cuando rpm >= (i+1)/10 del total
            rpmDots.forEachIndexed { i, dot ->
                dot.alpha = if (rpmFraction >= (i + 1) / 10f) 1.0f else 0.12f
            }
        }
    }

    /**
     * Convierte el int de marcha de AC a texto para el HUD.
     * Codificación AC: 0 = Reversa, 1 = Neutro, 2 = 1ª, 3 = 2ª, …
     */
    private fun gearLabel(gear: Int): String = when {
        gear <= 0 -> "R"
        gear == 1 -> "N"
        else      -> (gear - 1).toString()
    }

    private fun stopAcTelemetry() {
        acJob?.cancel()
        acJob = null
        try { acSocket?.close() } catch (_: Exception) {}
        acSocket = null
        runOnUiThread {
            gearIndicatorView.text = "N"
            speedValueView.text    = "0"
            rpmIndicator.text      = "0 RPM"
            rpmIndicator.setTextColor(0xFFff9e64.toInt())  // Color naranja por defecto
            rpmDots.forEach { it.alpha = 0.12f }
        }
    }

    // ─────────────────────────────────────────────────────────────────────────
    // SENSOR: ACELERÓMETRO (steering + contra-rotación HUD)
    // ─────────────────────────────────────────────────────────────────────────
    
    // Variables to track continuous rotation
    private var lastRawAngle = 0f
    private var continuousAngle = 0f
    private var isFirstReading = true

    override fun onSensorChanged(event: SensorEvent?) {
        event?.let {
            if (it.sensor.type == Sensor.TYPE_ACCELEROMETER) {
                val rawY = it.values[1]
                val rawX = it.values[0]

                // Calculate raw angle using atan2 (-180 to 180)
                val rawAngle = Math.toDegrees(
                    Math.atan2(rawY.toDouble(), rawX.toDouble())
                ).toFloat()

                if (isFirstReading) {
                    lastRawAngle = rawAngle
                    continuousAngle = rawAngle
                    isFirstReading = false
                } else {
                    // Calculate the shortest angular distance between the new angle and the last angle
                    var delta = rawAngle - lastRawAngle
                    
                    // If the delta is greater than 180, it means we crossed the -180/180 boundary
                    if (delta > 180f) {
                        delta -= 360f
                    } else if (delta < -180f) {
                        delta += 360f
                    }
                    
                    // Add the continuous delta to our accumulated angle
                    continuousAngle += delta
                    lastRawAngle = rawAngle
                }

                // Use the continuous angle for steering
                val steeringAngle = continuousAngle

                // ── Contra-rotación del HUD (indicador de marcha siempre recto) ──
                smoothedHudAngle = HUD_ALPHA * steeringAngle + (1f - HUD_ALPHA) * smoothedHudAngle
                runOnUiThread { gearContainer.rotation = -smoothedHudAngle }

                // ── Enviar ángulo al servidor ──────────────────────────────────
                val normalized = mapSteeringAngleToServerRange(steeringAngle, maxSteeringAngle)
                val limited    = limitSteeringAngle(normalized, maxSteeringAngle)

                val rightInd = findViewById<View>(R.id.right_max_angle_indicator)
                val leftInd  = findViewById<View>(R.id.left_max_angle_indicator)
                rightInd.visibility = if (limited >= maxSteeringAngle) View.VISIBLE else View.GONE
                leftInd.visibility  = if (limited <= -maxSteeringAngle) View.VISIBLE else View.GONE

                if (Math.abs(limited - lastY) > threshold) {
                    lastY = limited
                    queueCommand("A:$limited")
                }
            }
        }
    }

    override fun onAccuracyChanged(sensor: Sensor?, accuracy: Int) {}

    private fun limitSteeringAngle(angle: Float, max: Float) = angle.coerceIn(-max, max)
    private fun mapSteeringAngleToServerRange(angle: Float, max: Float) = (angle / max) * 10f

    // ─────────────────────────────────────────────────────────────────────────
    // LISTENERS DE TOQUE
    // ─────────────────────────────────────────────────────────────────────────
    @SuppressLint("ClickableViewAccessibility")
    private fun setupTouchListeners() {
        val leftSide: View  = findViewById(R.id.left_side)
        val rightSide: View = findViewById(R.id.right_side)

        leftSide.setOnTouchListener(object : View.OnTouchListener {
            private var initialY = 0f
            override fun onTouch(v: View?, event: MotionEvent): Boolean {
                when (event.action) {
                    MotionEvent.ACTION_DOWN  -> { initialY = event.y; startBrake() }
                    MotionEvent.ACTION_MOVE  -> updateBrake(event.y - initialY)
                    MotionEvent.ACTION_UP,
                    MotionEvent.ACTION_CANCEL -> stopBrake()
                }
                return true
            }
        })

        rightSide.setOnTouchListener(object : View.OnTouchListener {
            private var initialY = 0f
            override fun onTouch(v: View?, event: MotionEvent): Boolean {
                when (event.action) {
                    MotionEvent.ACTION_DOWN  -> { initialY = event.y; startAccelerate() }
                    MotionEvent.ACTION_MOVE  -> updateAccelerate(event.y - initialY)
                    MotionEvent.ACTION_UP,
                    MotionEvent.ACTION_CANCEL -> stopAccelerate()
                }
                return true
            }
        })
    }

    // ─────────────────────────────────────────────────────────────────────────
    // FRENO  (deslizante rojo de arriba abajo)
    // ─────────────────────────────────────────────────────────────────────────
    private fun startBrake() {
        brakeIndicator.visibility = View.VISIBLE
        brakeIndicator.layoutParams.height = 0
        brakeIndicator.requestLayout()
    }

    private fun stopBrake() {
        brakeIndicator.visibility = View.GONE
        brakeTopIndicator.visibility = View.GONE
        queueCommand("C:0")
    }

    private fun updateBrake(deltaY: Float) {
        val progress = (deltaY * brakeSensitivity).toInt().coerceIn(0, 100)
        val lp = brakeIndicator.layoutParams
        lp.height = (resources.displayMetrics.heightPixels * (progress / 100.0)).toInt()
        brakeIndicator.layoutParams = lp
        brakeIndicator.visibility = View.VISIBLE
        brakeTopIndicator.visibility = if (progress >= 100) View.VISIBLE else View.GONE
        queueCommand("C:$progress")
    }

    // ─────────────────────────────────────────────────────────────────────────
    // ACELERADOR  (deslizante verde de arriba abajo)
    // ─────────────────────────────────────────────────────────────────────────
    private fun startAccelerate() {
        accelerateIndicator.visibility = View.VISIBLE
        accelerateIndicator.layoutParams.height = 0
        accelerateIndicator.requestLayout()
    }

    private fun stopAccelerate() {
        accelerateIndicator.visibility = View.GONE
        accelerateTopIndicator.visibility = View.GONE
        queueCommand("B:0")
    }

    private fun updateAccelerate(deltaY: Float) {
        val progress = (deltaY * accelerationSensitivity).toInt().coerceIn(0, 100)
        val lp = accelerateIndicator.layoutParams
        lp.height = (resources.displayMetrics.heightPixels * (progress / 100.0)).toInt()
        accelerateIndicator.layoutParams = lp
        accelerateIndicator.visibility = View.VISIBLE
        accelerateTopIndicator.visibility = if (progress >= 100) View.VISIBLE else View.GONE
        queueCommand("B:$progress")
    }

    // ─────────────────────────────────────────────────────────────────────────
    // BOTONES DE ACCIÓN
    // ─────────────────────────────────────────────────────────────────────────
    @SuppressLint("ClickableViewAccessibility")
    private fun setupButtonListeners() {
        val listener = View.OnTouchListener { v, event ->
            when (event.actionMasked) {
                MotionEvent.ACTION_DOWN ->
                    v.tag = Pair(event.y, System.currentTimeMillis())

                MotionEvent.ACTION_MOVE -> {
                    @Suppress("UNCHECKED_CAST")
                    val tag = v.tag as? Pair<Float, Long>
                    if (tag != null) {
                        val dy = event.y - tag.first
                        if (Math.abs(dy) > swipeThresholdInPx) {
                            when (v.id) {
                                R.id.button_left_top, R.id.button_left_bottom   -> updateBrake(dy)
                                R.id.button_right_top, R.id.button_right_bottom -> updateAccelerate(dy)
                            }
                            return@OnTouchListener true
                        }
                    }
                }

                MotionEvent.ACTION_UP -> {
                    @Suppress("UNCHECKED_CAST")
                    val tag = v.tag as? Pair<Float, Long>
                    if (tag != null) {
                        val dy      = event.y - tag.first
                        val elapsed = (System.currentTimeMillis() - tag.second) / 1000.0
                        if (Math.abs(dy) <= swipeThresholdInPx && elapsed <= clickTimeLimit) {
                            animateButtonPress(v)
                            playShiftSound()
                            vibrate(75)
                            when (v.id) {
                                R.id.button_left_top     -> queueCommand("D")
                                R.id.button_left_bottom  -> queueCommand("E")
                                R.id.button_right_top    -> queueCommand("F")
                                R.id.button_right_bottom -> queueCommand("G")
                            }
                            v.performClick()
                        } else {
                            when (v.id) {
                                R.id.button_left_top, R.id.button_left_bottom   -> stopBrake()
                                R.id.button_right_top, R.id.button_right_bottom -> stopAccelerate()
                            }
                        }
                    }
                }
            }
            true
        }

        buttonLeftTop.setOnTouchListener(listener)
        buttonLeftBottom.setOnTouchListener(listener)
        buttonRightTop.setOnTouchListener(listener)
        buttonRightBottom.setOnTouchListener(listener)
    }

    private fun animateButtonPress(view: View) {
        CoroutineScope(Dispatchers.Main).launch {
            view.isClickable = true
            val rotY = if (view.id == R.id.button_left_top || view.id == R.id.button_left_bottom) -5f else 5f
            val press = AnimatorSet().apply {
                playTogether(
                    ObjectAnimator.ofFloat(view, "rotationY", rotY),
                    ObjectAnimator.ofFloat(view, "scaleX", 0.97f),
                    ObjectAnimator.ofFloat(view, "scaleY", 0.97f)
                )
                duration = 10
            }
            val release = AnimatorSet().apply {
                playTogether(
                    ObjectAnimator.ofFloat(view, "rotationY", 0f),
                    ObjectAnimator.ofFloat(view, "scaleX", 1f),
                    ObjectAnimator.ofFloat(view, "scaleY", 1f)
                )
                duration = 10
            }
            press.addListener(object : AnimatorListenerAdapter() {
                override fun onAnimationEnd(a: Animator) { release.start() }
            })
            release.addListener(object : AnimatorListenerAdapter() {
                override fun onAnimationEnd(a: Animator) { view.isClickable = true }
            })
            press.start()
        }
    }

    // ─────────────────────────────────────────────────────────────────────────
    // TECLAS DE VOLUMEN
    // ─────────────────────────────────────────────────────────────────────────
    override fun onKeyDown(keyCode: Int, event: KeyEvent?): Boolean = when (keyCode) {
        KeyEvent.KEYCODE_VOLUME_UP   -> { queueCommand("VOLUME_UP"); true }
        KeyEvent.KEYCODE_VOLUME_DOWN -> { queueCommand("VOLUME_DOWN"); true }
        else -> super.onKeyDown(keyCode, event)
    }

    // ─────────────────────────────────────────────────────────────────────────
    // AUDIO Y VIBRACIÓN
    // ─────────────────────────────────────────────────────────────────────────
    private fun playShiftSound() {
        CoroutineScope(Dispatchers.IO).launch { soundPool.play(soundId, 1f, 1f, 1, 0, 1f) }
    }

    private fun vibrate(duration: Long) {
        CoroutineScope(Dispatchers.IO).launch {
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                vibrator.vibrate(VibrationEffect.createOneShot(duration, VibrationEffect.DEFAULT_AMPLITUDE))
            } else {
                @Suppress("DEPRECATION")
                vibrator.vibrate(duration)
            }
        }
    }

    // ─────────────────────────────────────────────────────────────────────────
    // RED: COLA DE COMANDOS Y CONEXIÓN TCP
    // ─────────────────────────────────────────────────────────────────────────
    private fun queueCommand(command: String) {
        if (isConnected()) commandQueue.offer(command)
    }

    private suspend fun processCommandQueue() {
        while (isConnected()) {
            val cmd = commandQueue.poll()
            if (cmd != null) {
                try {
                    outputStream?.writeBytes("$cmd\n")
                    outputStream?.flush()
                } catch (e: IOException) {
                    e.printStackTrace()
                }
            }
            delay(1)
        }
    }

    @Synchronized
    private fun establishConnection() {
        if (isConnected()) return
        CoroutineScope(Dispatchers.IO).launch {
            try {
                closeConnection()
                socket = Socket(serverAddress, serverPort).apply {
                    tcpNoDelay      = true
                    keepAlive       = true
                    soTimeout       = 5000
                    sendBufferSize    = 65536
                    receiveBufferSize = 65536
                }
                outputStream = DataOutputStream(socket?.getOutputStream())

                setConnectionState(true, serverAddress)
                runOnUiThread {
                    Toast.makeText(this@SteeringWheelActivity, "Connected to $serverAddress", Toast.LENGTH_SHORT).show()
                }

                // Iniciar receptor TCP: lee los mensajes T:speed:gear:rpm del servidor
                startTcpReceiver()

                processCommandQueue()
            } catch (e: IOException) {
                setConnectionState(false, null)
                handleConnectionError(e)
            }
        }
    }

    private fun handleConnectionError(e: IOException) {
        e.printStackTrace()
        runOnUiThread {
            Toast.makeText(this, "Connection Failed. Is the PC Server running?", Toast.LENGTH_LONG).show()
            showConnectionOptions()
        }
    }

    private fun closeConnection() {
        try {
            outputStream?.flush()
            socket?.shutdownOutput()
            outputStream?.close()
            socket?.shutdownInput()
            socket?.close()
        } catch (e: Exception) {
            e.printStackTrace()
        } finally {
            socket = null
            outputStream = null
        }
    }

    private fun isConnected() = socket?.isConnected == true && socket?.isClosed == false

    // ─────────────────────────────────────────────────────────────────────────
    // DESCUBRIMIENTO DE SERVIDOR
    // ─────────────────────────────────────────────────────────────────────────
    private fun discoverServerViaUDP() {
        CoroutineScope(Dispatchers.IO).launch {
            try {
                val udp = DatagramSocket()
                udp.broadcast = true
                val msg = "DISCOVER_SERVER".toByteArray()
                udp.send(DatagramPacket(msg, msg.size, InetAddress.getByName("255.255.255.255"), serverPort))
                val resp = DatagramPacket(ByteArray(1024), 1024)
                udp.soTimeout = 5000
                try {
                    udp.receive(resp)
                    serverAddress = String(resp.data, 0, resp.length).split(":")[0]
                    udp.close()
                    establishConnection()
                } catch (e: SocketTimeoutException) {
                    runOnUiThread {
                        Toast.makeText(this@SteeringWheelActivity, "PC Server not found.", Toast.LENGTH_SHORT).show()
                        showConnectionOptions()
                    }
                }
            } catch (e: IOException) {
                e.printStackTrace()
                runOnUiThread {
                    Toast.makeText(this@SteeringWheelActivity, "Network error. Is WiFi connected?", Toast.LENGTH_SHORT).show()
                    showConnectionOptions()
                }
            }
        }
    }

    private fun discoverServerViaUsbTethering() {
        CoroutineScope(Dispatchers.IO).launch {
            try {
                val usbIp = getUsbTetheringIp()
                if (usbIp != null) {
                    val broadcast = "${usbIp.substringBeforeLast(".")}.255"
                    val udp = DatagramSocket()
                    udp.broadcast = true
                    val msg = "DISCOVER_SERVER".toByteArray()
                    udp.send(DatagramPacket(msg, msg.size, InetAddress.getByName(broadcast), serverPort))
                    val resp = DatagramPacket(ByteArray(1024), 1024)
                    udp.soTimeout = 3000
                    try {
                        udp.receive(resp)
                        serverAddress = String(resp.data, 0, resp.length).split(":")[0]
                        udp.close()
                        establishConnection()
                    } catch (e: SocketTimeoutException) {
                        runOnUiThread {
                            Toast.makeText(this@SteeringWheelActivity, "PC Server not found via USB.", Toast.LENGTH_SHORT).show()
                            showConnectionOptions()
                        }
                    }
                } else {
                    withContext(Dispatchers.Main) {
                        Toast.makeText(this@SteeringWheelActivity, "USB Tethering unavailable.", Toast.LENGTH_SHORT).show()
                    }
                }
            } catch (e: IOException) {
                e.printStackTrace()
                runOnUiThread {
                    Toast.makeText(this@SteeringWheelActivity, "USB Network error.", Toast.LENGTH_SHORT).show()
                    showConnectionOptions()
                }
            }
        }
    }

    private fun getUsbTetheringIp(): String? = try {
        NetworkInterface.getNetworkInterfaces().toList()
            .firstOrNull { it.name.contains("rndis") || it.name.contains("usb") }
            ?.inetAddresses?.toList()
            ?.firstOrNull { !it.isLoopbackAddress && it is Inet4Address }
            ?.hostAddress
    } catch (e: Exception) { null }

    // ─────────────────────────────────────────────────────────────────────────
    // DIÁLOGOS DE CONEXIÓN
    // ─────────────────────────────────────────────────────────────────────────
    private fun showConnectionOptions() {
        if (isDialogShowing) return
        val options = arrayOf("WiFi (Auto-detect)", "USB Tethering (Auto-detect)", "Manual IP Address")
        MaterialAlertDialogBuilder(this, R.style.GeneonDialogTheme)
            .setTitle("Connect to PC Server")
            .setAdapter(ArrayAdapter(this, R.layout.dialog_list_item, options)) { _, which ->
                isDialogShowing = false
            when (which) {
                    0 -> { Toast.makeText(this, "Searching via WiFi…", Toast.LENGTH_SHORT).show(); discoverServerViaUDP() }
                    1 -> { Toast.makeText(this, "Searching via USB…", Toast.LENGTH_SHORT).show(); discoverServerViaUsbTethering() }
                    2 -> showManualIpInputDialog()
                }
            }
            .setOnDismissListener { isDialogShowing = false }
            .create()
            .also { it.show(); isDialogShowing = true }
    }

    private fun showManualIpInputDialog() {
        val input = EditText(this).apply {
            inputType = InputType.TYPE_CLASS_TEXT
            setTextColor(ContextCompat.getColor(this@SteeringWheelActivity, android.R.color.white))
        }
        MaterialAlertDialogBuilder(this, R.style.GeneonDialogTheme)
            .setTitle("Enter PC IP Address")
            .setMessage("Enter the IP address shown in the Python Server app:")
            .setView(input)
            .setPositiveButton("Connect") { _, _ ->
                val ip = input.text.toString()
                if (ip.isNotEmpty()) { serverAddress = ip; establishConnection() }
                else Toast.makeText(this, "Please enter a valid IP address", Toast.LENGTH_SHORT).show()
            }
            .setNegativeButton("Cancel") { d, _ -> d.cancel() }
            .show()
    }

    // ─────────────────────────────────────────────────────────────────────────
    // CICLO DE VIDA
    // ─────────────────────────────────────────────────────────────────────────
    override fun onResume() {
        super.onResume()
        val prefs = getSharedPreferences("steering_prefs", MODE_PRIVATE)
        maxSteeringAngle        = prefs.getInt("steering_angle", 90).toFloat()
        accelerationSensitivity = prefs.getFloat(SettingsActivity.PREF_ACCELERATOR_SENSITIVITY, SettingsActivity.DEFAULT_ACCELERATOR_SENSITIVITY)
        brakeSensitivity        = prefs.getFloat(SettingsActivity.PREF_BRAKE_SENSITIVITY, SettingsActivity.DEFAULT_BRAKE_SENSITIVITY)
        clickTimeLimit          = prefs.getFloat(SettingsActivity.PREF_CLICK_TIME_LIMIT, SettingsActivity.DEFAULT_CLICK_TIME_LIMIT)
        swipeThresholdInPx      = prefs.getFloat(SettingsActivity.PREF_SWIPE_THRESHOLD, SettingsActivity.DEFAULT_SWIPE_THRESHOLD) *
                                  resources.displayMetrics.xdpi / 25.4f
                                  
        // Telemetry visibility
        val telemetryEnabled = prefs.getBoolean(SettingsActivity.PREF_TELEMETRY_ENABLED, true)
        val visibility = if (telemetryEnabled) View.VISIBLE else View.GONE
        
        cockpitGlow.visibility = visibility
        cockpitArcOuter.visibility = visibility
        cockpitArcInner.visibility = visibility
        horizonLine.visibility = visibility
        centerGearBlock.visibility = visibility
        speedContainer.visibility = visibility
        ffbContainer.visibility = visibility
        rpmContainer.visibility = visibility
    }

    override fun onDestroy() {
        super.onDestroy()
        statusUpdateJob?.cancel()
        sensorManager.unregisterListener(this)
        soundPool.release()
        stopAcTelemetry()
        closeConnection()
    }
}
