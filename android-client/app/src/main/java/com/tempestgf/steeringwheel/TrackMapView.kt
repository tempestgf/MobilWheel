package com.tempestgf.steeringwheel

import android.content.Context
import android.graphics.Canvas
import android.graphics.Color
import android.graphics.Paint
import android.graphics.Path
import android.util.AttributeSet
import android.view.View

class TrackMapView @JvmOverloads constructor(
    context: Context, attrs: AttributeSet? = null, defStyleAttr: Int = 0
) : View(context, attrs, defStyleAttr) {

    private val trackPoints = mutableListOf<Pair<Float, Float>>()
    private var carX = 0f
    private var carZ = 0f

    private val trackPaint = Paint().apply {
        color = Color.parseColor("#44FFFFFF")
        strokeWidth = 12f
        style = Paint.Style.STROKE
        strokeCap = Paint.Cap.ROUND
        strokeJoin = Paint.Join.ROUND
        isAntiAlias = true
    }

    private val carPaint = Paint().apply {
        color = Color.parseColor("#FF0000") // Red dot for the car
        style = Paint.Style.FILL
        isAntiAlias = true
    }

    private var minX = Float.MAX_VALUE
    private var maxX = Float.MIN_VALUE
    private var minZ = Float.MAX_VALUE
    private var maxZ = Float.MIN_VALUE

    fun updatePosition(x: Float, z: Float) {
        if(x == 0f && z == 0f) return

        carX = x
        carZ = z

        if (trackPoints.isEmpty()) {
            addPoint(x, z)
        } else {
            val last = trackPoints.last()
            val distSq = (x - last.first)*(x - last.first) + (z - last.second)*(z - last.second)
            if (distSq > 100f) { 
                addPoint(x, z)
            }
        }
        invalidate()
    }

    private fun addPoint(x: Float, z: Float) {
        trackPoints.add(Pair(x, z))
        if(trackPoints.size > 2000) trackPoints.removeAt(0)
        if (x < minX) minX = x
        if (x > maxX) maxX = x
        if (z < minZ) minZ = z
        if (z > maxZ) maxZ = z
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)

        if (trackPoints.isEmpty()) { 
            drawMockTrack(canvas, width.toFloat(), height.toFloat(), 20f)
            return 
        }

        val width = width.toFloat()
        val height = height.toFloat()
        val padding = 20f

        val pathW = (maxX - minX).coerceAtLeast(1f)
        val pathH = (maxZ - minZ).coerceAtLeast(1f)

        val scaleX = (width - 2 * padding) / pathW
        val scaleY = (height - 2 * padding) / pathH
        val scale = scaleX.coerceAtMost(scaleY)

        val offsetX = (width - pathW * scale) / 2f
        val offsetZ = (height - pathH * scale) / 2f

        val path = Path()
        trackPoints.forEachIndexed { index, point ->
            val mappedX = offsetX + (point.first - minX) * scale
            val mappedY = offsetZ + (maxZ - point.second) * scale 
            if (index == 0) path.moveTo(mappedX, mappedY)
            else path.lineTo(mappedX, mappedY)
        }

        canvas.drawPath(path, trackPaint)

        val mappedCarX = offsetX + (carX - minX) * scale
        val mappedCarZ = offsetZ + (maxZ - carZ) * scale
        canvas.drawCircle(mappedCarX, mappedCarZ, 12f, carPaint)
    }

    private fun drawMockTrack(canvas: Canvas, w: Float, h: Float, pad: Float) {
        val path = Path()
        val wInner = w - pad * 2
        val hInner = h - pad * 2
        val ox = pad
        val oy = pad

        path.moveTo(ox + wInner * 0.1f, oy + hInner * 0.8f) 
        path.quadTo(ox, oy + hInner * 0.9f, ox + wInner * 0.2f, oy + hInner * 0.9f)
        path.lineTo(ox + wInner * 0.8f, oy + hInner * 0.8f)
        path.quadTo(ox + wInner, oy + hInner * 0.7f, ox + wInner * 0.9f, oy + hInner * 0.5f)
        path.lineTo(ox + wInner * 0.6f, oy + hInner * 0.2f)
        path.quadTo(ox + wInner * 0.5f, oy + hInner * 0.1f, ox + wInner * 0.4f, oy + hInner * 0.2f)
        path.lineTo(ox + wInner * 0.2f, oy + hInner * 0.6f)
        path.quadTo(ox + wInner * 0.1f, oy + hInner * 0.7f, ox + wInner * 0.1f, oy + hInner * 0.8f)
        path.close()

        val mockPaint = Paint().apply {
            color = Color.parseColor("#607aa2f7")
            strokeWidth = 10f
            style = Paint.Style.STROKE
            strokeCap = Paint.Cap.ROUND
            strokeJoin = Paint.Join.ROUND
            isAntiAlias = true
        }

        canvas.drawPath(path, mockPaint)
        canvas.drawCircle(ox + wInner * 0.6f, oy + hInner * 0.2f, 15f, carPaint)
    }
}
