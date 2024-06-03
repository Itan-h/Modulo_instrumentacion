from machine import Pin
import sensores as s
from extras import BlynkLib_mp, oled, rotary_irq
import network, urequests, time, machine
#-----------------------------------------------------------------------------------------------
#caudal
valve = s.valvula(5,6)
#sensor_caudal = s.Caudalimetro(44,43)
bomba = s.Bomba(2)
#temperatura
max1 = s.MAX6675(42, 8, 15)  # Sensor 1
max2 = s.MAX6675(40,39,41)  # Sensor 2
resistencia = s.Trasductor_digital(4)
#nivel
ultrasonic_1 = s.Ultrasonico(17, 18, 0.1)
ultrasonic_2 = s.Ultrasonico(37, 36, 0.1)
hzt1_tanque1 = s.Sensor_switch(16)
hzt2_tanque1 = s.Sensor_switch(38)
hzt1_tanque2 = s.Sensor_switch(35)
hzt2_tanque2 = s.Sensor_switch(0)

btn = Pin(46, Pin.IN, Pin.PULL_UP)#boton del encoder
encoder = rotary_irq.RotaryIRQ(pin_num_clk=13,
                pin_num_dt=14,
                min_val=0,
                max_val=4,
                reverse=True,
                range_mode=rotary_irq.RotaryIRQ.RANGE_WRAP)

display = oled.Display(sck=Pin(3), 
                       mosi=Pin(9),
                       reset=Pin(10,Pin.OUT),
                       dc=Pin(11,Pin.OUT),
                       cs=Pin(12,Pin.OUT), 
                       id=2)

sp1_temp = 50
sp2_temp = 25
sp_caudal = 220 #lt/hr
sp_nivel = 9.5

ult1=ultrasonic_1.begin()
ult2=ultrasonic_2.begin()

def measuring():
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
    ult1 = ultrasonic_1.liters(ult1)
    ult2 = ultrasonic_2.liters(ult2)
    #caudal=sensor_caudal.get_lthr()
    hz1t1 = hzt1_tanque1.state()
    hz2t1 = hzt2_tanque1.state()
    hz1t2 = hzt1_tanque2.state()
    hz2t2 = hzt2_tanque2.state()
    res = resistencia.get_state()
    valv = valve.get_state()

# WiFi credentials
ssid = 'IZZI-F0EC'
password = '63emkXM3fzrfT2c7fy'
# ThingSpeak API key y URL
thingspeak_api_key = 'FD2XVQKL2G0RA56X'
thingspeak_url = "https://api.thingspeak.com/update?api_key=" + thingspeak_api_key + "&field1=0"
# Blynk credentials
auth_blynk = "610DmxAtbBJc9c2GVez6WD7DjIuzm1dE"
# Initialize Blynk
blynk = BlynkLib_mp.Blynk(auth_blynk)
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
    display.data_discrete(10, 0, "Temperatura 1:", tempe1)
    display.data_discrete(10, 32, "Temperatura 2:", tempe2)
    display.data_discrete(10, 64, "Ultrasonico 1:", ult1)
    display.data_discrete(10, 96, "Ultrasonico 2:", ult2)
    #display.data_discrete(5, 155, "cdl:", caudal)

    display.data_logic(10, 128, 'H1t1', hz1t1)
    display.data_logic(100, 128, 'H2t1', not(hz2t1))
    display.data_logic(10, 160, 'H1t2', hz1t2)
    display.data_logic(100, 160, 'H2t2', not(hz2t2))
    display.data_logic(10, 192, 'Rest', res)
    display.data_logic(100, 192, 'Valv', valv)

#while((hzt1_tanque1.state() == 1) and (hzt1_tanque2.state() == 1)): 
#   display.error(10, 10, 'Ambos tanques llenos')

while True:
    time.sleep(0.1)
    measuring()
    blink()
    set_display()
    '''
    if((tempe2 <= sp2_temp) and (hz2t2 == 1)):
        if(ultrasonic_1.on_off(0.2, ult1, sp_nivel) == 1):
            pass
            bomba.on_pid()
            bomba.on_pid(set_point=sp_caudal, procces_v=caudal)
            #Obtener litros totales y presentar en OLED
        else:
            bomba.off()
            if(tempe1 <= sp1_temp):
                resistencia.set_state(1)
            else:
                resistencia.set_state(0)
                if((hz2t1 != 1) and (hz1t2 != 1)):
                    valve.set_state(1)
                else:
                    valve.set_state(0)

    else:
        display.error(10, 10, 'Tanque 2 caliente o vacio')'''
    

    print("a")

