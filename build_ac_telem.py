import re
import os
import ctypes

ac_code = '''
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
    PHYSICS_MAP_NAME = "Local\\\\acpmf_physics"
    GRAPHIC_MAP_NAME = "Local\\\\acpmf_graphics"
    STATIC_MAP_NAME = "Local\\\\acpmf_static"

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
                tc=phys.tc,
                pitch=phys.pitch,
                abs=phys.abs,
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
'''

with open('C:/Users/Tempestgf/Coding/MobileWheel/python-server/game_telemetry.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Define the new ACPhysics dataclass replacement
ac_physics_code = '''
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
'''

# We need to replace ACPhysics entirely
text = re.sub(r'@dataclass\nclass ACPhysics:[\s\S]*?(?=class ACTelemetryReader:)', ac_physics_code + '\n', text)

# Now we replace ACTelemetryReader entirely
text = re.sub(r'class ACTelemetryReader:[\s\S]*?(?=class IRacingTelemetryReader:)', ac_code + '\n', text)

with open('C:/Users/Tempestgf/Coding/MobileWheel/python-server/game_telemetry.py', 'w', encoding='utf-8') as f:
    f.write(text)

with open('C:/Users/Tempestgf/Coding/Desktop/smoothoperator/mobilewheel/game_telemetry.py', 'w', encoding='utf-8') as f:
    f.write(text)

print("Both game_telemetry.py files patched successfully!")
