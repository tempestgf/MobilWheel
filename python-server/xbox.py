import socket
import ctypes
import time
import struct
import os
import sys
import platform
import logging
from collections import deque
import threading
import netifaces
import signal
import tkinter as tk

# Configuración del registro
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Detect OS
IS_WINDOWS = platform.system() == 'Windows'
IS_LINUX = platform.system() == 'Linux'

# Virtual joystick interface abstraction
vjoy = None
uinput_devices = {}

if IS_WINDOWS:
    # Windows vJoy setup
    is_64bits = struct.calcsize("P") * 8 == 64
    dll_path_64 = './vJoy/x64/vJoyInterface.dll'
    dll_path_32 = './vJoy/x86/vJoyInterface.dll'
    dll_path = dll_path_64 if is_64bits else dll_path_32

    if not os.path.isfile(dll_path):
        raise FileNotFoundError(f"Could not find module '{dll_path}'")

    vjoy = ctypes.WinDLL(dll_path)

    VJD_STAT_OWN = 0
    VJD_STAT_FREE = 1
    VJD_STAT_BUSY = 2
    VJD_STAT_MISS = 3
    VJD_STAT_UNKN = 4

    vjoy.AcquireVJD.argtypes = [ctypes.c_uint]
    vjoy.AcquireVJD.restype = ctypes.c_bool

    vjoy.RelinquishVJD.argtypes = [ctypes.c_uint]
    vjoy.RelinquishVJD.restype = ctypes.c_bool

    vjoy.SetBtn.argtypes = [ctypes.c_bool, ctypes.c_uint, ctypes.c_uint]
    vjoy.SetBtn.restype = ctypes.c_bool

    vjoy.SetAxis.argtypes = [ctypes.c_long, ctypes.c_uint, ctypes.c_uint]
    vjoy.SetAxis.restype = ctypes.c_bool

    vjoy.GetVJDStatus.argtypes = [ctypes.c_uint]
    vjoy.GetVJDStatus.restype = ctypes.c_int

elif IS_LINUX:
    # Linux uinput setup
    try:
        import evdev
        from evdev import UInput, AbsInfo, ecodes
        logging.info("Using evdev for Linux virtual gamepad")
    except ImportError:
        logging.error("evdev not installed. Install with: pip install evdev")
        raise

available_devices = [1, 2]
device_lock = threading.Lock()
device_states = {}

# Keep virtual devices alive across client reconnects
KEEP_DEVICE_ON_DISCONNECT = True
acquired_devices = set()

command_map = {
    'D': 'left_top',
    'E': 'left_bottom',
    'F': 'right_top',
    'G': 'right_bottom',
    'VOLUME_UP': 'volume_up',
    'VOLUME_DOWN': 'volume_down',
    'A': 'steering',
    'B': 'accelerate',
    'C': 'brake'
}

def acquire_vjd(device_id):
    """Acquire virtual joystick device (cross-platform)"""
    if IS_WINDOWS:
        return _acquire_vjd_windows(device_id)
    elif IS_LINUX:
        return _acquire_vjd_linux(device_id)
    return False

def _acquire_vjd_windows(device_id):
    """Windows vJoy device acquisition"""
    if device_id in acquired_devices:
        return True
    attempts = 5
    while attempts > 0:
        status = vjoy.GetVJDStatus(device_id)
        if status == VJD_STAT_FREE or status == VJD_STAT_OWN:
            if vjoy.AcquireVJD(device_id):
                logging.info(f"Device {device_id} acquired successfully.")
                set_axis(device_id, 0x31, 16384)
                acquired_devices.add(device_id)
                return True
            else:
                logging.error(f"Failed to acquire device {device_id}.")
                return False
        elif status == VJD_STAT_BUSY or status == VJD_STAT_MISS:
            logging.warning(f"Device {device_id} is in an unexpected state (Status: {status}). Forcing release...")
            relinquish_vjd(device_id)
            time.sleep(0.5)
            attempts -= 1
        else:
            logging.warning(f"Device {device_id} is not free. Status: {status}. Retrying in 0.5s...")
            time.sleep(0.5)
            attempts -= 1
    logging.error(f"Failed to acquire device {device_id} after multiple attempts.")
    return False

