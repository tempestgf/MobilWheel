import Foundation
import Network
import Combine

/// Manages TCP connection to the Python server and UDP discovery
final class ConnectionManager: ObservableObject {
    @Published var isConnected = false
    @Published var serverAddress: String = ""
    @Published var telemetry = TelemetryData()
    @Published var discoveredServers: [String] = []
    @Published var latencyMs: Int = 0

    private var tcpConnection: NWConnection?
    private var udpListener: NWListener?
    private var commandQueue = DispatchQueue(label: "com.mobilwheel.commands", qos: .userInteractive)
    private let serverPort: UInt16 = 12345

    // MARK: - UDP Discovery

    /// Broadcast to discover servers on the local network
    func discoverServers() {
        discoveredServers = []
        let params = NWParameters.udp
        let connection = NWConnection(
            host: .ipv4(.broadcast),
            port: NWEndpoint.Port(rawValue: serverPort)!,
            using: params
        )

        connection.stateUpdateHandler = { [weak self] state in
            if case .ready = state {
                let message = "DISCOVER_SERVER".data(using: .utf8)!
                connection.send(content: message, completion: .contentProcessed { _ in
                    self?.receiveDiscoveryResponse(connection: connection)
                })
            }
        }
        connection.start(queue: .global(qos: .userInitiated))

        // Timeout after 3 seconds
        DispatchQueue.global().asyncAfter(deadline: .now() + 3) {
            connection.cancel()
        }
    }

    private func receiveDiscoveryResponse(connection: NWConnection) {
        connection.receive(minimumIncompleteLength: 1, maximumLength: 1024) { [weak self] data, _, _, _ in
            guard let data = data, let response = String(data: data, encoding: .utf8) else { return }
            let address = response.trimmingCharacters(in: .whitespacesAndNewlines)
                .components(separatedBy: ":").first ?? response
            DispatchQueue.main.async {
                if !address.isEmpty && !(self?.discoveredServers.contains(address) ?? true) {
                    self?.discoveredServers.append(address)
                }
            }
            // Keep listening for more responses
            self?.receiveDiscoveryResponse(connection: connection)
        }
    }

    // MARK: - TCP Connection

    func connect(to host: String) {
        disconnect()
        serverAddress = host

        let params = NWParameters.tcp
        params.requiredInterfaceType = .wifi

        let connection = NWConnection(
            host: NWEndpoint.Host(host),
            port: NWEndpoint.Port(rawValue: serverPort)!,
            using: params
        )

        connection.stateUpdateHandler = { [weak self] state in
            DispatchQueue.main.async {
                switch state {
                case .ready:
                    self?.isConnected = true
                    self?.startReceiving()
                case .failed, .cancelled:
                    self?.isConnected = false
                    self?.tcpConnection = nil
                default:
                    break
                }
            }
        }

        tcpConnection = connection
        connection.start(queue: commandQueue)
    }

    func disconnect() {
        tcpConnection?.cancel()
        tcpConnection = nil
        DispatchQueue.main.async {
            self.isConnected = false
            self.serverAddress = ""
        }
    }

    // MARK: - Send Commands

    func send(_ command: ServerCommand) {
        guard let connection = tcpConnection, isConnected else { return }
        guard let data = command.rawCommand.data(using: .utf8) else { return }
        connection.send(content: data, completion: .contentProcessed { error in
            if let error = error {
                print("Send error: \(error)")
            }
        })
    }

    func sendRaw(_ string: String) {
        guard let connection = tcpConnection, isConnected else { return }
        guard let data = string.data(using: .utf8) else { return }
        connection.send(content: data, completion: .contentProcessed { _ in })
    }

    // MARK: - Receive Telemetry

    private func startReceiving() {
        guard let connection = tcpConnection else { return }
        connection.receive(minimumIncompleteLength: 1, maximumLength: 4096) { [weak self] data, _, isComplete, error in
            if let data = data, let message = String(data: data, encoding: .utf8) {
                // Can receive multiple lines at once
                let lines = message.components(separatedBy: "\n")
                for line in lines {
                    if let telemetry = TelemetryData.parse(line) {
                        DispatchQueue.main.async {
                            self?.telemetry = telemetry
                        }
                    }
                }
            }
            if isComplete || error != nil {
                DispatchQueue.main.async {
                    self?.isConnected = false
                }
                return
            }
            // Continue receiving
            self?.startReceiving()
        }
    }
}
