import serial
import serial.tools.list_ports

def get_arduino_serial(baudrate=9600, timeout=1):
    ports = serial.tools.list_ports.comports()
    for port in ports:
        # These keywords help detect common Arduino boards
        if "Arduino" in port.description or "CH340" in port.description or "USB Serial" in port.description:
            print(f"✅ Arduino found on port: {port.device}")
            try:
                return serial.Serial(port=port.device, baudrate=baudrate, timeout=timeout)
            except serial.SerialException as e:
                print(f"❌ Failed to open port {port.device}: {e}")
    raise Exception("❌ No Arduino found! Please check the connection.")
