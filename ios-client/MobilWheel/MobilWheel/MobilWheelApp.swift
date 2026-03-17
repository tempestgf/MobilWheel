import SwiftUI

@main
struct MobilWheelApp: App {
    @StateObject private var settings = SettingsManager()
    @StateObject private var connectionManager = ConnectionManager()

    var body: some Scene {
        WindowGroup {
            MainMenuView()
                .environmentObject(settings)
                .environmentObject(connectionManager)
                .preferredColorScheme(.dark)
        }
    }
}
