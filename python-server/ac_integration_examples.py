"""
Integration Example: Assetto Corsa Telemetry + Mobile Wheel Server

This example shows multiple ways to integrate AC telemetry with your application:
1. Simple console output
2. Integration with ServerApp GUI
3. WebSocket server for Android app
"""

import logging
import json
import asyncio
from ac_telemetry import ACTelemetryReader, ACPhysics

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# =============================================================================
# OPTION 1: Simple Integration with Callback
# =============================================================================

def simple_telemetry_integration():
    """
    Simple example: Read telemetry and print to console
    Good for testing and debugging
    """
    def on_telemetry_update(data: ACPhysics):
        # Print basic telemetry info
        print(f"\rGear: {data.gear:2d} | "
              f"RPM: {data.rpms:5d} | "
              f"Speed: {data.speed_kmh:6.1f} km/h | "
              f"Gas: {data.gas*100:4.1f}% | "
              f"Brake: {data.brake*100:4.1f}%", end='')
    
    reader = ACTelemetryReader()
    
    print("Starting simple telemetry reader...")
    print("Press Ctrl+C to stop\n")
    
    if reader.start_polling(callback=on_telemetry_update, poll_rate=0.05):
        try:
            import time
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\nStopping...")
    
    reader.stop_polling()


# =============================================================================
# OPTION 2: Integration with ServerApp GUI
# =============================================================================

class ACTelemetryGUIIntegration:
    """
    Integration example for adding AC telemetry to your existing ServerApp
    
    This would add new progress bars and labels to show:
    - Current RPM
    - Current speed
    - Current gear
    - Engine temperature
    - Tire temperatures
    """
    
    def __init__(self, server_app):
        """
        Args:
            server_app: Your ServerApp instance
        """
        self.server_app = server_app
        self.telemetry_reader = ACTelemetryReader()
        
    def add_telemetry_ui(self):
        """
        Example of how to add telemetry UI elements to ServerApp
        
        You would call this from ServerApp.__init__() after creating the main UI
        """
        import tkinter as tk
        from tkinter import ttk
        
        # Add a new frame for telemetry data
        telemetry_frame = ttk.LabelFrame(
            self.server_app.root, 
            text="Assetto Corsa Telemetry", 
            padding=(20, 10)
        )
        telemetry_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        
        # Speed label
        speed_label = ttk.Label(
            telemetry_frame, 
            text="Speed: --- km/h", 
            style="TokyoNight.TLabel"
        )
        speed_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        # Gear label
        gear_label = ttk.Label(
            telemetry_frame,
            text="Gear: -",
            style="TokyoNight.TLabel"
        )
        gear_label.grid(row=0, column=1, padx=10, pady=5, sticky="w")
        
        # RPM progress bar
        rpm_label = ttk.Label(
            telemetry_frame,
            text="RPM:",
            style="TokyoNight.TLabel"
        )
        rpm_label.grid(row=1, column=0, sticky="w")
        
        rpm_bar = ttk.Progressbar(
            telemetry_frame,
            orient="horizontal",
            length=300,
            mode="determinate",
            maximum=8000  # Adjust based on car
        )
        rpm_bar.grid(row=1, column=1, padx=10, pady=5)
        
        # Store references
        self.ui_elements = {
            'speed_label': speed_label,
            'gear_label': gear_label,
            'rpm_bar': rpm_bar
        }
    
    def on_telemetry_update(self, data: ACPhysics):
        """
        Callback to update GUI with telemetry data
        Must be called from main thread using root.after()
        """
        def update_ui():
            if hasattr(self, 'ui_elements'):
                self.ui_elements['speed_label'].config(
                    text=f"Speed: {data.speed_kmh:.1f} km/h"
                )
                self.ui_elements['gear_label'].config(
                    text=f"Gear: {data.gear if data.gear > 0 else 'R' if data.gear < 0 else 'N'}"
                )
                self.ui_elements['rpm_bar']['value'] = data.rpms
                
                # Log to the text area
                log_msg = f"AC: {data.speed_kmh:.0f} km/h | Gear {data.gear} | {data.rpms} RPM\n"
                self.server_app.log_area.configure(state='normal')
                self.server_app.log_area.insert(tk.END, log_msg)
                self.server_app.log_area.yview(tk.END)
                self.server_app.log_area.configure(state='disabled')
        
        # Schedule UI update on main thread
        self.server_app.root.after(0, update_ui)
    
    def start_telemetry(self):
        """Start reading telemetry"""
        return self.telemetry_reader.start_polling(
            callback=self.on_telemetry_update,
            poll_rate=0.05  # 20Hz update rate
        )
    
    def stop_telemetry(self):
        """Stop reading telemetry"""
        self.telemetry_reader.stop_polling()


# =============================================================================
# OPTION 3: WebSocket Server for Android App (Professional Architecture)
# =============================================================================

