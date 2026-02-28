"""
Assetto Corsa Telemetry Reader
Reads physics data from AC's shared memory (acpmf_physics)
Based on the official shared memory structure from assettocorsa/system/cfg/sharedmemory/sim_info.h
"""

import mmap
import struct
import ctypes
import logging
from dataclasses import dataclass
from typing import Optional, Callable
import threading
import time
import subprocess
import socket
import math

try:
    import irsdk
    IRSDK_AVAILABLE = True
except ImportError:
    IRSDK_AVAILABLE = False
    logging.warning("pyirsdk not installed. iRacing telemetry will not work. Run 'pip install pyirsdk'")

# Configure logging
logger = logging.getLogger(__name__)

def detect_running_game() -> Optional[str]:
    """
    Detects which supported racing game is currently running.
    Returns the name of the game or None if none are detected.
    """
    try:
        # Use tasklist to get running processes
        output = subprocess.check_output('tasklist', shell=True).decode('utf-8', errors='ignore').lower()
        
        if 'acs.exe' in output or 'acs_x86.exe' in output:
            return 'Assetto Corsa'
        elif 'iracingsim64.exe' in output or 'iracingsim64dx11.exe' in output:
            return 'iRacing'
        elif 'f1_25.exe' in output or 'f1_24.exe' in output or 'f1_23.exe' in output or 'f1_22.exe' in output:
            return 'F1 25'
        elif 'rrre64.exe' in output or 'rrre.exe' in output:
            return 'RaceRoom'
        elif 'le mans ultimate.exe' in output:
            return 'Le Mans Ultimate'
            
    except Exception as e:
        logger.error(f"Error detecting game: {e}")
        
    return None

@dataclass
class GamePhysics:
    """Generic data class containing physics telemetry for any game"""
    game_name: str
    gear: int
    rpms: int
    speed_kmh: float
    gas: float = 0.0
    brake: float = 0.0

@dataclass
class ACPhysics:
    """Data class containing all physics telemetry from Assetto Corsa"""
    
    # Basic info
    packet_id: int
    gas: float
    brake: float
    fuel: float
    gear: int
    rpms: int
    steer_angle: float
    speed_kmh: float
    
    # Velocity (world coordinates)
    velocity_x: float
    velocity_y: float
    velocity_z: float
    
    # Acceleration (local coordinates)
    acc_g_x: float
    acc_g_y: float
    acc_g_z: float
    
    # Wheel slip
    wheel_slip: tuple  # 4 floats (FL, FR, RL, RR)
    
    # Wheel load (not used in public version)
    wheel_load: tuple  # 4 floats
    
    # Wheels pressure
    wheels_pressure: tuple  # 4 floats
    
    # Wheel angular speed
    wheel_angular_speed: tuple  # 4 floats
    
    # Tyres wear (not used in public version)
    tyre_wear: tuple  # 4 floats
    
    # Tyre dirty level
    tyre_dirty_level: tuple  # 4 floats
    
    # Tyres core temperature
    tyre_core_temperature: tuple  # 4 floats
    
    # Camber angle RAD
    camber_rad: tuple  # 4 floats
    
    # Suspension travel
    suspension_travel: tuple  # 4 floats
    
    # DRS
    drs: float
    
    # TC
    tc: float
    
    # Heading
    heading: float
    
    # Pitch
    pitch: float
    
    # Roll
    roll: float
    
    # Additional data
    cg_height: float
    car_damage: tuple  # 5 floats
    
    # Pit limiter
    pit_limiter_on: int
    
    # ABS
    abs: float
    
    # Auto shifter
    auto_shifter_on: int
    
    # Turbo boost
    turbo_boost: float
    
    # Air temp
    air_temp: float
    
    # Road temp
    road_temp: float
    
    # Local angular velocity
    local_angular_vel_x: float
    local_angular_vel_y: float
    local_angular_vel_z: float
    
    # Final force feedback
    final_ff: float
    
    # Brake temp
    brake_temp: tuple  # 4 floats
    
    # Clutch
    clutch: float
    
    # Is AI controlled
    is_ai_controlled: int
    
    # Tyre contact point
    tyre_contact_point: tuple  # 4x3 floats (global coordinates)
    
    # Tyre contact normal
    tyre_contact_normal: tuple  # 4x3 floats (global coordinates)
    
    # Tyre contact heading
    tyre_contact_heading: tuple  # 4x3 floats (global coordinates)
    
    # Brake bias
    brake_bias: float


