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
    """Data class containing advanced physics telemetry from Assetto Corsa"""
    packet_id: int
    gas: float
    brake: float
    fuel: float
    gear: int
    rpms: int
    steer_angle: float
    speed_kmh: float
    velocity_x: float; velocity_y: float; velocity_z: float;
    acc_g_x: float; acc_g_y: float; acc_g_z: float;
    wheel_slip: tuple; wheel_load: tuple; wheels_pressure: tuple;
    wheel_angular_speed: tuple; tyre_wear: tuple; tyre_dirty_level: tuple;
    tyre_core_temperature: tuple
    drs: float
    tc: float
    pitch: float
    abs: float
    clutch: float
    brake_temp: tuple
    water_temp: float
    brake_bias: float
    max_rpm: int
    position: int
    lap_time: str
    best_lap: str

    def to_json_payload(self) -> dict:
        return {
            "game_name": "Assetto Corsa",
            "speed_kmh": self.speed_kmh,
            "gear": self.gear,
            "rpm": self.rpms,
            "max_rpm": self.max_rpm,
            "gas": self.gas,
            "brake": self.brake,
            "fuel": self.fuel,
            "clutch": self.clutch,
            "steer_angle": self.steer_angle,
            "tc": self.tc,
            "abs": self.abs,
            "drs": self.drs,
            "tyre_temps": self.tyre_core_temperature,
            "tyre_pressures": self.wheels_pressure,
            "brake_temps": self.brake_temp,
            "water_temp": self.water_temp,
            "brake_bias": self.brake_bias,
            "position": self.position,
            "lap_time": str(self.lap_time),
            "best_lap": str(self.best_lap)
        }


# --- Comprehensive AC Telemetry Types ---
import ctypes

class SPageFilePhysics(ctypes.Structure):
    _pack_ = 4
    _fields_ = [
        ("packetId", ctypes.c_int32),
        ("gas", ctypes.c_float),
        ("brake", ctypes.c_float),
        ("fuel", ctypes.c_float),
        ("gear", ctypes.c_int32),
        ("rpms", ctypes.c_int32),
        ("steerAngle", ctypes.c_float),
        ("speedKmh", ctypes.c_float),
        ("velocity", ctypes.c_float * 3),
        ("accG", ctypes.c_float * 3),
        ("wheelSlip", ctypes.c_float * 4),
        ("wheelLoad", ctypes.c_float * 4),
        ("wheelsPressure", ctypes.c_float * 4),
        ("wheelAngularSpeed", ctypes.c_float * 4),
        ("tyreWear", ctypes.c_float * 4),
        ("tyreDirtyLevel", ctypes.c_float * 4),
        ("tyreCoreTemperature", ctypes.c_float * 4),
        ("camberRAD", ctypes.c_float * 4),
        ("suspensionTravel", ctypes.c_float * 4),
        ("drs", ctypes.c_float),
        ("tc", ctypes.c_float),
        ("heading", ctypes.c_float),
        ("pitch", ctypes.c_float),
        ("roll", ctypes.c_float),
        ("cgHeight", ctypes.c_float),
        ("carDamage", ctypes.c_float * 5),
        ("numberOfTyresOut", ctypes.c_int32),
        ("pitLimiterOn", ctypes.c_int32),
        ("abs", ctypes.c_float),
        ("kersCharge", ctypes.c_float),
        ("kersInput", ctypes.c_float),
        ("autoShifterOn", ctypes.c_int32),
        ("rideHeight", ctypes.c_float * 2),
        ("turboBoost", ctypes.c_float),
        ("ballast", ctypes.c_float),
        ("airDensity", ctypes.c_float),
        ("airTemp", ctypes.c_float),
        ("roadTemp", ctypes.c_float),
        ("localAngularVel", ctypes.c_float * 3),
        ("finalFF", ctypes.c_float),
        ("performanceMeter", ctypes.c_float),
        ("engineBrake", ctypes.c_int32),
        ("ersRecoveryLevel", ctypes.c_int32),
        ("ersPowerLevel", ctypes.c_int32),
        ("ersHeatCharging", ctypes.c_int32),
        ("ersIsCharging", ctypes.c_int32),
        ("kersCurrentKJ", ctypes.c_float),
        ("drsAvailable", ctypes.c_int32),
        ("drsEnabled", ctypes.c_int32),
        ("brakeTemp", ctypes.c_float * 4),
        ("clutch", ctypes.c_float),
        ("tyreTempI", ctypes.c_float * 4),
        ("tyreTempM", ctypes.c_float * 4),
        ("tyreTempO", ctypes.c_float * 4),
        ("isAIControlled", ctypes.c_int32),
        ("tyreContactPoint", ctypes.c_float * 4 * 3),
        ("tyreContactNormal", ctypes.c_float * 4 * 3),
        ("tyreContactHeading", ctypes.c_float * 4 * 3),
        ("brakeBias", ctypes.c_float),
        ("localVelocity", ctypes.c_float * 3),
        ("P2PActivations", ctypes.c_int32),
        ("P2PStatus", ctypes.c_int32),
        ("currentMaxRpm", ctypes.c_int32),
        ("mz", ctypes.c_float * 4),
        ("fx", ctypes.c_float * 4),
        ("fy", ctypes.c_float * 4),
        ("slipRatio", ctypes.c_float * 4),
        ("slipAngle", ctypes.c_float * 4),
        ("tcinAction", ctypes.c_int32),
        ("absInAction", ctypes.c_int32),
        ("suspensionDamage", ctypes.c_float * 4),
        ("tyreTemp", ctypes.c_float * 4),
        ("waterTemp", ctypes.c_float),
    ]