class ACTelemetryWebSocketServer:
    """
    WebSocket server to stream AC telemetry to Android app
    
    This is the cleanest architecture for real-time telemetry:
    Python (reads AC) → WebSocket → Android App
    
    Requires: pip install websockets
    """
    
    def __init__(self, host='0.0.0.0', port=8765):
        self.host = host
        self.port = port
        self.telemetry_reader = ACTelemetryReader()
        self.clients = set()
        self.running = False
        
    def telemetry_to_json(self, data: ACPhysics) -> str:
        """Convert telemetry data to JSON for transmission"""
        # Send essential data (you can customize this)
        telemetry_dict = {
            'gear': data.gear,
            'rpms': data.rpms,
            'speed_kmh': round(data.speed_kmh, 1),
            'speed_mph': round(data.speed_kmh * 0.621371, 1),
            'gas': round(data.gas * 100, 1),
            'brake': round(data.brake * 100, 1),
            'clutch': round(data.clutch * 100, 1),
            'steer_angle': round(data.steer_angle, 2),
            'turbo_boost': round(data.turbo_boost, 2),
            'fuel': round(data.fuel, 1),
            'tyre_temps': {
                'fl': round(data.tyre_core_temperature[0], 1),
                'fr': round(data.tyre_core_temperature[1], 1),
                'rl': round(data.tyre_core_temperature[2], 1),
                'rr': round(data.tyre_core_temperature[3], 1),
            },
            'brake_temps': {
                'fl': round(data.brake_temp[0], 1),
                'fr': round(data.brake_temp[1], 1),
                'rl': round(data.brake_temp[2], 1),
                'rr': round(data.brake_temp[3], 1),
            },
            'g_force': {
                'lateral': round(data.acc_g_x, 2),
                'longitudinal': round(data.acc_g_y, 2),
                'vertical': round(data.acc_g_z, 2),
            },
            'abs': data.abs > 0,
            'tc': data.tc > 0,
            'drs': data.drs > 0,
            'pit_limiter': data.pit_limiter_on == 1,
        }
        
        return json.dumps(telemetry_dict)
    
    async def handle_client(self, websocket, path):
        """Handle a WebSocket client connection"""
        self.clients.add(websocket)
        client_address = websocket.remote_address
        logger.info(f"Client connected from {client_address}")
        
        try:
            # Send welcome message
            await websocket.send(json.dumps({'status': 'connected', 'message': 'AC Telemetry Server'}))
            
            # Keep connection alive
            async for message in websocket:
                # Handle incoming messages from client if needed
                logger.debug(f"Received from {client_address}: {message}")
                
        except Exception as e:
            logger.error(f"Error handling client {client_address}: {e}")
        finally:
            self.clients.remove(websocket)
            logger.info(f"Client disconnected from {client_address}")
    
    def on_telemetry_update(self, data: ACPhysics):
        """Broadcast telemetry to all connected clients"""
        if not self.clients:
            return
        
        try:
            json_data = self.telemetry_to_json(data)
            
            # Create async task to send to all clients
            asyncio.create_task(self.broadcast(json_data))
            
        except Exception as e:
            logger.error(f"Error broadcasting telemetry: {e}")
    
    async def broadcast(self, message: str):
        """Send message to all connected clients"""
        if self.clients:
            # Send to all clients concurrently
            await asyncio.gather(
                *[client.send(message) for client in self.clients],
                return_exceptions=True
            )
    
    async def start_server(self):
        """Start the WebSocket server"""
        try:
            import websockets
        except ImportError:
            logger.error("websockets package not installed. Run: pip install websockets")
            return
        
        # Start telemetry reader
        if not self.telemetry_reader.start_polling(
            callback=self.on_telemetry_update,
            poll_rate=0.033  # ~30fps
        ):
            logger.error("Failed to start telemetry reader")
            return
        
        # Start WebSocket server
        logger.info(f"Starting WebSocket server on {self.host}:{self.port}")
        
        async with websockets.serve(self.handle_client, self.host, self.port):
            self.running = True
            logger.info("WebSocket server is running. Press Ctrl+C to stop")
            
            # Run forever
            await asyncio.Future()  # Run forever
    
    def run(self):
        """Run the WebSocket server (blocking)"""
        try:
            asyncio.run(self.start_server())
        except KeyboardInterrupt:
            logger.info("Shutting down...")
        finally:
            self.telemetry_reader.stop_polling()


# =============================================================================
# OPTION 4: Combined Server (Wheel Input + AC Telemetry)
# =============================================================================

def create_combined_server():
    """
    Example of combining your existing wheel server with AC telemetry
    This would broadcast both wheel input AND game telemetry to Android app
    """
    
    print("""
    === Combined Mobile Wheel + AC Telemetry Server ===
    
    This architecture streams:
    - Wheel/controller input TO the game (your existing functionality)
    - Game telemetry FROM AC to your Android app (new functionality)
    
    Your Android app could then display:
    - Real-time RPM, speed, gear
    - Tire temps and pressures
    - G-force display
    - Delta time
    - Whatever telemetry you want!
    
    To implement this, you would:
    1. Add ACTelemetryReader to your xbox.py server
    2. Broadcast telemetry over the same socket connection
    3. Update Android app to receive and display telemetry
    
    Example message format:
    {
        "type": "telemetry",
        "data": {
            "rpm": 7500,
            "speed": 215.3,
            "gear": 5,
            ...
        }
    }
    """)


# =============================================================================
# Main Demo Runner
# =============================================================================

def main():
    print("=== Assetto Corsa Telemetry Integration Examples ===\n")
    print("Choose an option:")
    print("1. Simple console output")
    print("2. WebSocket server for Android app")
    print("3. Show combined server concept")
    print("0. Exit")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        simple_telemetry_integration()
    elif choice == "2":
        server = ACTelemetryWebSocketServer(host='0.0.0.0', port=8765)
        print("\nWebSocket server will start on port 8765")
        print("Connect your Android app to: ws://<your-pc-ip>:8765")
        server.run()
    elif choice == "3":
        create_combined_server()
    else:
        print("Exiting...")


if __name__ == "__main__":
    main()
