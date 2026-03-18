import SwiftUI

struct SettingsView: View {
    @EnvironmentObject var settings: SettingsManager
    @Environment(\.dismiss) var dismiss

    var body: some View {
        ZStack {
            Color.black.ignoresSafeArea()

            ScrollView {
                VStack(spacing: 28) {
                    Text("SETTINGS")
                        .font(.system(size: 24, weight: .bold, design: .monospaced))
                        .foregroundColor(.white)
                        .padding(.top, 20)

                    // Steering Angle
                    SettingSlider(
                        title: "STEERING ANGLE",
                        value: $settings.steeringAngle,
                        range: 10...900,
                        step: 1,
                        unit: "°",
                        format: "%.0f"
                    )

                    // Swipe Threshold
                    SettingSlider(
                        title: "SWIPE THRESHOLD",
                        value: $settings.swipeThreshold,
                        range: 0.1...40,
                        step: 0.1,
                        unit: "mm",
                        format: "%.1f"
                    )

                    // Click Time Limit
                    SettingSlider(
                        title: "CLICK TIME LIMIT",
                        value: $settings.clickTimeLimit,
                        range: 0.01...1.0,
                        step: 0.01,
                        unit: "sec",
                        format: "%.2f"
                    )

                    // Accelerator Sensitivity
                    SettingSlider(
                        title: "ACCELERATOR SENSITIVITY",
                        value: $settings.acceleratorSensitivity,
                        range: 0.1...8.0,
                        step: 0.1,
                        unit: "×",
                        format: "%.1f"
                    )

                    // Brake Sensitivity
                    SettingSlider(
                        title: "BRAKE SENSITIVITY",
                        value: $settings.brakeSensitivity,
                        range: 0.1...8.0,
                        step: 0.1,
                        unit: "×",
                        format: "%.1f"
                    )

                    // Telemetry toggle
                    HStack {
                        Text("ENABLE TELEMETRY")
                            .font(.system(size: 13, weight: .medium, design: .monospaced))
                            .foregroundColor(.white.opacity(0.8))
                        Spacer()
                        Toggle("", isOn: $settings.telemetryEnabled)
                            .labelsHidden()
                            .tint(mwAccent)
                    }
                    .padding(.horizontal, 24)

                    // Back button
                    Button(action: { dismiss() }) {
                        Text("BACK")
                            .font(.system(size: 16, weight: .bold, design: .monospaced))
                            .foregroundColor(.white)
                            .frame(maxWidth: .infinity)
                            .padding(.vertical, 14)
                            .background(Color.white.opacity(0.15))
                            .cornerRadius(8)
                    }
                    .padding(.horizontal, 24)
                    .padding(.bottom, 40)
                }
            }
        }
        .toolbar(.hidden, for: .navigationBar)
    }
}

// MARK: - Reusable Setting Slider

struct SettingSlider: View {
    let title: String
    @Binding var value: Double
    let range: ClosedRange<Double>
    let step: Double
    let unit: String
    let format: String

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack {
                Text(title)
                    .font(.system(size: 13, weight: .medium, design: .monospaced))
                    .foregroundColor(.white.opacity(0.8))
                Spacer()
                Text("\(String(format: format, value)) \(unit)")
                    .font(.system(size: 13, weight: .bold, design: .monospaced))
                    .foregroundColor(.white)
            }
            Slider(value: $value, in: range, step: step)
                .tint(mwAccent)
        }
        .padding(.horizontal, 24)
    }
}

#Preview {
    SettingsView()
        .environmentObject(SettingsManager())
}