class ACTelemetryReader:
    """
    Professional Assetto Corsa telemetry reader using shared memory.
    
    Features:
    - Full physics structure support
    - Thread-safe operation
    - Error handling and recovery
    - Callback support for real-time updates
    - 60fps+ capable
    """
    
    SHARED_MEMORY_NAME = "Local\\acpmf_physics"
    
    # Complete structure definition matching AC's shared memory
    # Reference: assettocorsa/system/cfg/sharedmemory/sim_info.h
    PHYSICS_STRUCT = (
        "i"      # packetId (int)
        "f"      # gas (float)
        "f"      # brake (float)
        "f"      # fuel (float)
        "i"      # gear (int)
        "i"      # rpms (int)
        "f"      # steerAngle (float)
        "f"      # speedKmh (float)
        "fff"    # velocity (3 floats)
        "fff"    # accG (3 floats)
        "ffff"   # wheelSlip (4 floats)
        "ffff"   # wheelLoad (4 floats)
        "ffff"   # wheelsPressure (4 floats)
        "ffff"   # wheelAngularSpeed (4 floats)
        "ffff"   # tyreWear (4 floats)
        "ffff"   # tyreDirtyLevel (4 floats)
        "ffff"   # tyreCoreTemperature (4 floats)
        "ffff"   # camberRAD (4 floats)
        "ffff"   # suspensionTravel (4 floats)
        "f"      # drs (float)
        "f"      # tc (float)
        "f"      # heading (float)
        "f"      # pitch (float)
        "f"      # roll (float)
        "f"      # cgHeight (float)
        "fffff"  # carDamage (5 floats)
        "i"      # pitLimiterOn (int)
        "f"      # abs (float)
        "i"      # autoShifterOn (int)
        "f"      # turboBoost (float)
        "f"      # airTemp (float)
        "f"      # roadTemp (float)
        "fff"    # localAngularVelocity (3 floats)
        "f"      # finalFF (float)
        "ffff"   # brakeTemp (4 floats)
        "f"      # clutch (float)
        "i"      # isAIControlled (int)
        "fff"    # tyreContactPoint[0] (3 floats)
        "fff"    # tyreContactPoint[1] (3 floats)
        "fff"    # tyreContactPoint[2] (3 floats)
        "fff"    # tyreContactPoint[3] (3 floats)
        "fff"    # tyreContactNormal[0] (3 floats)
        "fff"    # tyreContactNormal[1] (3 floats)
        "fff"    # tyreContactNormal[2] (3 floats)
        "fff"    # tyreContactNormal[3] (3 floats)
        "fff"    # tyreContactHeading[0] (3 floats)
        "fff"    # tyreContactHeading[1] (3 floats)
        "fff"    # tyreContactHeading[2] (3 floats)
        "fff"    # tyreContactHeading[3] (3 floats)
        "f"      # brakeBias (float)
    )
    
    STRUCT_SIZE = struct.calcsize(PHYSICS_STRUCT)
    
    def __init__(self):
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.current_data: Optional[ACPhysics] = None
        self.data_lock = threading.RLock()
        self.mmap_handle: Optional[mmap.mmap] = None
        
    def connect(self) -> bool:
        """
        Attempt to connect to Assetto Corsa's shared memory.
        Returns True if successful, False otherwise.
        """
        try:
            self.mmap_handle = mmap.mmap(-1, self.STRUCT_SIZE, self.SHARED_MEMORY_NAME)
            logger.info("Successfully connected to Assetto Corsa shared memory")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to AC shared memory: {e}")
            self.mmap_handle = None
            return False
    
    def disconnect(self):
        """Close the shared memory connection"""
        if self.mmap_handle:
            try:
                self.mmap_handle.close()
                logger.info("Disconnected from AC shared memory")
            except Exception as e:
                logger.error(f"Error closing shared memory: {e}")
            finally:
                self.mmap_handle = None
    
    def read_physics(self) -> Optional[ACPhysics]:
        """
        Read current physics data from shared memory.
        Returns ACPhysics object or None if read fails.
        """
        if not self.mmap_handle:
            return None
            
        try:
            # Seek to beginning and read all data
            self.mmap_handle.seek(0)
            data = self.mmap_handle.read(self.STRUCT_SIZE)
            
            # Unpack the binary data
            unpacked = struct.unpack(self.PHYSICS_STRUCT, data)
            
            # Parse into ACPhysics object
            idx = 0
            physics = ACPhysics(
                packet_id=unpacked[idx],
                gas=unpacked[idx+1],
                brake=unpacked[idx+2],
                fuel=unpacked[idx+3],
                gear=unpacked[idx+4] - 1,  # AC returns: 0=R, 1=N, 2+=gears, so we subtract 1
                rpms=unpacked[idx+5],
                steer_angle=unpacked[idx+6],
                speed_kmh=unpacked[idx+7],
                velocity_x=unpacked[idx+8],
                velocity_y=unpacked[idx+9],
                velocity_z=unpacked[idx+10],
                acc_g_x=unpacked[idx+11],
                acc_g_y=unpacked[idx+12],
                acc_g_z=unpacked[idx+13],
                wheel_slip=unpacked[idx+14:idx+18],
                wheel_load=unpacked[idx+18:idx+22],
                wheels_pressure=unpacked[idx+22:idx+26],
                wheel_angular_speed=unpacked[idx+26:idx+30],
                tyre_wear=unpacked[idx+30:idx+34],
                tyre_dirty_level=unpacked[idx+34:idx+38],
                tyre_core_temperature=unpacked[idx+38:idx+42],
                camber_rad=unpacked[idx+42:idx+46],
                suspension_travel=unpacked[idx+46:idx+50],
                drs=unpacked[idx+50],
                tc=unpacked[idx+51],
                heading=unpacked[idx+52],
                pitch=unpacked[idx+53],
                roll=unpacked[idx+54],
                cg_height=unpacked[idx+55],
                car_damage=unpacked[idx+56:idx+61],
                pit_limiter_on=unpacked[idx+61],
                abs=unpacked[idx+62],
                auto_shifter_on=unpacked[idx+63],
                turbo_boost=unpacked[idx+64],
                air_temp=unpacked[idx+65],
                road_temp=unpacked[idx+66],
                local_angular_vel_x=unpacked[idx+67],
                local_angular_vel_y=unpacked[idx+68],
                local_angular_vel_z=unpacked[idx+69],
                final_ff=unpacked[idx+70],
                brake_temp=unpacked[idx+71:idx+75],
                clutch=unpacked[idx+75],
                is_ai_controlled=unpacked[idx+76],
                tyre_contact_point=unpacked[idx+77:idx+89],  # 4x3 floats
                tyre_contact_normal=unpacked[idx+89:idx+101],  # 4x3 floats
                tyre_contact_heading=unpacked[idx+101:idx+113],  # 4x3 floats
                brake_bias=unpacked[idx+113],
            )
            
            with self.data_lock:
                self.current_data = physics
            
            return physics
            
        except Exception as e:
            logger.error(f"Error reading physics data: {e}")
            return None
    
    def get_current_data(self) -> Optional[ACPhysics]:
        """Get the most recently read physics data (thread-safe)"""
        with self.data_lock:
            return self.current_data
    
    def start_polling(self, callback: Optional[Callable[[ACPhysics], None]] = None, 
                     poll_rate: float = 0.016) -> bool:
        """
        Start polling telemetry data in a background thread.
        
        Args:
            callback: Optional function to call with each new data reading
            poll_rate: Polling interval in seconds (default: 0.016 = ~60fps)
        
        Returns:
            True if polling started successfully
        """
        if self.running:
            logger.warning("Polling already running")
            return False
        
        if not self.connect():
            return False
        
        self.running = True
        self.thread = threading.Thread(
            target=self._polling_loop,
            args=(callback, poll_rate),
            daemon=True
        )
        self.thread.start()
        logger.info(f"Started telemetry polling at {1/poll_rate:.1f} fps")
        return True
    
    def stop_polling(self):
        """Stop the polling thread"""
        if not self.running:
            return
        
        self.running = False
        if self.thread:
            self.thread.join(timeout=2.0)
        self.disconnect()
        logger.info("Stopped telemetry polling")
    
    def _polling_loop(self, callback: Optional[Callable], poll_rate: float):
        """Internal polling loop running in background thread"""
        last_packet_id = -1
        
        while self.running:
            try:
                data = self.read_physics()
                
                if data and callback:
                    # Only call callback if we got new data
                    if data.packet_id != last_packet_id:
                        callback(data)
                        last_packet_id = data.packet_id
                
                time.sleep(poll_rate)
                
            except Exception as e:
                logger.error(f"Error in polling loop: {e}")
                time.sleep(1)  # Wait longer on error
    
    def __enter__(self):
        """Context manager support"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager cleanup"""
        self.stop_polling()
        self.disconnect()


