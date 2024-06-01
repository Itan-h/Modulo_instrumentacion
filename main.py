from machine import Pin
import sensores as s
from extras import BlynkLib, oled, rotary_irq
import network, urequests, time, machine
#-----------------------------------------------------------------------------------------------
#caudal
valve = s.Valvula(4)
sensor_caudal = s.Caudalimetro(9)
bomba = s.Bomba(15)
#temperatura
max1 = s.MAX6675(sck=Pin(1), so=Pin(1), cs=Pin(1))  # Sensor 1
max2 = s.MAX6675(sck=Pin(1), so=Pin(1), cs=Pin(1))  # Sensor 2
resistencia = s.resistencia(3)
#nivel
ultrasonic_1 = s.Ultrasonico(12, 13)
ultrasonic_2 = s.Ultrasonico(12, 13)
hzt1_tanque1 = s.Sensor_switch(6)
hzt2_tanque1 = s.Sensor_switch(7)
hzt1_tanque2 = s.Sensor_switch(8)
hzt2_tanque2 = s.Sensor_switch(9)

btn = Pin(18, Pin.IN, Pin.PULL_UP)#boton del encoder
encoder = rotary_irq.RotaryIRQ(pin_num_clk=21,
                pin_num_dt=19,
                min_val=0,
                max_val=25,
                reverse=True,
                range_mode=rotary_irq.RotaryIRQ.RANGE_WRAP)

display = oled.Display(sck=Pin(18), 
                       mosi=Pin(23),
                       reset=Pin(5,Pin.OUT),
                       dc=Pin(19,Pin.OUT),
                       backlight=Pin(26,Pin.OUT), 
                       id=2)

sp1_temp = 50
sp2_temp = 25
sp_caudal = 220 #lt/hr
sp_nivel = 8

def get_data():
    global tempe1
    global tempe2
    global ult1
    global ult2
    global caudal
    global hz1t1
    global hz2t1
    global hz1t2
    global hz2t2
    global res
    global valv

    tempe1=max1.read()
    tempe2=max2.read()
    ult1=ultrasonic_1.liters()
    ult2=ultrasonic_2.liters()
    caudal=sensor_caudal.get_lthr()
    hz1t1 = hzt1_tanque1.state()
    hz2t1 = hzt2_tanque1.state()
    hz1t2 = hzt1_tanque2.state()
    hz2t2 = hzt2_tanque2.state()
    res = resistencia.get_state()
    valv = valve.get_state()

# WiFi credentials
ssid = 'POCO X4 GT'
password = '234567890'
# ThingSpeak API key y URL
thingspeak_api_key = 'FD2XVQKL2G0RA56X'
thingspeak_url = "https://api.thingspeak.com/update?api_key=" + thingspeak_api_key + "&field1=0"
# Blynk credentials
auth_blynk = "610DmxAtbBJc9c2GVez6WD7DjIuzm1dE"
# Initialize Blynk
blynk = BlynkLib.Blynk(auth_blynk)
# Connect to WiFi
red = network.WLAN(network.STA_IF)
red.active(True)
red.connect(ssid, password)

while not red.isconnected():
    pass

print('Conexión correcta')
print(red.ifconfig())

ultima_peticion = 0
intervalo_peticiones = 10

def reconectar():
    print('Fallo de conexión. Reconectando...')
    time.sleep(10)
    machine.reset()

def blink():
    try:
        if (time.time() - ultima_peticion) > intervalo_peticiones:
            tempe1=round(tempe1, 1)
            tempe2=round(tempe2, 1)
            ult1=round(ult1, 1)
            ult2=round(ult2, 1)
            caudal=round(caudal, 1)
            
            # Actualizar ThingSpeak
            thingspeak_url_update = thingspeak_url + "&field1=" + str(tempe1) + "&field2=" + str(tempe2) + "&field3=" + str(ult1) + "&field4=" + str(ult2) + "&field5=" + str(caudal)
            respuesta_thingspeak = urequests.get(thingspeak_url_update)
            print("Respuesta ThingSpeak:", respuesta_thingspeak.status_code)
            respuesta_thingspeak.close()
            
            # Actualizar Blynk
            blynk.virtual_write(0, tempe1)  # Virtual pin 0 para temperatura1
            blynk.virtual_write(1, tempe2)   # Virtual pin 1 para temperatura2
            blynk.virtual_write(2, ult1)  # Virtual pin 2 para ultrasonico1
            blynk.virtual_write(3, ult2)  # Virtual pin 3 para ultrasonico2
            blynk.virtual_write(4, caudal)  # Virtual pin 4 para caaudal
            ultima_peticion = time.time()
            blynk.run()

    except OSError as e:
        reconectar()

# while((max1.error() == 1) or (max2.error() == 1)): #error en el sensor 
#     pass

def set_display():
    display.data_discrete(5, 5, 178, 236, 93, "Temperatura 1:", str(tempe1))
    display.data_discrete(5, 55, 178, 236, 93, "Temperatura 2:", str(tempe2))
    display.data_discrete(5, 105, 178, 236, 93, "Ultrasonico 1:", str(ult1))
    display.data_discrete(5, 155, 178, 236, 93, "Ultrasonico 2:", str(ult2))

    display.data_logic(5, 205, 'H1t1', hz1t1)
    display.data_logic(105, 205, 'H2t1', hz2t1)
    display.data_logic(200, 205, 'H1t2', hz1t2)
    display.data_logic(5, 255, 'H2t2', hz2t2)
    display.data_logic(105, 255, 'Rest', res)
    display.data_logic(200, 255, 'Valv', valv)

while((hzt1_tanque1.state() == 1) and (hzt1_tanque2.state() == 1)): 
    display.error(10, 10, 'Ambos tanques llenos')

while True:
    time.sleep(0.25)
    get_data()
    blink()
    set_display()
    if((tempe2 <= sp2_temp) and (hz2t2 == 1)):
        if(ult1 <= 9.5):
            pass
            bomba.on_pid(set_point=sp_caudal, procces_v=caudal)
            #Obtener litros totales y presentar en OLED
        else:
            bomba.off()
            if(tempe1 <= sp1_temp):
                resistencia.set_state(1)
            else:
                resistencia.set_state(0)
                if((hz2t1== 1) and (hz1t2 != 1)):
                    valve.set_state(1)
                else:
                    valve.set_state(0)

    else:
        display.error(10, 10, 'Tanque 2 caliente')
    
