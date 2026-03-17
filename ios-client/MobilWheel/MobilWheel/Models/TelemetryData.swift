import Foundation

/// Telemetry data received from the server or directly from the game
struct TelemetryData {
    var speed: Int = 0        // km/h
    var gear: Int = 1         // 0=R, 1=N, 2-8=gears
    var rpm: Int = 0          // 0-20000

    /// Human-readable gear label
    var gearLabel: String {
        switch gear {
        case 0: return "R"
        case 1: return "N"
        default: return "\(gear - 1)"
        }
    }

    /// RPM fraction 0.0-1.0 (assumes 8000 max, adjustable)
    var rpmFraction: Double {
        return min(Double(rpm) / 8000.0, 1.0)
    }

    /// Parse server telemetry string "T:<speed>:<gear>:<rpm>"
    static func parse(_ message: String) -> TelemetryData? {
        let trimmed = message.trimmingCharacters(in: .whitespacesAndNewlines)
        guard trimmed.hasPrefix("T:") else { return nil }
        let parts = trimmed.dropFirst(2).split(separator: ":")
        guard parts.count >= 3,
              let speed = Int(parts[0]),
              let gear = Int(parts[1]),
              let rpm = Int(parts[2]) else { return nil }
        return TelemetryData(speed: speed, gear: gear, rpm: rpm)
    }
}
