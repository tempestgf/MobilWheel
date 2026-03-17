import Foundation
import CoreMotion
import Combine

/// Reads device accelerometer and converts tilt to steering angle
final class MotionManager: ObservableObject {
    @Published var currentAngle: Double = 0.0  // -10.0 to +10.0
    @Published var rawPitch: Double = 0.0

    private let motionManager = CMMotionManager()
    private var lastSentAngle: Double = 0.0
    private let sendThreshold: Double = 0.010
    private var maxSteeringAngle: Double = 90.0

    /// Start reading accelerometer data
    func start(maxAngle: Double, onUpdate: @escaping (Double) -> Void) {
        self.maxSteeringAngle = maxAngle
        guard motionManager.isAccelerometerAvailable else { return }

        motionManager.accelerometerUpdateInterval = 1.0 / 60.0  // 60 Hz
        motionManager.startAccelerometerUpdates(to: .main) { [weak self] data, _ in
            guard let self = self, let data = data else { return }

            let x = data.acceleration.x
            let y = data.acceleration.y

            // Calculate tilt angle from accelerometer (same as Android: atan2(y, x))
            let rawAngle = atan2(y, x) * (180.0 / .pi)
            self.rawPitch = rawAngle

            // Normalize to -10...+10 range based on max steering angle
            let normalized = (rawAngle / self.maxSteeringAngle) * 10.0
            let clamped = max(-10.0, min(10.0, normalized))

            // Only send if change exceeds threshold
            if abs(clamped - self.lastSentAngle) > self.sendThreshold {
                self.currentAngle = clamped
                self.lastSentAngle = clamped
                onUpdate(clamped)
            }
        }
    }

    /// Update max steering angle while running
    func updateMaxAngle(_ angle: Double) {
        self.maxSteeringAngle = angle
    }

    func stop() {
        motionManager.stopAccelerometerUpdates()
    }

    deinit {
        stop()
    }
}
