import SwiftUI

/// The main steering wheel / racing HUD view
struct WheelView: View {
    @EnvironmentObject var connection: ConnectionManager
    @EnvironmentObject var settings: SettingsManager
    @StateObject private var motion = MotionManager()

    @State private var throttleValue: Int = 0
    @State private var brakeValue: Int = 0
    @State private var smoothedRotation: Double = 0.0

    var body: some View {
        GeometryReader { geo in
            ZStack {
                Color.black.ignoresSafeArea()

                // Status bar at top
                VStack(spacing: 0) {
                    StatusBarView(
                        isConnected: connection.isConnected,
                        serverAddress: connection.serverAddress,
                        rpm: connection.telemetry.rpm
                    )

                    Spacer()
                }

                // Brake bar (left side)
                HStack {
                    PedalBar(value: brakeValue, color: .red, label: "BRAKE")
                        .frame(width: 40)
                        .padding(.leading, 8)
                    Spacer()
                }

                // Throttle bar (right side)
                HStack {
                    Spacer()
                    PedalBar(value: throttleValue, color: .green, label: "GAS")
                        .frame(width: 40)
                        .padding(.trailing, 8)
                }

                // Center gear/speed HUD — counter-rotates to stay upright
                GearHUDView(telemetry: connection.telemetry)
                    .rotationEffect(.degrees(-smoothedRotation))

                // Touch zones for throttle/brake/buttons
                HStack(spacing: 0) {
                    // Left side: brake + buttons
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

                    // Right side: throttle + buttons
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
            motion.start(maxAngle: settings.steeringAngle) { angle in
                connection.send(.steering(angle))
                // Exponential smoothing for HUD counter-rotation
                let displayAngle = (angle / 10.0) * settings.steeringAngle
                smoothedRotation = 0.18 * displayAngle + 0.82 * smoothedRotation
            }
        }
        .onDisappear {
            UIApplication.shared.isIdleTimerDisabled = false
            motion.stop()
        }
        .onChange(of: settings.steeringAngle) { newValue in
            motion.updateMaxAngle(newValue)
        }
        .statusBarHidden(true)
    }
}

// MARK: - Status Bar

struct StatusBarView: View {
    let isConnected: Bool
    let serverAddress: String
    let rpm: Int

    var body: some View {
        HStack(spacing: 12) {
            // Connection indicator
            Circle()
                .fill(isConnected ? Color.green : Color.red)
                .frame(width: 10, height: 10)
            Text(isConnected ? serverAddress : "DISCONNECTED")
                .font(.system(size: 11, weight: .medium, design: .monospaced))
                .foregroundColor(.white.opacity(0.7))

            Spacer()

            // RPM shift lights
            RPMShiftLights(rpm: rpm)

            Text("\(rpm) RPM")
                .font(.system(size: 11, weight: .medium, design: .monospaced))
                .foregroundColor(.white.opacity(0.7))
        }
        .padding(.horizontal, 16)
        .padding(.vertical, 8)
        .background(Color.black.opacity(0.8))
    }
}

// MARK: - RPM Shift Lights

struct RPMShiftLights: View {
    let rpm: Int
    private let dotCount = 15
    // Thresholds for 15 dots: green(1-5), yellow(6-10), red(11-15)
    private let thresholds: [Double] = [
        0.30, 0.38, 0.46, 0.54, 0.62,  // Green
        0.64, 0.68, 0.72, 0.76, 0.82,  // Yellow
        0.85, 0.88, 0.91, 0.94, 0.97   // Red
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

// MARK: - Gear HUD (center)

struct GearHUDView: View {
    let telemetry: TelemetryData

    var body: some View {
        VStack(spacing: 4) {
            Text(telemetry.gearLabel)
                .font(.system(size: 80, weight: .bold, design: .monospaced))
                .foregroundColor(.white)

            Text("\(telemetry.speed)")
                .font(.system(size: 36, weight: .medium, design: .monospaced))
                .foregroundColor(.white.opacity(0.8))

            Text("km/h")
                .font(.system(size: 12, weight: .regular, design: .monospaced))
                .foregroundColor(.white.opacity(0.4))
        }
    }
}

// MARK: - Pedal Bar

struct PedalBar: View {
    let value: Int  // 0-100
    let color: Color
    let label: String

    var body: some View {
        GeometryReader { geo in
            ZStack(alignment: .bottom) {
                RoundedRectangle(cornerRadius: 4)
                    .fill(Color.white.opacity(0.1))
                RoundedRectangle(cornerRadius: 4)
                    .fill(color.opacity(0.7))
                    .frame(height: geo.size.height * CGFloat(value) / 100.0)

                Text(label)
                    .font(.system(size: 9, weight: .bold, design: .monospaced))
                    .foregroundColor(.white.opacity(0.5))
                    .rotationEffect(.degrees(-90))
                    .padding(.bottom, 30)
            }
        }
        .padding(.vertical, 60)
    }
}

// MARK: - Touch Zone (handles drag for pedals + tap for buttons)

enum TouchSide {
    case left, right
}

struct TouchZone: UIViewRepresentable {
    let side: TouchSide
    let sensitivity: Double
    let swipeThreshold: Double  // in mm
    let clickTimeLimit: Double  // in seconds
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

    // Convert mm to points (~163 PPI on modern iPhones → 1mm ≈ 6.4 pts)
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
            // Button tap
            let tapY = touch.location(in: self).y
            let isTop = tapY < bounds.height / 2
            if isTop {
                onTopButton?()
            } else {
                onBottomButton?()
            }
            // Haptic feedback
            let generator = UIImpactFeedbackGenerator(style: .medium)
            generator.impactOccurred()
        } else if isDragging {
            onDragEnd?()
        }

        isDragging = false
    }

    override func touchesCancelled(_ touches: Set<UITouch>, with event: UIEvent?) {
        if isDragging {
            onDragEnd?()
        }
        isDragging = false
    }
}

// MARK: - CGFloat clamping helper

extension CGFloat {
    func clamped(to range: ClosedRange<CGFloat>) -> CGFloat {
        return Swift.min(Swift.max(self, range.lowerBound), range.upperBound)
    }
}