class IRacingTelemetryReader:
    """
    iRacing telemetry reader using pyirsdk.
    """
    def __init__(self):
        self.ir = None
        self.connected = False
        
    def connect(self) -> bool:
        if not IRSDK_AVAILABLE:
            logger.error("pyirsdk not installed. Cannot connect to iRacing.")
            return False
            
        try:
            self.ir = irsdk.IRSDK()
            if self.ir.startup():
                self.connected = True
                logger.info("Successfully connected to iRacing telemetry")
                return True
            else:
                logger.error("Failed to connect to iRacing telemetry. Is the game running?")
                return False
        except Exception as e:
            logger.error(f"Error connecting to iRacing: {e}")
            return False
            
    def disconnect(self):
        if self.ir and self.connected:
            self.ir.shutdown()
            self.connected = False
            logger.info("Disconnected from iRacing telemetry")
            
    def read_physics(self) -> Optional[GamePhysics]:
        if not self.connected or not self.ir:
            return None
            
        try:
            # Check if we are still connected and data is fresh
            if not self.ir.is_initialized or not self.ir.is_connected:
                self.connected = False
                return None
                
            # Freeze the data to read it consistently
            self.ir.freeze_var_buffer_latest()
            
            # Read values
            gear = self.ir['Gear']
            rpm = self.ir['RPM']
            speed_ms = self.ir['Speed']
            gas = self.ir['Throttle']
            brake = self.ir['Brake']
            
            # Handle None values if telemetry isn't fully ready
            if gear is None or rpm is None or speed_ms is None:
                return None
                
            # Convert speed from m/s to km/h
            speed_kmh = speed_ms * 3.6
            
            return GamePhysics(
                game_name='iRacing',
                gear=int(gear),
                rpms=int(rpm),
                speed_kmh=float(speed_kmh),
                gas=float(gas) if gas is not None else 0.0,
                brake=float(brake) if brake is not None else 0.0
            )
        except Exception as e:
            logger.error(f"Error reading iRacing telemetry: {e}")
            return None

