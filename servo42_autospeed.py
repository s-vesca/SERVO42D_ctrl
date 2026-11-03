import serial
import time

PORTA = "COM11"
BAUD = 38400
SLAVE = 0x01

def send_raw(ser, data):
    """Invia il pacchetto calcolando il checksum in coda e legge la risposta."""
    crc = sum(data) & 0xFF
    packet = bytearray(data + [crc])
    ser.write(packet)
    time.sleep(0.02)
    rx = ser.read(16)
    return rx

def set_speed(ser, speed_sp):
    """Imposta la velocità applicando la logica di direzione e byte."""
    if speed_sp > ((2**12) - 1):
        speed_sp = 2**12 - 1
    if speed_sp < -(2**12):
        speed_sp = -2**12

    dir = 0 if speed_sp > 0 else 1
    abs_speed = abs(speed_sp)
    
    speed_byte1 = int(abs_speed / 256)
    if dir:
        speed_byte1 = 0x80 | speed_byte1

    speed_byte2 = int(abs_speed % 256)
    
    # Valore di accelerazione fluido
    acc_byte = 0x20  

    packet_data = [0xFA, SLAVE, 0xF6, speed_byte1, speed_byte2, acc_byte]
    send_raw(ser, packet_data)

try:
    with serial.Serial(PORTA, BAUD, timeout=1) as ser:
        print("--- Enable CMD ---")
        send_raw(ser, [0xFA, SLAVE, 0xF3, 0x01])
        time.sleep(0.5)

        print("\nAvvio profilo triangolare: da -100 RPM a +100 RPM in modo continuo. Ctrl+C per fermare.\n")

        target_max = 100
        step = 5        # Incremento più piccolo per una transizione molto fluida a basse velocità
        delay = 0.05    # Ritardo tra uno step e l'altro

        while True:
            # 1. Rampa in salita: da -100 a +100 RPM
            print("--- Rampa verso +100 RPM ---")
            for current_speed in range(-target_max, target_max + 1, step):
                set_speed(ser, current_speed)
                time.sleep(delay)

            # 2. Rampa in discesa: da +100 a -100 RPM
            print("--- Rampa verso -100 RPM ---")
            for current_speed in range(target_max, -(target_max + 1), -step):
                set_speed(ser, current_speed)
                time.sleep(delay)

except KeyboardInterrupt:
    print("\nInterrotto dall'utente. Arresto del motore...")
    try:
        with serial.Serial(PORTA, BAUD, timeout=1) as ser:
            set_speed(ser, 0)
            time.sleep(0.1)
    except:
        pass
    print("Connessione chiusa.")
except Exception as e:
    print(f"Errore: {e}")