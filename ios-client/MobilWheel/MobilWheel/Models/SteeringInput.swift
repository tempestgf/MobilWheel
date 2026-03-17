import Foundation

/// Represents the current state of all steering inputs
struct SteeringInput {
    var steeringAngle: Double = 0.0   // -10.0 to +10.0
    var throttle: Int = 0              // 0-100
    var brake: Int = 0                 // 0-100
}

/// Commands sent to the server
enum ServerCommand {
    case steering(Double)       // A:<angle>
    case throttle(Int)          // B:<value>
    case brake(Int)             // C:<value>
    case leftTop                // D
    case leftBottom             // E
    case rightTop               // F
    case rightBottom            // G
    case volumeUp               // VOLUME_UP
    case volumeDown             // VOLUME_DOWN

    var rawCommand: String {
        switch self {
        case .steering(let angle):
            return "A:\(String(format: "%.1f", angle))\n"
        case .throttle(let value):
            return "B:\(value)\n"
        case .brake(let value):
            return "C:\(value)\n"
        case .leftTop:
            return "D\n"
        case .leftBottom:
            return "E\n"
        case .rightTop:
            return "F\n"
        case .rightBottom:
            return "G\n"
        case .volumeUp:
            return "VOLUME_UP\n"
        case .volumeDown:
            return "VOLUME_DOWN\n"
        }
    }
}