class RaceRoomTelemetryReader:
    """
    RaceRoom telemetry reader using shared memory.
    """
    SHM_NAME = "$R3E"
    SHM_SIZE = 40960
    
    def __init__(self):
        self.mmap_handle = None
        
    def connect(self) -> bool:
        try:
            self.mmap_handle = mmap.mmap(-1, self.SHM_SIZE, self.SHM_NAME, access=mmap.ACCESS_READ)
            logger.info("Successfully connected to RaceRoom shared memory")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to RaceRoom shared memory: {e}")
            self.mmap_handle = None
            return False
            
    def disconnect(self):
        if self.mmap_handle:
            try:
                self.mmap_handle.close()
                logger.info("Disconnected from RaceRoom shared memory")
            except Exception as e:
                logger.error(f"Error closing RaceRoom shared memory: {e}")
            finally:
                self.mmap_handle = None
                
    def read_physics(self) -> Optional[GamePhysics]:
        if not self.mmap_handle:
            return None
            
        try:
            # Read from specific offsets
            speed_ms = struct.unpack_from('<f', self.mmap_handle, 1336)[0]
            engine_rps = struct.unpack_from('<f', self.mmap_handle, 1340)[0]
            gear = struct.unpack_from('<i', self.mmap_handle, 1352)[0]
            gas = struct.unpack_from('<f', self.mmap_handle, 1432)[0]
            brake = struct.unpack_from('<f', self.mmap_handle, 1440)[0]
            
            # Conversions
            rpm = engine_rps * (60 / (2 * math.pi)) # rad/s to RPM
            speed_kmh = speed_ms * 3.6              # m/s to km/h
            
            return GamePhysics(
                game_name='RaceRoom',
                gear=int(gear),
                rpms=int(rpm),
                speed_kmh=float(speed_kmh),
                gas=float(gas),
                brake=float(brake)
            )
        except Exception as e:
            logger.error(f"Error reading RaceRoom telemetry: {e}")
            return None

