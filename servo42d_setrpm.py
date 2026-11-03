import serial
import time

PORTA = "COM11"
BAUD = 38400
SLAVE = 0x01

def send_raw(ser, data):
    crc = sum(data) & 0xFF
    packet = bytearray(data + [crc])
    print(f"TX: {packet.hex().upper()}")
    ser.write(packet)
    time.sleep(0.05)
    rx = ser.read(16)
    print(f"RX: {rx.hex().upper()}\n")
    return rx

try:
    with serial.Serial(PORTA, BAUD, timeout=1) as ser:
        speed_sp = int(input("Enter Speed set-point [RPM]: "))
        if(speed_sp > ((2**12) - 1)):
            speed_sp = 2**12 - 1

        if(speed_sp < -(2**12)):
            speed_sp = -2**12
        

        print(f"speed setpoint = {speed_sp}")

        if(speed_sp > 0):
            dir = 0
        else:
            dir = 1

        speed_cmd_head = [0xFA, SLAVE, 0xF6]
        speed_byte1 = (int)(abs(speed_sp) / 256)

        if (dir):
            speed_byte1 = 0x80 | speed_byte1

        speed_byte2 = (int)(abs(speed_sp) % 256)

        acc_byte = 0xF0

        print(f"Byte1: {speed_byte1}")
        print(f"Byte2: {speed_byte2}")
        print("--- Enable CMD ---")

        # Comando FA [Addr] 31 [CRC]
        send_raw(ser, [0xFA, SLAVE, 0xF3, 0x01])

        print("--- Speed CMD ---")
        send_raw(ser, [0xFA, SLAVE, 0xF6, speed_byte1,speed_byte2, acc_byte])

except Exception as e:
    print(f"Errore: {e}")