def _acquire_vjd_linux(device_id):
    """Linux uinput device creation"""
    try:
        if device_id in uinput_devices:
            acquired_devices.add(device_id)
            return True
        # Define capabilities for a racing wheel
        cap = {
            ecodes.EV_KEY: [
                ecodes.BTN_TRIGGER,  # Button 1
                ecodes.BTN_THUMB,    # Button 2
                ecodes.BTN_THUMB2,   # Button 3
                ecodes.BTN_TOP,      # Button 4
                ecodes.BTN_TOP2,     # Button 5
                ecodes.BTN_PINKIE,   # Button 6
            ],
            ecodes.EV_ABS: [
                (ecodes.ABS_X, AbsInfo(value=16384, min=0, max=32767, fuzz=0, flat=0, resolution=0)),      # Steering
                (ecodes.ABS_Y, AbsInfo(value=16384, min=0, max=32767, fuzz=0, flat=0, resolution=0)),      # Accelerate
                (ecodes.ABS_Z, AbsInfo(value=16384, min=0, max=32767, fuzz=0, flat=0, resolution=0)),      # Brake
            ],
        }
        
        device = UInput(cap, name=f'MobileWheel-{device_id}', version=0x1)
        uinput_devices[device_id] = {
            'device': device,
            'buttons': {},
            'axes': {ecodes.ABS_X: 16384, ecodes.ABS_Y: 16384, ecodes.ABS_Z: 16384}
        }
        logging.info(f"Linux uinput device {device_id} created successfully.")
        return True
    except Exception as e:
        logging.error(f"Failed to create Linux uinput device {device_id}: {e}")
        return False

def relinquish_vjd(device_id):
    """Release virtual joystick device (cross-platform)"""
    if IS_WINDOWS:
        _relinquish_vjd_windows(device_id)
    elif IS_LINUX:
        _relinquish_vjd_linux(device_id)

def _relinquish_vjd_windows(device_id):
    """Windows vJoy device release"""
    try:
        for _ in range(3):
            if vjoy.RelinquishVJD(device_id):
                logging.info(f"Device {device_id} relinquished successfully.")
                time.sleep(0.1)
                break
            else:
                logging.warning(f"Attempt to relinquish device {device_id} failed. Retrying...")
                time.sleep(0.1)
    except Exception as e:
        logging.error(f"Failed to relinquish device {device_id}: {e}")

def _relinquish_vjd_linux(device_id):
    """Linux uinput device cleanup"""
    try:
        if device_id in uinput_devices:
            uinput_devices[device_id]['device'].close()
            del uinput_devices[device_id]
            logging.info(f"Linux uinput device {device_id} closed successfully.")
    except Exception as e:
        logging.error(f"Failed to close Linux uinput device {device_id}: {e}")

def set_button(device_id, button_id, state):
    """Set button state (cross-platform)"""
    if IS_WINDOWS:
        _set_button_windows(device_id, button_id, state)
    elif IS_LINUX:
        _set_button_linux(device_id, button_id, state)

def _set_button_windows(device_id, button_id, state):
    """Windows vJoy button"""
    if vjoy.SetBtn(state, device_id, button_id):
        logging.debug(f"Button {button_id} on device {device_id} set to {'pressed' if state else 'released'}.")
    else:
        logging.error(f"Failed to set button {button_id} on device {device_id}.")

def _set_button_linux(device_id, button_id, state):
    """Linux uinput button"""
    if device_id not in uinput_devices:
        logging.error(f"Device {device_id} not found")
        return
    
    # Map button IDs to evdev keycodes
    button_map = {
        1: ecodes.BTN_TRIGGER,
        2: ecodes.BTN_THUMB,
        3: ecodes.BTN_THUMB2,
        4: ecodes.BTN_TOP,
        5: ecodes.BTN_TOP2,
        6: ecodes.BTN_PINKIE,
    }
    
    if button_id in button_map:
        device = uinput_devices[device_id]['device']
        device.write(ecodes.EV_KEY, button_map[button_id], 1 if state else 0)
        device.syn()
        logging.debug(f"Button {button_id} on device {device_id} set to {'pressed' if state else 'released'}.")
    else:
        logging.error(f"Button {button_id} not mapped for Linux")