class F1TelemetryReader:
    """
    F1 2022-2025 telemetry reader using UDP.
    """
    # F1 2023 / 2024 UDP Telemetry format
    # Header is 29 bytes
    HEADER_FORMAT = '<HBBBBBQfIIBB'
    HEADER_SIZE = struct.calcsize(HEADER_FORMAT)

    # Car Telemetry Data is 60 bytes per car
    CAR_TELEMETRY_FORMAT = '<HfffBbHBBHHHHHBBBBBBBBHffffBBBB'
    CAR_TELEMETRY_SIZE = struct.calcsize(CAR_TELEMETRY_FORMAT)
    
    def __init__(self, port=20777):
        self.port = port
        self.sock = None
        self.last_data = None
        self.running = False
        self.thread = None
        self.data_lock = threading.RLock()
        
    def connect(self) -> bool:
        try:
            self.sock = socket.socket(socket.AF_INET, socket.socket.SOCK_DGRAM)
            self.sock.bind(("0.0.0.0", self.port))
            self.sock.settimeout(0.5) # Non-blocking with timeout
            self.running = True
            self.thread = threading.Thread(target=self._udp_listener, daemon=True)
            self.thread.start()
            logger.info(f"Successfully started F1 UDP listener on port {self.port}")
            return True
        except Exception as e:
            logger.error(f"Failed to start F1 UDP listener: {e}")
            self.sock = None
            return False
            
    def disconnect(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=1.0)
        if self.sock:
            try:
                self.sock.close()
                logger.info("Closed F1 UDP listener")
            except Exception as e:
                logger.error(f"Error closing F1 UDP socket: {e}")
            finally:
                self.sock = None
                
    def _udp_listener(self):
        while self.running and self.sock:
            try:
                data, addr = self.sock.recvfrom(2048)
                
                if len(data) < self.HEADER_SIZE:
                    continue
                    
                header = struct.unpack(self.HEADER_FORMAT, data[:self.HEADER_SIZE])
                packet_id = header[5]
                player_car_index = header[10]
                
                # Packet ID 6 is "Car Telemetry"
                if packet_id == 6:
                    offset = self.HEADER_SIZE + (player_car_index * self.CAR_TELEMETRY_SIZE)
                    
                    if offset + self.CAR_TELEMETRY_SIZE <= len(data):
                        car_data = struct.unpack(self.CAR_TELEMETRY_FORMAT, data[offset:offset + self.CAR_TELEMETRY_SIZE])
                        
                        speed = car_data[0]       # uint16, km/h
                        throttle = car_data[1]    # float, 0.0 to 1.0
                        brake = car_data[3]       # float, 0.0 to 1.0
                        gear = car_data[5]        # int8, -1=Reverse, 0=Neutral, 1-8=Gears
                        engine_rpm = car_data[6]  # uint16
                        
                        physics = GamePhysics(
                            game_name='F1 25',
                            gear=int(gear),
                            rpms=int(engine_rpm),
                            speed_kmh=float(speed),
                            gas=float(throttle),
                            brake=float(brake)
                        )
                        
                        with self.data_lock:
                            self.last_data = physics
                            
            except socket.timeout:
                pass
            except Exception as e:
                logger.error(f"Error in F1 UDP listener: {e}")
                time.sleep(0.1)
                
    def read_physics(self) -> Optional[GamePhysics]:
        with self.data_lock:
            return self.last_data

