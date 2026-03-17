import SwiftUI
import UIKit

/// The main steering wheel / racing HUD view — matches Android layout
struct WheelView: View {
    @EnvironmentObject var connection: ConnectionManager
    @EnvironmentObject var settings: SettingsManager
    @Environment(\.dismiss) var dismiss
    @StateObject private var motion = MotionManager()

    @State private var throttleValue: Int = 0
    @State private var brakeValue: Int = 0
    @State private var smoothedRotation: Double = 0.0
    @State private var showExitConfirm = false
    @State private var batteryLevel: Int = 0
    @State private var batteryTimer: Timer?

    var body: some View {
        GeometryReader { geo in
            ZStack {
                Color.black.ignoresSafeArea()

                // ── Top status bar ──
                VStack(spacing: 0) {
                    TopStatusBar(
                        isConnected: connection.isConnected,
                        serverAddress: connection.serverAddress,
                        rpm: connection.telemetry.rpm,
                        batteryLevel: batteryLevel,
                        onBackTap: { showExitConfirm = true }
                    )
                    Spacer()

                    // ── Bottom labels ──
                    HStack {
                        Text("BRAKE")
                            .font(.system(size: 13, weight: .bold, design: .monospaced))
                            .foregroundColor(.red.opacity(0.5))
                            .frame(maxWidth: .infinity)
                        Text("GAS")
                            .font(.system(size: 13, weight: .bold, design: .monospaced))
                            .foregroundColor(.green.opacity(0.5))
                            .frame(maxWidth: .infinity)
                    }
                    .padding(.bottom, 8)
                }

                // ── Main content: Left panel | Center gear | Right panel ──
                HStack(spacing: 0) {
                    // LEFT HALF: Brake side
                    ZStack {
                        // Brake fill overlay
                        VStack {
                            Spacer()
                            Rectangle()
                                .fill(Color.red.opacity(0.15))
                                .frame(height: geo.size.height * CGFloat(brakeValue) / 100.0)
                        }
                        .clipShape(RoundedRectangle(cornerRadius: 16))

                        // Button zones with labels
                        VStack(spacing: 0) {
                            // L1 / D
                            ZStack {
                                RoundedRectangle(cornerRadius: 12)
                                    .stroke(Color.white.opacity(0.15), lineWidth: 1)
                                    .padding(8)
                                Text("L1 / D")
                                    .font(.system(size: 18, weight: .semibold, design: .monospaced))
                                    .foregroundColor(.white.opacity(0.4))
                            }
                            .frame(maxHeight: .infinity)

                            // FFB indicator
                            HStack(spacing: 0) {
                                FFBIndicator(value: brakeValue)
                                    .frame(width: 30)
                                    .padding(.leading, 12)
                                Spacer()
                            }
                            .frame(height: 1)

                            // L2 / E
                            ZStack {
                                RoundedRectangle(cornerRadius: 12)
                                    .stroke(Color.white.opacity(0.15), lineWidth: 1)
                                    .padding(8)
                                Text("L2 / E")
                                    .font(.system(size: 18, weight: .semibold, design: .monospaced))
                                    .foregroundColor(.white.opacity(0.4))
                            }
                            .frame(maxHeight: .infinity)
                        }
                    }
                    .background(
                        RoundedRectangle(cornerRadius: 16)
                            .stroke(Color.red.opacity(0.2), lineWidth: 1)
                    )
                    .padding(.leading, 8)
                    .padding(.vertical, 40)

                    // CENTER: Gear + Speed HUD
                    ZStack {
                        // Concentric rings
                        Circle()
                            .stroke(Color.orange.opacity(0.15), lineWidth: 1)
                            .frame(width: 220, height: 220)
                        Circle()
                            .stroke(Color.orange.opacity(0.25), lineWidth: 1)
                            .frame(width: 180, height: 180)

                        // Gear display — counter-rotates
                        VStack(spacing: 2) {
                            Text("GEAR")
                                .font(.system(size: 12, weight: .medium, design: .monospaced))
                                .foregroundColor(.green.opacity(0.7))

                            Text(connection.telemetry.gearLabel)
                                .font(.system(size: 90, weight: .bold, design: .rounded))
                                .foregroundColor(.white.opacity(0.9))
                                .shadow(color: .white.opacity(0.1), radius: 10)
                        }
                        .rotationEffect(.degrees(-smoothedRotation))
                    }
                    .frame(width: 240)

                    // RIGHT HALF: Throttle side
                    ZStack {
                        // Throttle fill overlay
                        VStack {
                            Spacer()
                            Rectangle()
                                .fill(Color.green.opacity(0.2))
                                .frame(height: geo.size.height * CGFloat(throttleValue) / 100.0)
                        }
                        .clipShape(RoundedRectangle(cornerRadius: 16))

                        // Button zones with labels
                        VStack(spacing: 0) {
                            // R1 / F
                            ZStack {
                                RoundedRectangle(cornerRadius: 12)
                                    .stroke(Color.white.opacity(0.15), lineWidth: 1)
                                    .padding(8)
                                Text("R1 / F")
                                    .font(.system(size: 18, weight: .semibold, design: .monospaced))
                                    .foregroundColor(.white.opacity(0.4))
                            }
                            .frame(maxHeight: .infinity)

                            // Speed display (right side, like Android)
                            HStack {
                                Spacer()
                                VStack(spacing: 0) {
                                    Text("\(connection.telemetry.speed)")
                                        .font(.system(size: 48, weight: .bold, design: .monospaced))
                                        .foregroundColor(.white.opacity(0.85))
                                    Text("KM/H")
                                        .font(.system(size: 11, weight: .medium, design: .monospaced))
                                        .foregroundColor(.white.opacity(0.4))
                                }
                                .padding(.trailing, 20)
                            }
                            .frame(height: 1)

                            // R2 / G
                            ZStack {
                                RoundedRectangle(cornerRadius: 12)
                                    .stroke(Color.white.opacity(0.15), lineWidth: 1)
                                    .padding(8)
                                Text("R2 / G")
                                    .font(.system(size: 18, weight: .semibold, design: .monospaced))
                                    .foregroundColor(.white.opacity(0.4))
                            }
                            .frame(maxHeight: .infinity)
                        }
                    }
                    .background(
                        RoundedRectangle(cornerRadius: 16)
                            .stroke(Color.green.opacity(0.2), lineWidth: 1)
                    )
                    .padding(.trailing, 8)
                    .padding(.vertical, 40)
                }

                // ── Touch zones overlay (invisible, handles all input) ──
                HStack(spacing: 0) {
                    TouchZone(
                        side: .left,
                        sensitivity: settings.brakeSensitivity,
                        swipeThreshold: settings.swipeThreshold,
                        clickTimeLimit: settings.clickTimeLimit,
                        onDrag: { value in
                            brakeValue = value
                            connection.send(.brake(value))
                        },
                        onDragEnd: {
                            brakeValue = 0
                            connection.send(.brake(0))
                        },
                        onTopButton: { connection.send(.leftTop) },
                        onBottomButton: { connection.send(.leftBottom) }
                    )

                    TouchZone(
                        side: .right,
                        sensitivity: settings.acceleratorSensitivity,
                        swipeThreshold: settings.swipeThreshold,
                        clickTimeLimit: settings.clickTimeLimit,
                        onDrag: { value in
                            throttleValue = value
                            connection.send(.throttle(value))
                        },
                        onDragEnd: {
                            throttleValue = 0
                            connection.send(.throttle(0))
                        },
                        onTopButton: { connection.send(.rightTop) },
                        onBottomButton: { connection.send(.rightBottom) }
                    )
                }
                .ignoresSafeArea()
            }
        }
        .onAppear {
            UIApplication.shared.isIdleTimerDisabled = true
            updateBattery()
            batteryTimer = Timer.scheduledTimer(withTimeInterval: 30, repeats: true) { _ in
                updateBattery()
            }
            motion.start(maxAngle: settings.steeringAngle) { angle in
                connection.send(.steering(angle))
                let displayAngle = (angle / 10.0) * settings.steeringAngle
                smoothedRotation = 0.18 * displayAngle + 0.82 * smoothedRotation
            }
        }
        .onDisappear {
            UIApplication.shared.isIdleTimerDisabled = false
            batteryTimer?.invalidate()
            motion.stop()
        }
        .onChange(of: settings.steeringAngle) { newValue in
            motion.updateMaxAngle(newValue)
        }
        .alert("Exit?", isPresented: $showExitConfirm) {
            Button("Disconnect & Exit") {
                connection.disconnect()
                dismiss()
            }
            Button("Cancel", role: .cancel) {}
        } message: {
            Text("Disconnect from server and return to menu?")
        }
        .statusBarHidden(true)
        .navigationBarHidden(true)
    }