def set_axis(device_id, axis_id, value):
    """Set axis value (cross-platform)"""
    if IS_WINDOWS:
        _set_axis_windows(device_id, axis_id, value)
    elif IS_LINUX:
        _set_axis_linux(device_id, axis_id, value)

def _set_axis_windows(device_id, axis_id, value):
    """Windows vJoy axis"""
    if vjoy.SetAxis(value, device_id, axis_id):
        logging.debug(f"Axis {axis_id} on device {device_id} set to {value}.")
    else:
        logging.error(f"Failed to set axis {axis_id} on device {device_id}.")

def _set_axis_linux(device_id, axis_id, value):
    """Linux uinput axis"""
    if device_id not in uinput_devices:
        logging.error(f"Device {device_id} not found")
        return
    
    # Map vJoy axis IDs to evdev axis codes
    axis_map = {
        0x30: ecodes.ABS_X,  # Steering
        0x31: ecodes.ABS_Y,  # Accelerate
        0x32: ecodes.ABS_Z,  # Brake
    }
    
    if axis_id in axis_map:
        device = uinput_devices[device_id]['device']
        evdev_axis = axis_map[axis_id]
        device.write(ecodes.EV_ABS, evdev_axis, int(value))
        device.syn()
        uinput_devices[device_id]['axes'][evdev_axis] = int(value)
        logging.debug(f"Axis {axis_id} on device {device_id} set to {value}.")
    else:
        logging.error(f"Axis {axis_id} not mapped for Linux")

