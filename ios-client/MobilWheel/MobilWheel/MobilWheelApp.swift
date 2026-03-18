import SwiftUI
import UIKit

@main
struct MobilWheelApp: App {
    @StateObject private var settings = SettingsManager()
    @StateObject private var connectionManager = ConnectionManager()

    init() {
        UIView.appearance().tintColor = UIColor(red: 1.0, green: 0.427, blue: 0.0, alpha: 1.0)
    }

    var body: some Scene {
        WindowGroup {
            MainMenuView()
                .environmentObject(settings)
                .environmentObject(connectionManager)
                .preferredColorScheme(.dark)
                .accentColor(mwAccent)
                .tint(mwAccent)
                .background(Color.black)
        }
    }
}