    private func updateBattery() {
        UIDevice.current.isBatteryMonitoringEnabled = true
        batteryLevel = Int(UIDevice.current.batteryLevel * 100)
        if batteryLevel < 0 { batteryLevel = 100 }
    }
}

// MARK: - Top Status Bar

struct TopStatusBar: View {
    let isConnected: Bool
    let serverAddress: String
    let rpm: Int
    let batteryLevel: Int
    let onBackTap: () -> Void

    var body: some View {
        HStack(spacing: 10) {
            Button(action: onBackTap) {
                HStack(spacing: 6) {
                    Circle()
                        .fill(isConnected ? Color.green : Color.red)
                        .frame(width: 10, height: 10)
                    Text(isConnected ? "CONNECTED" : "DISCONNECTED")
                        .font(.system(size: 10, weight: .bold, design: .monospaced))
                        .foregroundColor(isConnected ? .green : .red)
                }
            }

            Text(serverAddress)
                .font(.system(size: 10, weight: .medium, design: .monospaced))
                .foregroundColor(.white.opacity(0.5))

            Spacer()

            VStack(spacing: 2) {
                Text("\(rpm)  RPM")
                    .font(.system(size: 10, weight: .bold, design: .monospaced))
                    .foregroundColor(.green.opacity(0.8))
                RPMShiftLights(rpm: rpm)
            }

            Spacer()

            HStack(spacing: 12) {
                Text("PING: <5ms")
                    .font(.system(size: 9, weight: .medium, design: .monospaced))
                    .foregroundColor(.white.opacity(0.4))

                Text("BAT: \(batteryLevel)%")
                    .font(.system(size: 9, weight: .medium, design: .monospaced))
                    .foregroundColor(.white.opacity(0.4))

                Text(timeString())
                    .font(.system(size: 9, weight: .medium, design: .monospaced))
                    .foregroundColor(.white.opacity(0.4))
            }
        }
        .padding(.horizontal, 16)
        .padding(.vertical, 6)
        .background(Color.black.opacity(0.9))
    }

