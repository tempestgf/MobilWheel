import SwiftUI
import UIKit

@main
struct MobilWheelApp: App {
    @StateObject private var settings = SettingsManager()
    @StateObject private var connectionManager = ConnectionManager()

    init() {
        UIView.appearance().tintColor = UIColor(mwAccent)
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
