import Foundation

/// Telemetry data received from the server or directly from the game
struct TelemetryData {
    var speed: Int = 0        // km/h
    var gear: Int = 1         // 0=R, 1=N, 2-8=gears
    var rpm: Int = 0          // 0-20000
    var ffb: Int = 0          // 0-100 force feedback intensity

    /// Parse server telemetry string "T:<speed>:<gear>:<rpm>" or "T:<speed>:<gear>:<rpm>:<ffb>"
    static func parse(_ message: String) -> TelemetryData? {
        let trimmed = message.trimmingCharacters(in: .whitespacesAndNewlines)
        guard trimmed.hasPrefix("T:") else { return nil }
        let parts = trimmed.dropFirst(2).split(separator: ":")
        guard parts.count >= 3,
              let speed = Int(parts[0]),
              let gear = Int(parts[1]),
              let rpm = Int(parts[2]) else { return nil }
        let ffb = parts.count >= 4 ? Int(parts[3]) ?? 0 : 0
        return TelemetryData(speed: speed, gear: gear, rpm: rpm, ffb: ffb)
    }
}