    private func timeString() -> String {
        let f = DateFormatter()
        f.dateFormat = "HH:mm"
        return f.string(from: Date())
    }
}

// MARK: - RPM Shift Lights

struct RPMShiftLights: View {
    let rpm: Int
    private let dotCount = 15
    private let thresholds: [Double] = [
        0.30, 0.38, 0.46, 0.54, 0.62,
        0.64, 0.68, 0.72, 0.76, 0.82,
        0.85, 0.88, 0.91, 0.94, 0.97
    ]

    var body: some View {
        HStack(spacing: 3) {
            ForEach(0..<dotCount, id: \.self) { i in
                Circle()
                    .fill(colorForDot(i))
                    .frame(width: 8, height: 8)
                    .opacity(isLit(i) ? 1.0 : 0.15)
            }
        }
    }

    private func colorForDot(_ index: Int) -> Color {
        if index < 5 { return .green }
        if index < 10 { return .yellow }
        return .red
    }

    private func isLit(_ index: Int) -> Bool {
        let fraction = min(Double(rpm) / 8000.0, 1.0)
        return fraction >= thresholds[index]
    }
}

// MARK: - FFB Indicator

struct FFBIndicator: View {
    let value: Int

    var body: some View {
        VStack(spacing: 0) {
            VStack(spacing: 2) {
                ForEach(0..<8, id: \.self) { i in
                    let barIndex = 7 - i
                    let threshold = barIndex * 12
                    RoundedRectangle(cornerRadius: 1)
                        .fill(value > threshold ? Color.orange : Color.gray.opacity(0.3))
                        .frame(height: 6)
                }
            }
            Text("FFB")
                .font(.system(size: 7, weight: .bold, design: .monospaced))
                .foregroundColor(.white.opacity(0.3))
                .padding(.top, 2)
        }
    }
}

