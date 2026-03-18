import SwiftUI
import UIKit

// MARK: - MobilWheel Palette
let mwAccent    = Color(red: 1.0, green: 0.427, blue: 0.0)
private let mwDimGrey  = Color.white.opacity(0.08)
private let mwBorder   = Color.white.opacity(0.12)

/// The main steering wheel / racing HUD view
struct WheelView: View {
    @EnvironmentObject var connection: ConnectionManager
    @EnvironmentObject var settings: SettingsManager
    @Environment(\.dismiss) var dismiss
    @StateObject private var motion = MotionManager()
    @StateObject private var volumeHandler = VolumeButtonHandler()

    @State private var throttleValue: Int = 0
    @State private var brakeValue: Int = 0
    @State private var smoothedRotation: Double = 0.0
    @State private var showExitConfirm = false
    @State private var batteryLevel: Int = 0
    @State private var batteryTimer: Timer?
    @State private var flashL1 = false
    @State private var flashL2 = false
    @State private var flashR1 = false
    @State private var flashR2 = false

    @State private var lastGear: Int = 1
    @State private var displayedGear: Int = 1
    @State private var gearShiftDirection: Edge = .bottom
    @State private var gearDebounceWork: DispatchWorkItem?

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
                        latencyMs: connection.latencyMs,
                        onBackTap: { showExitConfirm = true }
                    )
                    Spacer()

                    // ── Bottom labels ──
                    HStack(spacing: 0) {
                        Text("BRAKE")
                            .font(.system(size: 11, weight: .bold, design: .monospaced))
                            .foregroundColor(.red.opacity(0.35))
                            .tracking(3)
                            .frame(maxWidth: .infinity, maxHeight: .infinity)
                            .overlay(
                                RoundedRectangle(cornerRadius: 10)
                                    .stroke(mwBorder, lineWidth: 1)
                            )
                            .padding(.leading, 8)
                            .padding(.trailing, 4)

                        Text("GAS")
                            .font(.system(size: 11, weight: .bold, design: .monospaced))
                            .foregroundColor(.green.opacity(0.35))
                            .tracking(3)
                            .frame(maxWidth: .infinity, maxHeight: .infinity)
                            .overlay(
                                RoundedRectangle(cornerRadius: 10)
                                    .stroke(mwBorder, lineWidth: 1)
                            )
                            .padding(.leading, 4)
                            .padding(.trailing, 8)
                    }
                    .frame(height: 32)
                    .padding(.bottom, 8)
                }

                // ── Main content: Left panel | Center gear | Right panel ──
                HStack(spacing: 0) {
                    // LEFT HALF: Brake side
                    ZStack {
                        // Button zones with labels
                        VStack(spacing: 0) {
                            // L1 / D
                            ZStack {
                                RoundedRectangle(cornerRadius: 12)
                                    .fill(flashL1 ? mwAccent.opacity(0.15) : Color.clear)
                                    .padding(8)
                                RoundedRectangle(cornerRadius: 12)
                                    .stroke(mwDimGrey, lineWidth: 1)
                                    .padding(8)
                                Text("L1 / D")
                                    .font(.system(size: 18, weight: .semibold, design: .monospaced))
                                    .foregroundColor(.white.opacity(0.25))
                                    .tracking(2)
                            }
                            .frame(maxHeight: .infinity)

                            // FFB indicator
                            HStack(spacing: 0) {
                                FFBIndicator(value: connection.telemetry.ffb)
                                    .frame(width: 30)
                                    .padding(.leading, 12)
                                Spacer()
                            }
                            .frame(height: 1)

                            // L2 / E
                            ZStack {
                                RoundedRectangle(cornerRadius: 12)
                                    .fill(flashL2 ? mwAccent.opacity(0.15) : Color.clear)
                                    .padding(8)
                                RoundedRectangle(cornerRadius: 12)
                                    .stroke(mwDimGrey, lineWidth: 1)
                                    .padding(8)
                                Text("L2 / E")
                                    .font(.system(size: 18, weight: .semibold, design: .monospaced))
                                    .foregroundColor(.white.opacity(0.25))
                                    .tracking(2)
                            }
                            .frame(maxHeight: .infinity)
                        }
                    }
                    .overlay(alignment: .bottom) {
                        Rectangle()
                            .fill(Color.red.opacity(0.15))
                            .frame(height: max(0, CGFloat(brakeValue) / 100.0 * (geo.size.height - 80)))
                            .animation(.easeOut(duration: 0.12), value: brakeValue)
                            .allowsHitTesting(false)
                    }
                    .clipShape(RoundedRectangle(cornerRadius: 16))
                    .overlay(
                        RoundedRectangle(cornerRadius: 16)
                            .stroke(mwBorder, lineWidth: 1)
                    )
                    .padding(.leading, 8)
                    .padding(.vertical, 40)
                    ZStack {
                        // Concentric rings
                        Circle()
                            .stroke(mwAccent.opacity(0.2), lineWidth: 1)
                            .frame(width: 220, height: 220)
                        Circle()
                            .stroke(mwAccent.opacity(0.35), lineWidth: 1.5)
                            .frame(width: 180, height: 180)

                        // Gear display — counter-rotates
                        VStack(spacing: 2) {
                            Text("GEAR")
                                .font(.system(size: 11, weight: .semibold, design: .monospaced))
                                .foregroundColor(mwAccent.opacity(0.8))
                                .tracking(4)

                            Text(displayedGearLabel)
                                .frame(width: 120, height: 110)
                                .font(.system(size: 90, weight: .bold, design: .rounded))
                                .foregroundColor(.white.opacity(0.92))
                                .shadow(color: mwAccent.opacity(0.08), radius: 20)
                                .contentTransition(.numericText(countsDown: gearShiftDirection == .top))
                                .animation(.interpolatingSpring(stiffness: 300, damping: 25), value: displayedGear)
                        }
                        .rotationEffect(.degrees(-smoothedRotation))
                    }
                    .frame(width: 240)

                    // RIGHT HALF: Throttle side
                    ZStack {
                        // Button zones with labels
                        VStack(spacing: 0) {
                            // R1 / F
                            ZStack {
                                RoundedRectangle(cornerRadius: 12)
                                    .fill(flashR1 ? mwAccent.opacity(0.15) : Color.clear)
                                    .padding(8)
                                RoundedRectangle(cornerRadius: 12)
                                    .stroke(mwDimGrey, lineWidth: 1)
                                    .padding(8)
                                Text("R1 / F")
                                    .font(.system(size: 18, weight: .semibold, design: .monospaced))
                                    .foregroundColor(.white.opacity(0.25))
                                    .tracking(2)
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
                                    .fill(flashR2 ? mwAccent.opacity(0.15) : Color.clear)
                                    .padding(8)
                                RoundedRectangle(cornerRadius: 12)
                                    .stroke(mwDimGrey, lineWidth: 1)
                                    .padding(8)
                                Text("R2 / G")
                                    .font(.system(size: 18, weight: .semibold, design: .monospaced))
                                    .foregroundColor(.white.opacity(0.25))
                                    .tracking(2)
                            }
                            .frame(maxHeight: .infinity)
                        }
                    }
                    .overlay(alignment: .bottom) {
                        Rectangle()
                            .fill(Color.green.opacity(0.2))
                            .frame(height: max(0, CGFloat(throttleValue) / 100.0 * (geo.size.height - 80)))
                            .animation(.easeOut(duration: 0.12), value: throttleValue)
                            .allowsHitTesting(false)
                    }
                    .clipShape(RoundedRectangle(cornerRadius: 16))
                    .overlay(
                        RoundedRectangle(cornerRadius: 16)
                            .stroke(mwBorder, lineWidth: 1)
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
                        onTopButton: { connection.send(.leftTop); flashButton($flashL1) },
                        onBottomButton: { connection.send(.leftBottom); flashButton($flashL2) }
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
                        onTopButton: { connection.send(.rightTop); flashButton($flashR1) },
                        onBottomButton: { connection.send(.rightBottom); flashButton($flashR2) }
                    )
                }
                .padding(.top, 32)
                .ignoresSafeArea(edges: [.bottom, .leading, .trailing])
            }
        }
        .onAppear {
            UIApplication.shared.isIdleTimerDisabled = true
            updateBattery()
            batteryTimer = Timer.scheduledTimer(withTimeInterval: 30, repeats: true) { _ in
                updateBattery()
            }
            volumeHandler.onVolumeUp = { connection.send(.volumeUp) }
            volumeHandler.onVolumeDown = { connection.send(.volumeDown) }
            volumeHandler.start()
            motion.start(maxAngle: settings.steeringAngle) { angle in
                connection.send(.steering(angle))
                let displayAngle = (angle / 10.0) * settings.steeringAngle
                smoothedRotation = 0.18 * displayAngle + 0.82 * smoothedRotation
            }
        }
        .onDisappear {
            UIApplication.shared.isIdleTimerDisabled = false
            batteryTimer?.invalidate()
            batteryTimer = nil
            gearDebounceWork?.cancel()
            gearDebounceWork = nil
            motion.stop()
            volumeHandler.stop()
        }
        .onChange(of: settings.steeringAngle) { newValue in
            motion.updateMaxAngle(newValue)
        }
        .onChange(of: connection.telemetry.gear) { newGear in
            gearDebounceWork?.cancel()
            // Neutral (1) between shifts — skip it unless staying in N
            if newGear == 1 && lastGear != 0 && lastGear != 1 {
                let capturedDisplayed = displayedGear
                let work = DispatchWorkItem { [self] in
                    gearShiftDirection = newGear > capturedDisplayed ? .bottom : .top
                    lastGear = newGear
                    displayedGear = newGear
                }
                gearDebounceWork = work
                lastGear = newGear
                DispatchQueue.main.asyncAfter(deadline: .now() + 0.05, execute: work)
            } else {
                gearShiftDirection = newGear > displayedGear ? .bottom : .top
                lastGear = newGear
                displayedGear = newGear
            }
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
        .toolbar(.hidden, for: .navigationBar)
    }

    private var displayedGearLabel: String {
        switch displayedGear {
        case 0: return "R"
        case 1: return "N"
        default: return "\(displayedGear - 1)"
        }
    }

    private func updateBattery() {
        UIDevice.current.isBatteryMonitoringEnabled = true
        batteryLevel = Int(UIDevice.current.batteryLevel * 100)
        if batteryLevel < 0 { batteryLevel = 100 }
    }

    private func flashButton(_ flag: Binding<Bool>) {
        withAnimation(.easeIn(duration: 0.05)) { flag.wrappedValue = true }
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.15) {
            withAnimation(.easeOut(duration: 0.2)) { flag.wrappedValue = false }
        }
    }
}

