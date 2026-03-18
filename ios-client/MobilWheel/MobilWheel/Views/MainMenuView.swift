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

                VStack(spacing: 16) {
                    Spacer()

                    // Logo / Title
                    HStack(spacing: 16) {
                        Image(systemName: "steeringwheel")
                            .font(.system(size: 40))
                            .foregroundColor(.white)

                        VStack(alignment: .leading, spacing: 2) {
                            Text("MOBILWHEEL")
                                .font(.system(size: 24, weight: .bold, design: .monospaced))
                                .foregroundColor(.white)

                            Text("iOS Racing Controller")
                                .font(.system(size: 11, weight: .regular, design: .monospaced))
                                .foregroundColor(.white.opacity(0.5))
                        }
                    }

                    Spacer()

                    // Menu Buttons
                    VStack(spacing: 12) {
                        MenuButton(title: "START ENGINE", icon: "power", prominent: true) {
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
                        .padding(.bottom, 4)
                }
            }
            .navigationDestination(isPresented: $showWheel) {
                WheelView()
                    .environmentObject(connection)
                    .environmentObject(settings)
                    .toolbar(.hidden, for: .navigationBar)
            }
            .navigationDestination(isPresented: $showSettings) {
                SettingsView()
                    .environmentObject(settings)
            }
            .alert("About", isPresented: $showAbout) {
                Button("OK", role: .cancel) {}
            } message: {
                Text("MobilWheel iOS Client\nVersion 1.0.0\n\nAn app that simulates your phone as a steering wheel for PC racing simulators.\n\nSupports: Assetto Corsa, ACC, iRacing, Le Mans Ultimate")
            }
            .overlay {
                if showConnect {
                    Color.black.opacity(0.6)
                        .ignoresSafeArea()
                        .onTapGesture { showConnect = false }

                    VStack(spacing: 16) {
                        Text("Connect to Server")
                            .font(.system(size: 16, weight: .bold, design: .monospaced))
                            .foregroundColor(.white)

                        TextField("IP Address", text: $ipAddress)
                            .keyboardType(.URL)
                            .autocorrectionDisabled()
                            .textInputAutocapitalization(.never)
                            .padding(12)
                            .background(Color.white.opacity(0.1))
                            .foregroundColor(.white)
                            .cornerRadius(8)
                            .overlay(
                                RoundedRectangle(cornerRadius: 8)
                                    .stroke(Color.white.opacity(0.3), lineWidth: 1)
                            )

                        if !connection.discoveredServers.isEmpty {
                            Text("Found: \(connection.discoveredServers.joined(separator: ", "))")
                                .font(.system(size: 11, design: .monospaced))
                                .foregroundColor(.white.opacity(0.5))
                        } else {
                            Text("Enter IP or tap Discover")
                                .font(.system(size: 11, design: .monospaced))
                                .foregroundColor(.white.opacity(0.3))
                        }

                        HStack(spacing: 12) {
                            Button {
                                connection.discoverServers()
                            } label: {
                                Text("Discover")
                                    .font(.system(size: 14, weight: .semibold, design: .monospaced))
                                    .foregroundColor(.white)
                                    .frame(maxWidth: .infinity)
                                    .padding(.vertical, 12)
                                    .background(Color.white.opacity(0.1))
                                    .cornerRadius(8)
                            }

                            Button {
                                let host = ipAddress.trimmingCharacters(in: .whitespacesAndNewlines)
                                if !host.isEmpty {
                                    connection.connect(to: host)
                                    showConnect = false
                                    showWheel = true
                                }
                            } label: {
                                Text("Connect")
                                    .font(.system(size: 14, weight: .bold, design: .monospaced))
                                    .foregroundColor(.black)
                                    .frame(maxWidth: .infinity)
                                    .padding(.vertical, 12)
                                    .background(mwAccent)
                                    .cornerRadius(8)
                            }
                        }

                        Button {
                            showConnect = false
                        } label: {
                            Text("Cancel")
                                .font(.system(size: 13, design: .monospaced))
                                .foregroundColor(.white.opacity(0.5))
                        }
                    }
                    .padding(24)
                    .frame(maxWidth: 340)
                    .background(Color(white: 0.15))
                    .cornerRadius(16)
                    .overlay(
                        RoundedRectangle(cornerRadius: 16)
                            .stroke(Color.white.opacity(0.1), lineWidth: 1)
                    )
                }
            }
        }
        .background(Color.black)
        .onAppear {
            UIApplication.shared.isIdleTimerDisabled = true
        }
    }
}

// MARK: - Menu Button Style

struct MenuButton: View {
    let title: String
    let icon: String
    var prominent: Bool = false
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            HStack(spacing: 12) {
                Image(systemName: icon)
                    .font(.system(size: 18, weight: .semibold))
                Text(title)
                    .font(.system(size: 16, weight: .bold, design: .monospaced))
            }
            .foregroundColor(prominent ? .black : .white)
            .frame(maxWidth: .infinity)
            .padding(.vertical, 16)
            .background(prominent ? mwAccent : Color.white.opacity(0.1))
            .cornerRadius(12)
            .overlay(
                RoundedRectangle(cornerRadius: 12)
                    .stroke(prominent ? mwAccent : Color.white.opacity(0.2), lineWidth: 1)
            )
        }
    }
}

#Preview {
    MainMenuView()
        .environmentObject(ConnectionManager())
        .environmentObject(SettingsManager())
}