// MARK: - Touch Zone

enum TouchSide {
    case left, right
}

struct TouchZone: UIViewRepresentable {
    let side: TouchSide
    let sensitivity: Double
    let swipeThreshold: Double
    let clickTimeLimit: Double
    let onDrag: (Int) -> Void
    let onDragEnd: () -> Void
    let onTopButton: () -> Void
    let onBottomButton: () -> Void

    func makeUIView(context: Context) -> TouchZoneUIView {
        let view = TouchZoneUIView()
        view.side = side
        view.sensitivity = sensitivity
        view.swipeThresholdMM = swipeThreshold
        view.clickTimeLimit = clickTimeLimit
        view.onDrag = onDrag
        view.onDragEnd = onDragEnd
        view.onTopButton = onTopButton
        view.onBottomButton = onBottomButton
        view.isMultipleTouchEnabled = true
        view.backgroundColor = .clear
        return view
    }

    func updateUIView(_ uiView: TouchZoneUIView, context: Context) {
        uiView.sensitivity = sensitivity
        uiView.swipeThresholdMM = swipeThreshold
        uiView.clickTimeLimit = clickTimeLimit
    }
}

class TouchZoneUIView: UIView {
    var side: TouchSide = .left
    var sensitivity: Double = 4.0
    var swipeThresholdMM: Double = 4.0
    var clickTimeLimit: Double = 0.25
    var onDrag: ((Int) -> Void)?
    var onDragEnd: (() -> Void)?
    var onTopButton: (() -> Void)?
    var onBottomButton: (() -> Void)?

    private var touchStartY: CGFloat = 0
    private var touchStartTime: TimeInterval = 0
    private var isDragging = false

    private var swipeThresholdPts: CGFloat {
        CGFloat(swipeThresholdMM) * 6.4
    }

    override func touchesBegan(_ touches: Set<UITouch>, with event: UIEvent?) {
        guard let touch = touches.first else { return }
        touchStartY = touch.location(in: self).y
        touchStartTime = touch.timestamp
        isDragging = false
    }

    override func touchesMoved(_ touches: Set<UITouch>, with event: UIEvent?) {
        guard let touch = touches.first else { return }
        let currentY = touch.location(in: self).y
        let deltaY = currentY - touchStartY

        if abs(deltaY) > swipeThresholdPts {
            isDragging = true
            let progress = Int((abs(deltaY) * CGFloat(sensitivity)).clamped(to: 0...100))
            onDrag?(progress)
        }
    }

    override func touchesEnded(_ touches: Set<UITouch>, with event: UIEvent?) {
        guard let touch = touches.first else { return }
        let currentY = touch.location(in: self).y
        let deltaY = abs(currentY - touchStartY)
        let elapsed = touch.timestamp - touchStartTime

        if deltaY <= swipeThresholdPts && elapsed <= clickTimeLimit {
            let tapY = touch.location(in: self).y
            let isTop = tapY < bounds.height / 2
            if isTop {
                onTopButton?()
            } else {
                onBottomButton?()
            }
            let generator = UIImpactFeedbackGenerator(style: .medium)
            generator.impactOccurred()
        } else if isDragging {
            onDragEnd?()
        }
        isDragging = false
    }

    override func touchesCancelled(_ touches: Set<UITouch>, with event: UIEvent?) {
        if isDragging { onDragEnd?() }
        isDragging = false
    }
}

extension CGFloat {
    func clamped(to range: ClosedRange<CGFloat>) -> CGFloat {
        return Swift.min(Swift.max(self, range.lowerBound), range.upperBound)
    }
}