class LMUTelemetryReader:
    """
    Le Mans Ultimate telemetry reader using pyLMUSharedMemory.
    """
    def __init__(self):
        self.lmu = None
        self.connected = False
        
    def connect(self) -> bool:
        try:
            from pylmusharedmemory import lmu_mmap, lmu_data
            # access_mode 0 creates a safe copy buffer to avoid data desync while reading
            self.lmu = lmu_mmap.MMapControl("LMU_Data", lmu_data.LMUObjectOut)
            self.lmu.create(access_mode=0)
            self.connected = True
            logger.info("Successfully connected to Le Mans Ultimate shared memory")
            return True
        except ImportError:
            logger.error("pyLMUSharedMemory not found. Please ensure it is in the python-server directory.")
            return False
        except Exception as e:
            logger.error(f"Failed to connect to Le Mans Ultimate shared memory: {e}")
            self.lmu = None
            self.connected = False
            return False
            
    def disconnect(self):
        if self.lmu:
            try:
                self.lmu.close()
                logger.info("Disconnected from Le Mans Ultimate shared memory")
            except Exception as e:
                logger.error(f"Error disconnecting from Le Mans Ultimate: {e}")
            finally:
                self.lmu = None
                self.connected = False
                
    def read_physics(self) -> Optional[GamePhysics]:
        if not self.connected or not self.lmu:
            return None
            
        try:
            self.lmu.update() # Fetch latest data from memory
            
            telemetry_data = self.lmu.data.telemetry
            
            # Check if the player is actually in a vehicle
            if telemetry_data.playerHasVehicle:
                player_idx = telemetry_data.playerVehicleIdx
                player_telem = telemetry_data.telemInfo[player_idx]
                
                # 1. Gear
                gear = player_telem.mGear
                
                # 2. RPM
                rpm = player_telem.mEngineRPM
                
                # 3. Speed (mLocalVel is in m/s, multiply by 3.6 for km/h)
                vel_x = player_telem.mLocalVel.x
                vel_y = player_telem.mLocalVel.y
                vel_z = player_telem.mLocalVel.z
                speed_ms = math.sqrt(vel_x**2 + vel_y**2 + vel_z**2)
                speed_kmh = speed_ms * 3.6
                
                # 4. Pedals
                gas = player_telem.mUnfilteredThrottle
                brake = player_telem.mUnfilteredBrake
                
                return GamePhysics(
                    game_name='Le Mans Ultimate',
                    gear=int(gear),
                    rpms=int(rpm),
                    speed_kmh=float(speed_kmh),
                    gas=float(gas),
                    brake=float(brake)
                )
            return None
        except Exception as e:
            logger.error(f"Error reading Le Mans Ultimate telemetry: {e}")
            return None

