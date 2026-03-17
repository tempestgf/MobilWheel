import SwiftUI

/// Connection dialog with server discovery and manual IP entry
struct ConnectView: View {
    @EnvironmentObject var connection: ConnectionManager
    @Environment(\.dismiss) var dismiss

    @State private var manualIP = ""
    @State private var isSearching = false

    var body: some View {
        ZStack {
            Color.black.ignoresSafeArea()

            VStack(spacing: 24) {
                Text("CONNECT")
                    .font(.system(size: 24, weight: .bold, design: .monospaced))
                    .foregroundColor(.white)
                    .padding(.top, 20)

                // Connection status
                HStack(spacing: 8) {
                    Circle()
                        .fill(connection.isConnected ? Color.green : Color.red)
                        .frame(width: 10, height: 10)
                    Text(connection.isConnected ? "Connected to \(connection.serverAddress)" : "Disconnected")
                        .font(.system(size: 13, design: .monospaced))
                        .foregroundColor(.white.opacity(0.7))
                }

                // Manual IP entry
                VStack(alignment: .leading, spacing: 8) {
                    Text("SERVER IP")
                        .font(.system(size: 11, weight: .medium, design: .monospaced))
                        .foregroundColor(.white.opacity(0.5))

                    HStack {
                        TextField("192.168.1.100", text: $manualIP)
                            .font(.system(size: 16, design: .monospaced))
                            .foregroundColor(.white)
                            .keyboardType(.decimalPad)
                            .padding(12)
                            .background(Color.white.opacity(0.1))
                            .cornerRadius(8)

                        Button(action: {
                            let host = manualIP.trimmingCharacters(in: .whitespacesAndNewlines)
                            if !host.isEmpty {
                                connection.connect(to: host)
                            }
                        }) {
                            Image(systemName: "arrow.right.circle.fill")
                                .font(.system(size: 32))
                                .foregroundColor(.blue)
                        }
                    }
                }
                .padding(.horizontal, 24)

                // Discover button
                Button(action: {
                    isSearching = true
                    connection.discoverServers()
                    DispatchQueue.main.asyncAfter(deadline: .now() + 3) {
                        isSearching = false
                    }
                }) {
                    HStack {
                        if isSearching {
                            ProgressView()
                                .tint(.white)
                        }
                        Text(isSearching ? "SEARCHING..." : "DISCOVER SERVERS")
                            .font(.system(size: 14, weight: .bold, design: .monospaced))
                    }
                    .foregroundColor(.white)
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, 14)
                    .background(Color.blue.opacity(0.3))
                    .cornerRadius(8)
                }
                .padding(.horizontal, 24)
                .disabled(isSearching)

                // Discovered servers list
                if !connection.discoveredServers.isEmpty {
                    VStack(alignment: .leading, spacing: 8) {
                        Text("FOUND SERVERS")
                            .font(.system(size: 11, weight: .medium, design: .monospaced))
                            .foregroundColor(.white.opacity(0.5))
                            .padding(.horizontal, 24)

                        ForEach(connection.discoveredServers, id: \.self) { server in
                            Button(action: {
                                connection.connect(to: server)
                            }) {
                                HStack {
                                    Image(systemName: "desktopcomputer")
                                        .foregroundColor(.blue)
                                    Text(server)
                                        .font(.system(size: 14, design: .monospaced))
                                        .foregroundColor(.white)
                                    Spacer()
                                    Image(systemName: "chevron.right")
                                        .foregroundColor(.white.opacity(0.3))
                                }
                                .padding(12)
                                .background(Color.white.opacity(0.08))
                                .cornerRadius(8)
                            }
                            .padding(.horizontal, 24)
                        }
                    }
                }

                Spacer()

                // Disconnect / Back
                if connection.isConnected {
                    Button(action: { connection.disconnect() }) {
                        Text("DISCONNECT")
                            .font(.system(size: 14, weight: .bold, design: .monospaced))
                            .foregroundColor(.red)
                            .frame(maxWidth: .infinity)
                            .padding(.vertical, 14)
                            .background(Color.red.opacity(0.15))
                            .cornerRadius(8)
                    }
                    .padding(.horizontal, 24)
                }

                Button(action: { dismiss() }) {
                    Text("BACK")
                        .font(.system(size: 14, weight: .bold, design: .monospaced))
                        .foregroundColor(.white)
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 14)
                        .background(Color.white.opacity(0.15))
                        .cornerRadius(8)
                }
                .padding(.horizontal, 24)
                .padding(.bottom, 30)
            }
        }
        .navigationBarHidden(true)
    }
}