// MARK: - Top Status Bar

struct TopStatusBar: View {
    let isConnected: Bool
    let serverAddress: String
    let rpm: Int
    let batteryLevel: Int
    let latencyMs: Int
    let onBackTap: () -> Void

    var body: some View {
        ZStack {
            // Left: connection status
            HStack {
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
                    .foregroundColor(.white.opacity(0.3))

                Spacer()
            }

            // Center: RPM
            VStack(spacing: 2) {
                Text("\(rpm)  RPM")
                    .font(.system(size: 10, weight: .bold, design: .monospaced))
                    .foregroundColor(mwAccent.opacity(0.9))
                RPMShiftLights(rpm: rpm)
            }

            // Right: ping, battery, time
            HStack {
                Spacer()

                HStack(spacing: 12) {
                    Text("PING: \(latencyMs)ms")
                        .font(.system(size: 9, weight: .medium, design: .monospaced))
                        .foregroundColor(latencyMs < 20 ? .green.opacity(0.5) : latencyMs < 50 ? mwAccent.opacity(0.5) : .red.opacity(0.5))

                    Text("BAT: \(batteryLevel)%")
                        .font(.system(size: 9, weight: .medium, design: .monospaced))
                        .foregroundColor(.white.opacity(0.3))

                    Text(timeString())
                        .font(.system(size: 9, weight: .medium, design: .monospaced))
                        .foregroundColor(.white.opacity(0.3))
                }
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
                        .fill(value > threshold ? mwAccent : Color.gray.opacity(0.15))
                        .frame(height: 6)
                }
            }
            Text("FFB")
                .font(.system(size: 7, weight: .bold, design: .monospaced))
                .foregroundColor(.white.opacity(0.2))
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
        view.isMultipleTouchEnabled = false
        view.isExclusiveTouch = true
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

    // Track the specific touch driving the drag to avoid multi-touch confusion
    private weak var activeTouch: UITouch?
    private var touchStartY: CGFloat = 0
    private var touchStartTime: TimeInterval = 0
    private var isDragging = false

    private var swipeThresholdPts: CGFloat {
        CGFloat(swipeThresholdMM) * 6.4
    }

    override func touchesBegan(_ touches: Set<UITouch>, with event: UIEvent?) {
        // If we already have an active drag, ignore new touches
        if activeTouch != nil { return }
        guard let touch = touches.first else { return }
        activeTouch = touch
        touchStartY = touch.location(in: self).y
        touchStartTime = touch.timestamp
        isDragging = false
    }

    override func touchesMoved(_ touches: Set<UITouch>, with event: UIEvent?) {
        guard let tracked = activeTouch, touches.contains(tracked) else { return }
        let currentY = tracked.location(in: self).y
        let deltaY = currentY - touchStartY

        if abs(deltaY) > swipeThresholdPts {
            isDragging = true
            // Map drag distance proportionally to the full zone height
            // so you need to drag the entire zone to reach 100%.
            let fraction = (abs(deltaY) - swipeThresholdPts) / (bounds.height - swipeThresholdPts) * 4.0
            let progress = Int((fraction * 100).clamped(to: 0...100))
            onDrag?(progress)
        }
    }

    override func touchesEnded(_ touches: Set<UITouch>, with event: UIEvent?) {
        guard let tracked = activeTouch, touches.contains(tracked) else { return }

        if isDragging {
            // Always release the drag value
            onDragEnd?()
        } else {
            // Only treat as tap if it was short and didn't move far
            let currentY = tracked.location(in: self).y
            let deltaY = abs(currentY - touchStartY)
            let elapsed = tracked.timestamp - touchStartTime

            if deltaY <= swipeThresholdPts && elapsed <= clickTimeLimit {
                let isTop = currentY < bounds.height / 2
                if isTop {
                    onTopButton?()
                } else {
                    onBottomButton?()
                }
                let generator = UIImpactFeedbackGenerator(style: .medium)
                generator.impactOccurred()
            }
        }
        resetTouch()
    }

    override func touchesCancelled(_ touches: Set<UITouch>, with event: UIEvent?) {
        // Always release on cancel — system interrupted the touch
        if isDragging { onDragEnd?() }
        resetTouch()
    }

    private func resetTouch() {
        activeTouch = nil
        isDragging = false
    }
}

extension CGFloat {
    func clamped(to range: ClosedRange<CGFloat>) -> CGFloat {
        return Swift.min(Swift.max(self, range.lowerBound), range.upperBound)
    }
}

// MARK: - Previews

#Preview("Wheel – Connected") {
    let conn = ConnectionManager()
    conn.isConnected = true
    conn.serverAddress = "192.168.1.100"
    conn.telemetry = TelemetryData(speed: 187, gear: 5, rpm: 5400)

    return WheelView()
        .environmentObject(conn)
        .environmentObject(SettingsManager())
}

#Preview("Wheel – Disconnected") {
    let conn = ConnectionManager()
    conn.isConnected = false
    conn.serverAddress = ""
    conn.telemetry = TelemetryData(speed: 0, gear: 1, rpm: 0)

    return WheelView()
        .environmentObject(conn)
        .environmentObject(SettingsManager())
}
