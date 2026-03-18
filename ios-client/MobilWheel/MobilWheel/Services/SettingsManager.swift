import Foundation
import Combine

/// Manages settings/preferences, persisted via UserDefaults
final class SettingsManager: ObservableObject {
    private let defaults = UserDefaults.standard

    @Published var steeringAngle: Double {
        didSet { defaults.set(steeringAngle, forKey: Keys.steeringAngle) }
    }
    @Published var swipeThreshold: Double {
        didSet { defaults.set(swipeThreshold, forKey: Keys.swipeThreshold) }
    }
    @Published var clickTimeLimit: Double {
        didSet { defaults.set(clickTimeLimit, forKey: Keys.clickTimeLimit) }
    }
    @Published var acceleratorSensitivity: Double {
        didSet { defaults.set(acceleratorSensitivity, forKey: Keys.accelSensitivity) }
    }
    @Published var brakeSensitivity: Double {
        didSet { defaults.set(brakeSensitivity, forKey: Keys.brakeSensitivity) }
    }
    @Published var telemetryEnabled: Bool {
        didSet { defaults.set(telemetryEnabled, forKey: Keys.telemetryEnabled) }
    }

    private enum Keys {
        static let steeringAngle = "steering_angle"
        static let swipeThreshold = "swipe_threshold"
        static let clickTimeLimit = "click_time_limit"
        static let accelSensitivity = "accelerator_sensitivity"
        static let brakeSensitivity = "brake_sensitivity"
        static let telemetryEnabled = "telemetry_enabled"
    }

    init() {
        let d = UserDefaults.standard
        // Register defaults
        d.register(defaults: [
            Keys.steeringAngle: 90.0,
            Keys.swipeThreshold: 4.0,
            Keys.clickTimeLimit: 0.25,
            Keys.accelSensitivity: 4.0,
            Keys.brakeSensitivity: 4.0,
            Keys.telemetryEnabled: true
        ])

        self.steeringAngle = d.double(forKey: Keys.steeringAngle)
        self.swipeThreshold = d.double(forKey: Keys.swipeThreshold)
        self.clickTimeLimit = d.double(forKey: Keys.clickTimeLimit)
        self.acceleratorSensitivity = d.double(forKey: Keys.accelSensitivity)
        self.brakeSensitivity = d.double(forKey: Keys.brakeSensitivity)
        self.telemetryEnabled = d.bool(forKey: Keys.telemetryEnabled)
    }
}
