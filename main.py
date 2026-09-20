import network
import time
import dht
import urequests
from machine import Pin, ADC, PWM, time_pulse_us

# =========================================================
# THINGSPEAK SETTINGS
# =========================================================

SSID = "Wokwi-GUEST"
PASSWORD = ""

CHANNEL_ID = "3498720"

WRITE_API_KEY = "YOUR_WRITE_API_KEY"
READ_API_KEY = "YOUR_READ_API_KEY"

THINGSPEAK_UPDATE_URL = "https://api.thingspeak.com/update"

THINGSPEAK_FIELD8_URL = (
    "https://api.thingspeak.com/channels/"
    + CHANNEL_ID
    + "/fields/8/last.txt"
    + "?api_key="
    + READ_API_KEY
)

# =========================================================
# GPIO SETTINGS
# =========================================================

DHT_PIN = 15

TRIG_PIN = 5
ECHO_PIN = 18

QUALITY_PIN = 34

RELAY_PIN = 23

GREEN_LED_PIN = 26
RED_LED_PIN = 25

BUZZER_PIN = 27

# =========================================================
# WATER LEVEL SETTINGS
# =========================================================

TANK_HEIGHT = 100.0

LOW_LEVEL = 20.0
HIGH_LEVEL = 80.0

POOR_QUALITY = 40.0

# =========================================================
# SENSOR SETUP
# =========================================================

dht_sensor = dht.DHT22(Pin(DHT_PIN))

TRIG = Pin(TRIG_PIN, Pin.OUT)
ECHO = Pin(ECHO_PIN, Pin.IN)

quality_sensor = ADC(Pin(QUALITY_PIN))
quality_sensor.atten(ADC.ATTN_11DB)

# =========================================================
# OUTPUT SETUP
# =========================================================

pump = Pin(RELAY_PIN, Pin.OUT)

green_led = Pin(GREEN_LED_PIN, Pin.OUT)
red_led = Pin(RED_LED_PIN, Pin.OUT)

buzzer = PWM(Pin(BUZZER_PIN))
buzzer.freq(1000)
buzzer.duty_u16(0)

# Start everything OFF
pump.value(0)
green_led.value(0)
red_led.value(0)
buzzer.duty_u16(0)

# =========================================================
# HC-SR04 DISTANCE FUNCTION
# =========================================================

def measure_distance():

    TRIG.value(0)
    time.sleep_us(2)

    TRIG.value(1)
    time.sleep_us(10)

    TRIG.value(0)

    duration = time_pulse_us(ECHO, 1, 30000)

    if duration < 0:
        return None

    return duration / 58.0


# =========================================================
# WATER LEVEL CALCULATION
# =========================================================

def calculate_water_level(distance):

    if distance is None:
        return None

    level = ((TANK_HEIGHT - distance) / TANK_HEIGHT) * 100.0

    if level < 0:
        level = 0

    if level > 100:
        level = 100

    return level


# =========================================================
# READ THINGSPEAK FIELD 8
# =========================================================

def read_pump_command():

    try:

        response = urequests.get(THINGSPEAK_FIELD8_URL)

        value = response.text.strip()

        response.close()

        command = int(value)

        if command in (0, 1, 2):
            return command

        print("Invalid Field 8 command:", command)
        print("Using automatic mode.")

        return 0

    except Exception as e:

        print("Field 8 read error:", e)

        # Safe fallback to automatic local control
        return 0


# =========================================================
# SEND DATA TO THINGSPEAK
# =========================================================

def send_to_thingspeak(
    water_level,
    temperature,
    water_quality,
    pump_status,
    alarm_status,
    humidity,
    distance
):

    url = (
        THINGSPEAK_UPDATE_URL
        + "?api_key=" + WRITE_API_KEY
        + "&field1=" + str(round(water_level, 2))
        + "&field2=" + str(round(temperature, 2))
        + "&field3=" + str(round(water_quality, 2))
        + "&field4=" + str(pump_status)
        + "&field5=" + str(alarm_status)
        + "&field6=" + str(round(humidity, 2))
        + "&field7=" + str(round(distance, 2))
    )

    try:

        response = urequests.get(url)

        print("ThingSpeak response:", response.text)

        response.close()

    except Exception as e:

        print("ThingSpeak upload error:", e)


# =========================================================
# WIFI CONNECTION
# =========================================================

print()
print("==============================================")
print(" SMART WATER MONITORING SYSTEM")
print(" FULL INTEGRATED TEST")
print("==============================================")
print()

wifi = network.WLAN(network.STA_IF)
wifi.active(True)

print("Connecting to Wi-Fi...")

wifi.connect(SSID, PASSWORD)

timeout = 20