class GameTelemetryReader:
    """
    Smart telemetry reader that automatically detects the running game
    and reads its telemetry.
    """
    def __init__(self):
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.current_game: Optional[str] = None
        self.ac_reader = ACTelemetryReader()
        self.iracing_reader = IRacingTelemetryReader()
        self.raceroom_reader = RaceRoomTelemetryReader()
        self.f1_reader = F1TelemetryReader()
        self.lmu_reader = LMUTelemetryReader()
        self.data_lock = threading.RLock()
        self.current_data: Optional[GamePhysics] = None
        
    def connect(self) -> bool:
        """
        Detect the running game and connect to its telemetry.
        """
        game = detect_running_game()
        if not game:
            logger.debug("No supported game detected.")
            return False
            
        self.current_game = game
        logger.info(f"Detected game: {self.current_game}")
        
        if self.current_game == 'Assetto Corsa':
            return self.ac_reader.connect()
        elif self.current_game == 'iRacing':
            return self.iracing_reader.connect()
        elif self.current_game == 'RaceRoom':
            return self.raceroom_reader.connect()
        elif self.current_game == 'F1 25':
            return self.f1_reader.connect()
        elif self.current_game == 'Le Mans Ultimate':
            return self.lmu_reader.connect()
        else:
            logger.info(f"Telemetry for {self.current_game} is not fully implemented yet, but game was detected.")
            return True
            
    def disconnect(self):
        if self.current_game == 'Assetto Corsa':
            self.ac_reader.disconnect()
        elif self.current_game == 'iRacing':
            self.iracing_reader.disconnect()
        elif self.current_game == 'RaceRoom':
            self.raceroom_reader.disconnect()
        elif self.current_game == 'F1 25':
            self.f1_reader.disconnect()
        elif self.current_game == 'Le Mans Ultimate':
            self.lmu_reader.disconnect()
        self.current_game = None
        
    def read_physics(self) -> Optional[GamePhysics]:
        if not self.current_game:
            return None
            
        physics = None
        if self.current_game == 'Assetto Corsa':
            ac_data = self.ac_reader.read_physics()
            if ac_data:
                physics = GamePhysics(
                    game_name=self.current_game,
                    gear=ac_data.gear,
                    rpms=ac_data.rpms,
                    speed_kmh=ac_data.speed_kmh,
                    gas=ac_data.gas,
                    brake=ac_data.brake
                )
        elif self.current_game == 'iRacing':
            physics = self.iracing_reader.read_physics()
        elif self.current_game == 'RaceRoom':
            physics = self.raceroom_reader.read_physics()
        elif self.current_game == 'F1 25':
            physics = self.f1_reader.read_physics()
        elif self.current_game == 'Le Mans Ultimate':
            physics = self.lmu_reader.read_physics()
        else:
            # Mock data for other games until implemented
            physics = GamePhysics(
                game_name=self.current_game,
                gear=1,
                rpms=0,
                speed_kmh=0.0
            )
            
        if physics:
            with self.data_lock:
                self.current_data = physics
            return physics
            
        return None

    def start_polling(self, callback: Optional[Callable[[GamePhysics], None]] = None, 
                     poll_rate: float = 0.016) -> bool:
        if self.running:
            return False
            
        if not self.connect():
            return False
            
        self.running = True
        self.thread = threading.Thread(
            target=self._polling_loop,
            args=(callback, poll_rate),
            daemon=True
        )
        self.thread.start()
        return True
        
    def stop_polling(self):
        if not self.running:
            return
        self.running = False
        if self.thread:
            self.thread.join(timeout=2.0)
        self.disconnect()
        
    def _polling_loop(self, callback: Optional[Callable], poll_rate: float):
        while self.running:
            try:
                # Periodically re-check if game is still running or changed
                # We do this every few seconds, not every frame
                if int(time.time()) % 5 == 0:
                    current = detect_running_game()
                    if current != self.current_game:
                        logger.info(f"Game changed from {self.current_game} to {current}")
                        self.disconnect()
                        if current:
                            self.current_game = current
                            if self.current_game == 'Assetto Corsa':
                                self.ac_reader.connect()
                            elif self.current_game == 'iRacing':
                                self.iracing_reader.connect()
                            elif self.current_game == 'RaceRoom':
                                self.raceroom_reader.connect()
                            elif self.current_game == 'F1 25':
                                self.f1_reader.connect()
                            elif self.current_game == 'Le Mans Ultimate':
                                self.lmu_reader.connect()
                        else:
                            self.current_game = None
                
                data = self.read_physics()
                if data and callback:
                    callback(data)
                    
                time.sleep(poll_rate)
            except Exception as e:
                logger.error(f"Error in game telemetry polling loop: {e}")
                time.sleep(1)


# Simple example usage
def example_callback(data: GamePhysics):
    """Example callback function to display telemetry"""
    print(f"Gear: {data.gear:>2} | "
          f"RPM: {data.rpms:>5} | "
          f"Speed: {data.speed_kmh:>6.1f} km/h | "
          f"Gas: {data.gas:>4.1%} | "
          f"Brake: {data.brake:>4.1%}")


def demo():
    """Demo function to test the telemetry reader"""
    print("=== Game Telemetry Reader ===")
    print("Make sure a supported game is running!")
    print("Press Ctrl+C to stop\n")
    
    reader = GameTelemetryReader()
    
    # Start polling at 60fps with callback
    if reader.start_polling(callback=example_callback, poll_rate=0.016):
        try:
            # Keep main thread alive
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nStopping...")
    else:
        print("Failed to start telemetry reader. Make sure:")
        print("1. A supported game is running")
        print("2. You're in a session (not main menu)")
        print("3. Python is running with admin privileges (if needed)")
    
    reader.stop_polling()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    demo()
