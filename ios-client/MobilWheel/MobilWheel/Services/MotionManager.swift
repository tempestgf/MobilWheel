import CoreMotion
import UIKit

/// Reads device accelerometer and converts tilt to steering angle
final class MotionManager: ObservableObject {
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

            // Accelerometer axes are fixed to the hardware (portrait frame).
            // We need to rotate them into screen coordinates so steering
            // always matches the visible UI regardless of landscape orientation.
            //
            // Landscape-left  (home btn right): screenRight = +devY, screenUp = −devX → atan2( y, −x)
            // Landscape-right (home btn left):  screenRight = −devY, screenUp = +devX → atan2(−y,  x)
            let orientation = UIApplication.shared.connectedScenes
                .compactMap { $0 as? UIWindowScene }
                .first?.interfaceOrientation

            let rawAngle: Double
            if orientation == .landscapeRight {
                rawAngle = atan2(y, -x) * (180.0 / .pi)
            } else {
                rawAngle = atan2(-y, x) * (180.0 / .pi)
            }

            // Normalize to -10...+10 range based on max steering angle
            let normalized = -(rawAngle / self.maxSteeringAngle) * 10.0
            let clamped = max(-10.0, min(10.0, normalized))

            // Only send if change exceeds threshold
            if abs(clamped - self.lastSentAngle) > self.sendThreshold {
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