def map_value(value, in_min, in_max, out_min, out_max):
    # Asegura que el valor esté dentro del rango de entrada
    value = max(min(value, in_max), in_min)

    # Realiza el mapeo de valor
    return int((value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)

def process_critical_message(device_id, message, update_ui_callback=None):
    logging.info(f"Received critical message: {message}")

    if not message:
        logging.error("Error: Empty message received")
        return

    command = message.strip()
    logging.info(f"Processing command: {command}")

    if command in command_map:
        # Obtén el nombre del botón desde el mapa
        button_name = command_map[command].lower()
        logging.info(f"Mapped command: {command} to button {button_name}")

        # Si es necesario, maneja la conversión para vJoy
        button_id = {
            'D': 1,  # Left Top
            'E': 2,  # Left Bottom
            'F': 3,  # Right Top
            'G': 4,  # Right Bottom
            'VOLUME_UP': 5,  # Volume Up
            'VOLUME_DOWN': 6  # Volume Down
        }.get(command)

        if button_id is not None:
            logging.info(f"Button {button_id} will be pressed on device {device_id}")
            set_button(device_id, button_id, True)
            threading.Timer(0.05, set_button, args=(device_id, button_id, False)).start()
        
        # Actualiza la interfaz gráfica
        if update_ui_callback:
            logging.info(f"Calling UI callback for button: {button_name}")
            root = tk._default_root  # Asegúrate de que este sea el root de Tkinter
            root.after(0, update_ui_callback, button_name, True)
        else:
            logging.error("update_ui_callback is None!")
    else:
        logging.error(f"Error: Command {command} did not map to a valid button ID.")



def process_non_critical_message(device_id, message, update_ui_callback=None):
    state = device_states[device_id]
    logging.debug(f"Processing non-critical message: {message}")

    if not message:
        logging.error("Error: Empty message received")
        return

    parts = message.split(":")
    if len(parts) != 2:
        logging.error(f"Error: Incorrect message format. Parts: {parts}")
        return

    command, value = parts
    if command not in command_map:
        logging.error(f"Error: Unknown command identifier: {command}")
        return

    try:
        if command == 'A' and value is not None:  # Steering
            y = float(value)
            steering_value = map_value(y, -10.0, 10.0, 1, 32767)
            state['last_steering_value'] = steering_value
            set_axis(device_id, 0x30, int(steering_value))
            if update_ui_callback:
                update_ui_callback('steering', int(steering_value))
            logging.info(f"Steering value set: {int(steering_value)}")
        
        elif command in ['B', 'C'] and value.isdigit():  # Accelerate or Brake
            int_value = int(value)
            axis_value = map_value(int_value, 0, 100, 16384, 32767)
            if command == 'B':  # Acelerar
                set_axis(device_id, 0x31, axis_value)
                if update_ui_callback:
                    update_ui_callback('accelerate', int_value)
            elif command == 'C':  # Frenar
                set_axis(device_id, 0x32, axis_value)
                if update_ui_callback:
                    update_ui_callback('brake', int_value)
            logging.info(f"{command_map[command]} value mapped: {axis_value}")

    except ValueError as ve:
        logging.error(f"Error converting value: {ve}")


def handle_client(conn, addr, update_ui_callback=None):
    logging.info(f"handle_client called with update_ui_callback: {update_ui_callback is not None}")
    acquired_device_id = None

    if acquire_vjd(1):
        acquired_device_id = 1
    elif acquire_vjd(2):
        acquired_device_id = 2
    else:
        logging.error(f"No available devices for {addr}.")
        conn.close()
        return

    if acquired_device_id is not None:
        device_states[acquired_device_id] = {
            'critical_message_queue': deque(),
            'non_critical_message_queue': deque(),
            'last_steering_value': 16384,
            'threads': []
        }

        critical_thread = threading.Thread(target=handle_critical_messages, args=(acquired_device_id, update_ui_callback))
        non_critical_thread = threading.Thread(target=handle_non_critical_messages, args=(acquired_device_id, update_ui_callback))


        
        critical_thread.start()
        non_critical_thread.start()

        device_states[acquired_device_id]['threads'].extend([critical_thread, non_critical_thread])
    else:
        logging.error("No device_id available, cannot create threads.")
        conn.close()
        return

    try:
        with conn:
            buffer = ""
            # Set socket to non-blocking with timeout for responsiveness
            conn.settimeout(5.0)
            while not shutdown_event.is_set():
                try:
                    data = conn.recv(8192).decode('utf-8')
                    if not data:
                        break
                    buffer += data
                    while '\n' in buffer:
                        line, buffer = buffer.split('\n', 1)
                        message = line.strip()
                        if message:
                            parts = message.split(":")
                            command = parts[0] if len(parts) > 0 else None
                            if command in ['D', 'E', 'F', 'G', 'VOLUME_UP', 'VOLUME_DOWN']:
                                device_states[acquired_device_id]['critical_message_queue'].append(message)
                            else:
                                device_states[acquired_device_id]['non_critical_message_queue'].append(message)
                except socket.timeout:
                    # Check if still connected
                    if shutdown_event.is_set():
                        break
                    continue

    except Exception as e:
        logging.error(f"Error processing data: {e}")
    
    finally:
        logging.info(f"Connection with {addr} closed")
        try:
            for thread in device_states[acquired_device_id]['threads']:
                if thread.is_alive():
                    logging.info(f"Waiting for thread {thread.name} to finish...")
                    thread.join(timeout=1)

            if not KEEP_DEVICE_ON_DISCONNECT:
                relinquish_vjd(acquired_device_id)
        except Exception as e:
            logging.error(f"Error during cleanup: {e}")
        
        finally:
            with device_lock:
                if acquired_device_id in device_states:
                    del device_states[acquired_device_id]
                if acquired_device_id not in available_devices:
                    available_devices.append(acquired_device_id)
            
            try:
                conn.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            finally:
                conn.close()


def handle_critical_messages(device_id, update_ui_callback=None):
    logging.info(f"handle_critical_messages received update_ui_callback: {update_ui_callback is not None}")
    thread_name = threading.current_thread().name
    while not shutdown_event.is_set():
        if device_id not in device_states:
            logging.info(f"Exiting {thread_name} because the device state no longer exists.")
            break
        if device_states[device_id]['critical_message_queue']:
            msg = device_states[device_id]['critical_message_queue'].popleft()
            process_critical_message(device_id, msg, update_ui_callback)
        else:
            time.sleep(0.001)  # Reduced sleep time for faster response


def handle_non_critical_messages(device_id, update_ui_callback=None):
    thread_name = threading.current_thread().name
    while not shutdown_event.is_set():
        if device_id not in device_states:
            logging.info(f"Exiting {thread_name} because the device state no longer exists.")
            break
        processed_count = 0
        # Process more messages per batch for better throughput
        while device_states[device_id]['non_critical_message_queue'] and processed_count < 20:
            msg = device_states[device_id]['non_critical_message_queue'].popleft()
            process_non_critical_message(device_id, msg, update_ui_callback)
            processed_count += 1
        if processed_count == 0:
            time.sleep(0.001)  # Short sleep when no messages

def get_local_ip_for_client(client_ip):
    client_ip_prefix = '.'.join(client_ip.split('.')[:3]) + '.'
    for interface in netifaces.interfaces():
        addrs = netifaces.ifaddresses(interface)
        if netifaces.AF_INET in addrs:
            for addr in addrs[netifaces.AF_INET]:
                ip = addr['addr']
                if ip.startswith(client_ip_prefix):
                    return ip
    return None

shutdown_event = threading.Event()

def cleanup_devices():
    """Release all virtual devices on server shutdown."""
    for device_id in list(acquired_devices):
        try:
            relinquish_vjd(device_id)
        except Exception as e:
            logging.error(f"Failed to cleanup device {device_id}: {e}")
    acquired_devices.clear()

def signal_handler(sig, frame):
    logging.info("Interrupt received, shutting down...")
    shutdown_event.set()

signal.signal(signal.SIGINT, signal_handler)

def start_server(update_ui_callback=None):
    logging.info(f"start_server called with update_ui_callback: {update_ui_callback is not None}")

    TCP_IP = "0.0.0.0"
    TCP_PORT = 12345
    UDP_PORT = 12345

    # Reset shutdown event
    shutdown_event.clear()

    sock_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Enable socket reuse to avoid "Address already in use" errors
    sock_tcp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    if hasattr(socket, 'SO_REUSEPORT'):
        sock_tcp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    # Disable Nagle's algorithm for low latency
    sock_tcp.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    sock_tcp.bind((TCP_IP, TCP_PORT))
    sock_tcp.listen(5)
    logging.info(f"Listening for TCP connections on {TCP_IP}:{TCP_PORT}")

    sock_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock_udp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    if hasattr(socket, 'SO_REUSEPORT'):
        sock_udp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    sock_udp.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock_udp.bind((TCP_IP, UDP_PORT))
    logging.info(f"Listening for UDP broadcasts on {TCP_IP}:{UDP_PORT}")

    discovery_thread = threading.Thread(target=handle_discovery, args=(sock_udp,))
    discovery_thread.daemon = True
    discovery_thread.start()

    try:
        while not shutdown_event.is_set():
            sock_tcp.settimeout(1.0)
            try:
                conn, addr = sock_tcp.accept()
                # Set TCP_NODELAY on client connection for low latency
                conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                # Set socket buffer sizes for better performance
                conn.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 65536)
                conn.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 65536)
                client_thread = threading.Thread(target=handle_client, args=(conn, addr, update_ui_callback))
                client_thread.daemon = True
                client_thread.start()
            except socket.timeout:
                continue
    except KeyboardInterrupt:
        logging.info("Server is shutting down...")
    finally:
        shutdown_event.set()
        try:
            sock_tcp.shutdown(socket.SHUT_RDWR)
        except:
            pass
        sock_tcp.close()
        try:
            sock_udp.shutdown(socket.SHUT_RDWR)
        except:
            pass
        sock_udp.close()
        cleanup_devices()
        logging.info("Sockets closed. Server shut down.")

def handle_discovery(sock_udp):
    while not shutdown_event.is_set():
        try:
            sock_udp.settimeout(1.0)
            message, address = sock_udp.recvfrom(1024)
            if message.decode() == "DISCOVER_SERVER":
                server_ip = get_local_ip_for_client(address[0])
                if server_ip is None:
                    logging.error("No valid local IP found.")
                    continue
                response_message = f"{server_ip}:12345"
                sock_udp.sendto(response_message.encode(), address)
                logging.info(f"Responded to discovery from {address} with IP {server_ip}")
        except socket.timeout:
            continue
        except OSError:
            break