while not wifi.isconnected() and timeout > 0:

    print("Waiting for Wi-Fi...")

    time.sleep(1)

    timeout -= 1


if not wifi.isconnected():

    print("Wi-Fi connection FAILED.")

    while True:
        time.sleep(5)


print("Wi-Fi connected!")
print("IP address:", wifi.ifconfig()[0])

print()
print("System starting...")
print()

# =========================================================
# MAIN LOOP
# =========================================================

while True:

    print()
    print("----------------------------------------------")
    print("READING SYSTEM DATA")
    print("----------------------------------------------")

    # -----------------------------------------------------
    # DHT22
    # -----------------------------------------------------

    try:

        dht_sensor.measure()

        temperature = dht_sensor.temperature()
        humidity = dht_sensor.humidity()

    except Exception as e:

        print("DHT22 ERROR:", e)

        temperature = 0
        humidity = 0


    # -----------------------------------------------------
    # HC-SR04
    # -----------------------------------------------------

    distance = measure_distance()

    if distance is None:

        print("HC-SR04 ERROR")

        distance = TANK_HEIGHT

    water_level = calculate_water_level(distance)


    # -----------------------------------------------------
    # WATER QUALITY
    # -----------------------------------------------------

    adc_value = quality_sensor.read()

    water_quality = (adc_value / 4095.0) * 100.0


    # -----------------------------------------------------
    # THINGSPEAK FIELD 8
    # -----------------------------------------------------

    pump_command = read_pump_command()


    # -----------------------------------------------------
    # DISPLAY READINGS
    # -----------------------------------------------------

    print()
    print("Temperature:", temperature, "C")
    print("Humidity:", humidity, "%")
    print("Distance:", round(distance, 2), "cm")
    print("Water Level:", round(water_level, 2), "%")
    print("Water Quality:", round(water_quality, 2), "%")
    print("ADC Value:", adc_value)

    print()
    print("ThingSpeak Pump Command:", pump_command)


    # =====================================================
    # CONTROL LOGIC
    # =====================================================

    # -----------------------------------------------------
    # SAFETY PRIORITY:
    # POOR WATER QUALITY
    # -----------------------------------------------------

    if water_quality < POOR_QUALITY:

        pump.value(0)

        red_led.value(1)
        green_led.value(0)

        buzzer.duty_u16(32768)

        alarm_status = 1
        pump_status = 0

        print()
        print("STATUS: POOR WATER QUALITY")
        print("PUMP: OFF")
        print("ALARM: ON")


    else:

        # Normal water quality
        red_led.value(0)
        green_led.value(1)

        buzzer.duty_u16(0)

        alarm_status = 0


        # =================================================
        # COMMAND 0 = AUTOMATIC
        # =================================================

        if pump_command == 0:

            if water_level < LOW_LEVEL:

                pump.value(1)

                print()
                print("MODE: AUTOMATIC")
                print("STATUS: WATER LEVEL LOW")
                print("PUMP: ON")


            elif water_level > HIGH_LEVEL:

                pump.value(0)

                print()
                print("MODE: AUTOMATIC")
                print("STATUS: WATER LEVEL HIGH")
                print("PUMP: OFF")


            else:

                print()
                print("MODE: AUTOMATIC")
                print("STATUS: NORMAL WATER LEVEL")
                print("PUMP: PREVIOUS STATE")


        # =================================================
        # COMMAND 1 = FORCE OFF
        # =================================================

        elif pump_command == 1:

            pump.value(0)

            print()
            print("MODE: CLOUD FORCE OFF")
            print("PUMP: OFF")


        # =================================================
        # COMMAND 2 = REQUEST ON
        # =================================================

        elif pump_command == 2:

            if water_level > HIGH_LEVEL:

                pump.value(0)

                print()
                print("MODE: CLOUD REQUEST ON")
                print("STATUS: TANK LEVEL HIGH")
                print("PUMP: OFF")
                print("HIGH-LEVEL SAFETY ACTIVE")

            else:

                pump.value(1)

                print()
                print("MODE: CLOUD REQUEST ON")
                print("PUMP: ON")


        pump_status = pump.value()

        print("ALARM: OFF")


    # =====================================================
    # FINAL STATUS
    # =====================================================

    print()
    print("==============================================")
    print("FINAL STATUS")
    print("==============================================")
    print("Pump Status:", pump_status)
    print("Alarm Status:", alarm_status)
    print("==============================================")


    # =====================================================
    # UPLOAD FIELDS 1-7
    # =====================================================

    print()
    print("Sending data to ThingSpeak...")

    send_to_thingspeak(
        water_level,
        temperature,
        water_quality,
        pump_status,
        alarm_status,
        humidity,
        distance
    )


    print()
    print("Waiting 20 seconds...")
    
    time.sleep(20)
