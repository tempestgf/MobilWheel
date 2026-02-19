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

# Configure logging
logger = logging.getLogger(__name__)


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


# Simple example usage
def example_callback(data: ACPhysics):
    """Example callback function to display telemetry"""
    print(f"Gear: {data.gear:>2} | "
          f"RPM: {data.rpms:>5} | "
          f"Speed: {data.speed_kmh:>6.1f} km/h | "
          f"Gas: {data.gas:>4.1%} | "
          f"Brake: {data.brake:>4.1%}")


def demo():
    """Demo function to test the telemetry reader"""
    print("=== Assetto Corsa Telemetry Reader ===")
    print("Make sure AC is running and you're in a session!")
    print("Press Ctrl+C to stop\n")
    
    reader = ACTelemetryReader()
    
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
        print("1. Assetto Corsa is running")
        print("2. You're in a session (not main menu)")
        print("3. Python is running with admin privileges (if needed)")
    
    reader.stop_polling()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    demo()