class SPageFileGraphic(ctypes.Structure):
    _pack_ = 4
    _fields_ = [
        ("packetId", ctypes.c_int32),
        ("status", ctypes.c_int32),
        ("session", ctypes.c_int32),
        ("currentTime", ctypes.c_wchar * 15),
        ("lastTime", ctypes.c_wchar * 15),
        ("bestTime", ctypes.c_wchar * 15),
        ("split", ctypes.c_wchar * 15),
        ("completedLaps", ctypes.c_int32),
        ("position", ctypes.c_int32),
        ("iCurrentTime", ctypes.c_int32),
        ("iLastTime", ctypes.c_int32),
        ("iBestTime", ctypes.c_int32),
        ("sessionTimeLeft", ctypes.c_float),
        ("distanceTraveled", ctypes.c_float),
        ("isInPit", ctypes.c_int32),
        ("currentSectorIndex", ctypes.c_int32),
        ("lastSectorTime", ctypes.c_int32),
        ("numberOfLaps", ctypes.c_int32),
        ("tyreCompound", ctypes.c_wchar * 33),
        ("replayTimeMultiplier", ctypes.c_float),
        ("normalizedCarPosition", ctypes.c_float),
        ("activeCars", ctypes.c_int32),
        ("carCoordinates", ctypes.c_float * 60 * 3),
        ("carID", ctypes.c_int32 * 60),
        ("playerCarID", ctypes.c_int32),
        ("penaltyTime", ctypes.c_float),
        ("flag", ctypes.c_int32),
        ("penalty", ctypes.c_int32),
        ("idealLineOn", ctypes.c_int32),
        ("isInPitLane", ctypes.c_int32),
        ("surfaceGrip", ctypes.c_float),
        ("mandatoryPitDone", ctypes.c_int32),
        ("windSpeed", ctypes.c_float),
        ("windDirection", ctypes.c_float),
        ("isSetupMenuVisible", ctypes.c_int32),
        ("mainDisplayIndex", ctypes.c_int32),
        ("secondaryDisplayIndex", ctypes.c_int32),
        ("TC", ctypes.c_int32),
        ("TCCut", ctypes.c_int32),
        ("EngineMap", ctypes.c_int32),
        ("ABS", ctypes.c_int32),
        ("ABSM", ctypes.c_int32),
        ("fuelXLap", ctypes.c_float),
        ("isTimedRace", ctypes.c_int32),
        ("hasExtraLap", ctypes.c_int32),
        ("carSkin", ctypes.c_wchar * 33),
        ("shouldPosition", ctypes.c_int32),
        ("direction", ctypes.c_int32),
    ]

class SPageFileStatic(ctypes.Structure):
    _pack_ = 4
    _fields_ = [
        ("smVersion", ctypes.c_wchar * 15),
        ("acVersion", ctypes.c_wchar * 15),
        ("numberOfSessions", ctypes.c_int32),
        ("numCars", ctypes.c_int32),
        ("carModel", ctypes.c_wchar * 33),
        ("track", ctypes.c_wchar * 33),
        ("playerName", ctypes.c_wchar * 33),
        ("playerSurname", ctypes.c_wchar * 33),
        ("playerNick", ctypes.c_wchar * 33),
        ("sectorCount", ctypes.c_int32),
        ("maxTorque", ctypes.c_float),
        ("maxPower", ctypes.c_float),
        ("maxRpm", ctypes.c_int32),
        ("maxFuel", ctypes.c_float),
        ("suspensionMaxTravel", ctypes.c_float * 4),
        ("tyreRadius", ctypes.c_float * 4),
        ("maxTurboBoost", ctypes.c_float),
        ("deprecated_1", ctypes.c_float),
        ("deprecated_2", ctypes.c_float),
        ("penaltiesEnabled", ctypes.c_int32),
        ("aidFuelRate", ctypes.c_float),
        ("aidTireRate", ctypes.c_float),
        ("aidMechanicalDamage", ctypes.c_float),
        ("allowTyreBlankets", ctypes.c_int32),
        ("aidStability", ctypes.c_float),
        ("aidAutoClutch", ctypes.c_int32),
        ("aidAutoBlip", ctypes.c_int32),
    ]

