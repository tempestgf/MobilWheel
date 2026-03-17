import SwiftUI

struct MainMenuView: View {
    @EnvironmentObject var connection: ConnectionManager
    @EnvironmentObject var settings: SettingsManager

    @State private var showConnect = false
    @State private var showSettings = false
    @State private var showAbout = false
    @State private var showWheel = false
    @State private var ipAddress = ""

    var body: some View {
        NavigationStack {
            ZStack {
                // Dark gradient background
                LinearGradient(
                    colors: [Color.black, Color(white: 0.12)],
                    startPoint: .top,
                    endPoint: .bottom
                )
                .ignoresSafeArea()

                VStack(spacing: 0) {
                    Spacer()

                    // Logo / Title
                    VStack(spacing: 8) {
                        Image(systemName: "steeringwheel")
                            .font(.system(size: 64))
                            .foregroundColor(.white)

                        Text("MOBILWHEEL")
                            .font(.system(size: 32, weight: .bold, design: .monospaced))
                            .foregroundColor(.white)

                        Text("iOS Racing Controller")
                            .font(.system(size: 14, weight: .regular, design: .monospaced))
                            .foregroundColor(.white.opacity(0.5))
                    }

                    Spacer()

                    // Menu Buttons
                    VStack(spacing: 16) {
                        MenuButton(title: "START ENGINE", icon: "power") {
                            showConnect = true
                        }

                        MenuButton(title: "SETTINGS", icon: "gearshape") {
                            showSettings = true
                        }

                        MenuButton(title: "ABOUT", icon: "info.circle") {
                            showAbout = true
                        }
                    }
                    .padding(.horizontal, 40)

                    Spacer()

                    // Footer
                    Text("© 2026 MobilWheel")
                        .font(.system(size: 10, design: .monospaced))
                        .foregroundColor(.white.opacity(0.3))
                        .padding(.bottom, 20)
                }
            }
            .navigationDestination(isPresented: $showWheel) {
                WheelView()
                    .environmentObject(connection)
                    .environmentObject(settings)
                    .navigationBarHidden(true)
            }
            .navigationDestination(isPresented: $showSettings) {
                SettingsView()
                    .environmentObject(settings)
            }
            .alert("Connect to Server", isPresented: $showConnect) {
                TextField("IP Address", text: $ipAddress)
                    .keyboardType(.decimalPad)
                Button("Discover") {
                    connection.discoverServers()
                }
                Button("Connect") {
                    let host = ipAddress.trimmingCharacters(in: .whitespacesAndNewlines)
                    if !host.isEmpty {
                        connection.connect(to: host)
                        showWheel = true
                    }
                }
                Button("Cancel", role: .cancel) {}
            } message: {
                if connection.discoveredServers.isEmpty {
                    Text("Enter the server IP address or tap Discover")
                } else {
                    Text("Found: \(connection.discoveredServers.joined(separator: ", "))")
                }
            }
            .alert("About", isPresented: $showAbout) {
                Button("OK", role: .cancel) {}
            } message: {
                Text("MobilWheel iOS Client\nVersion 1.0.0\n\nAn app that simulates your phone as a steering wheel for PC racing simulators.\n\nSupports: Assetto Corsa, ACC, iRacing, Le Mans Ultimate")
            }
        }
    }
}

// MARK: - Menu Button Style

struct MenuButton: View {
    let title: String
    let icon: String
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            HStack(spacing: 12) {
                Image(systemName: icon)
                    .font(.system(size: 18, weight: .semibold))
                Text(title)
                    .font(.system(size: 16, weight: .bold, design: .monospaced))
            }
            .foregroundColor(.white)
            .frame(maxWidth: .infinity)
            .padding(.vertical, 16)
            .background(Color.white.opacity(0.1))
            .cornerRadius(12)
            .overlay(
                RoundedRectangle(cornerRadius: 12)
                    .stroke(Color.white.opacity(0.2), lineWidth: 1)
            )
        }
    }
}