class ACTelemetryReader:
    """
    Professional Assetto Corsa telemetry reader using shared memory.
    Reads physics, graphics, and static to provide full Telemetry.
    """
    PHYSICS_MAP_NAME = r"Local\acpmf_physics"
    GRAPHIC_MAP_NAME = r"Local\acpmf_graphic"
    STATIC_MAP_NAME = r"Local\acpmf_static"

    def __init__(self):
        self._physics_mmap = None
        self._graphic_mmap = None
        self._static_mmap = None
        self.connected = False
        self._lock = threading.Lock()
        self._stop_event = threading.Event()
        self._callbacks = []

    def connect(self) -> bool:
        with self._lock:
            if self.connected:
                return True
            try:
                self._physics_mmap = mmap.mmap(-1, ctypes.sizeof(SPageFilePhysics), self.PHYSICS_MAP_NAME)
                self._graphic_mmap = mmap.mmap(-1, ctypes.sizeof(SPageFileGraphic), self.GRAPHIC_MAP_NAME)
                self._static_mmap = mmap.mmap(-1, ctypes.sizeof(SPageFileStatic), self.STATIC_MAP_NAME)
                self.connected = True
                logging.info("Connected to Assetto Corsa shared memory")
                return True
            except FileNotFoundError:
                self.disconnect()
                return False
            except Exception as e:
                logging.error(f"Error connecting to AC shared memory: {e}")
                self.disconnect()
                return False

    def disconnect(self):
        with self._lock:
            self.connected = False
            for mapped in (self._physics_mmap, self._graphic_mmap, self._static_mmap):
                if mapped:
                    try:
                        mapped.close()
                    except:
                        pass
            self._physics_mmap = None
            self._graphic_mmap = None
            self._static_mmap = None

    def is_running(self) -> bool:
        return self.connected

    def read_physics(self):
        if not self.connected:
            return None
        try:
            self._physics_mmap.seek(0)
            phys_data = self._physics_mmap.read(ctypes.sizeof(SPageFilePhysics))
            phys = SPageFilePhysics.from_buffer_copy(phys_data)

            self._graphic_mmap.seek(0)
            graph_data = self._graphic_mmap.read(ctypes.sizeof(SPageFileGraphic))
            graph = SPageFileGraphic.from_buffer_copy(graph_data)

            self._static_mmap.seek(0)
            stat_data = self._static_mmap.read(ctypes.sizeof(SPageFileStatic))
            stat = SPageFileStatic.from_buffer_copy(stat_data)

            return ACPhysics(
                packet_id=phys.packetId,
                gas=phys.gas,
                brake=phys.brake,
                fuel=phys.fuel,
                gear=phys.gear,
                rpms=phys.rpms,
                steer_angle=phys.steerAngle,
                speed_kmh=phys.speedKmh,
                velocity_x=phys.velocity[0],
                velocity_y=phys.velocity[1],
                velocity_z=phys.velocity[2],
                acc_g_x=phys.accG[0],
                acc_g_y=phys.accG[1],
                acc_g_z=phys.accG[2],
                wheel_slip=tuple(phys.wheelSlip),
                wheel_load=tuple(phys.wheelLoad),
                wheels_pressure=tuple(phys.wheelsPressure),
                wheel_angular_speed=tuple(phys.wheelAngularSpeed),
                tyre_wear=tuple(phys.tyreWear),
                tyre_dirty_level=tuple(phys.tyreDirtyLevel),
                tyre_core_temperature=tuple(phys.tyreCoreTemperature),
                drs=phys.drs,
                tc=float(graph.TC),
                pitch=phys.pitch,
                abs=float(graph.ABS),
                clutch=phys.clutch,
                brake_temp=tuple(phys.brakeTemp),
                water_temp=phys.waterTemp,
                brake_bias=phys.brakeBias,
                max_rpm=stat.maxRpm if stat.maxRpm > 0 else phys.currentMaxRpm,
                position=graph.position,
                lap_time=graph.currentTime,
                best_lap=graph.bestTime
            )
        except Exception as e:
            # AC closed or mmap failure
            self.disconnect()
            return None

    def start_polling(self, callback_rate_hz: int = 60):
        # same as before, simplified for placeholder
        pass
    def stop_polling(self):
        pass
    def register_callback(self, callback):
        pass
    def unregister_callback(self, callback):
        pass

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
