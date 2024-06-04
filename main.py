from machine import Pin
import sensores as s
from extras import BlynkLib_mp, oled, rotary_irq
import network, urequests, time, machine
import st7789
#-----------------------------------------------------------------------------------------------
#caudal
valve = s.valvula(5,6)
sensor_caudal = s.Caudalimetro(44,43)
bomba = s.Bomba(1)
#temperatura
max2 = s.MAX6675(42, 8, 15)  # Sensor 1
max1 = s.MAX6675(40,39,41)  # Sensor 2
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
                max_val=7,
                reverse=True,
                range_mode=rotary_irq.RotaryIRQ.RANGE_WRAP)

display = oled.Display(sck=Pin(3), 
                       mosi=Pin(9),
                       reset=Pin(10,Pin.OUT),
                       dc=Pin(11,Pin.OUT),
                       cs=Pin(12,Pin.OUT), 
                       id=2)

sp1_temp = 40
sp2_temp = 30
sp_caudal = 220 #lt/hr
sp_nivel = 9

caudal_ant=0
temp1_ant=0
temp2_ant=0

activation=False
count=10
encoder.set(value=1)

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
    caudal=sensor_caudal.get_lthr()
    hz1t1 = hzt1_tanque1.state()
    hz2t1 = hzt2_tanque1.state()
    hz1t2 = hzt1_tanque2.state()
    hz2t2 = hzt2_tanque2.state()
    res = resistencia.get_state()
    valv = valve.get_state()
'''
# WiFi credentials
ssid = 'Ingrid Zoe'
password = 'Ingrid08'
# ThingSpeak API key y URL
thingspeak_api_key = 'OEZ2DZM0LU0760LA'
thingspeak_url = "https://api.thingspeak.com/update?api_key=" + thingspeak_api_key + "&field1=0"
# Blynk credentials
auth_blynk = 'tRQzMwfAls9yDoETDjk-INun-DJzwVxV'
# Initialize Blynk
blynk = BlynkLib_mp.Blynk(auth_blynk)
# Connect to WiFi
red = network.WLAN(network.STA_IF)
red.active(True)
red.connect(ssid, password)

while not red.isconnected():
    print("conectando")
    display.data_discrete(10, 132, "conectando...", 0)
    pass
    display.oled_clear()

print('Conexión correcta')
print(red.ifconfig())

ultima_peticion = 0
intervalo_peticiones = 10

def reconectar():
    display.data_discrete(10, 132, "desconectado...", 0)
    print('Fallo de conexión. Reconectando...')
    time.sleep(10)
    machine.reset()

def blink():
    global tempe1
    global tempe2
    global ult1
    global ult2
    global caudal
    global ultima_peticion
    global intervalo_peticiones
    try:
        if (time.time() - ultima_peticion) > intervalo_peticiones:
            t1=round(tempe1, 1)
            t2=round(tempe2, 1)
            u1=round(ult1, 1)
            u2=round(ult2, 1)
            cl=round(caudal, 1)
            
            # Actualizar ThingSpeak
            thingspeak_url_update = thingspeak_url + "&field1=" + str(t1) + "&field2=" + str(t2) + "&field3=" + str(u1) + "&field4=" + str(u2) + "&field5=" + str(cl)
            respuesta_thingspeak = urequests.get(thingspeak_url_update)
            print("Respuesta ThingSpeak:", respuesta_thingspeak.status_code)
            respuesta_thingspeak.close()
            
            # Actualizar Blynk
            
            blynk.virtual_write(0, t1)  # Virtual pin 0 para temperatura1
            blynk.virtual_write(1, t2)   # Virtual pin 1 para temperatura2
            blynk.virtual_write(2, u1)  # Virtual pin 2 para ultrasonico1
            blynk.virtual_write(3, u2)  # Virtual pin 3 para ultrasonico2
            blynk.virtual_write(4, cl)  # Virtual pin 4 para caaudal
            ultima_peticion = time.time()
                

    except OSError as e:
        reconectar()
'''
# while((max1.error() == 1) or (max2.error() == 1)): #error en el sensor 
#     pass

def set_display():
    display.data_discrete(10, 0, "Temp 1:", tempe1, "°C     ")
    display.data_discrete(10, 33, "Temp 2:", tempe2, "°C     ")
    display.data_discrete(10, 66, "U Sonic 1:", round(ult1, 2), "L     ")
    display.data_discrete(10, 99, "U Sonic 2:", round(ult2, 2),"L     ")
    display.data_discrete(10, 132, "cdl:", caudal, "L/h   ")
    display.data_discrete(210, 132, "enc:", encoder.value())

    display.data_logic(10, 169, 'H1t1', hz1t1)
    display.data_logic(105, 169, 'H2t1', not(hz2t1))
    display.data_logic(200, 169, 'H1t2', hz1t2)
    display.data_logic(10, 202, 'H2t2', not(hz2t2))
    display.data_logic(105, 202, 'Rest', res)
    display.data_logic(200, 202, 'Valv', valv)

def graphic_caudal():
    global caudal_ant
    global count
    x1=count-1
    x2=count
    y1=220-(int(caudal_ant*220/400))
    y2=220-(int(caudal*220/400))
    caudal_ant=caudal
    display.label(120,0,"CAUDAL", st7789.BLUE)
    display.graph(10,0,10,240, st7789.WHITE)
    display.graph(0,220,320,220, st7789.WHITE)
    display.graph(x1,y1,x2,y2, st7789.BLUE)
    display.label(180,223,str(caudal)+" L/h", st7789.BLUE)
    if count==319:
        display.oled_clear()

def graphic_temp1():
    global temp1_ant
    global count
    x1=count-1
    x2=count
    y1=220-int(temp1_ant*2)
    y2=220-int(tempe1*2)
    temp1_ant=tempe1
    display.label(110,0,"TEMPERATURA 1", st7789.RED)
    display.graph(10,0,10,240, st7789.WHITE)
    display.graph(0,220,320,220, st7789.WHITE)
    display.graph(x1,y1,x2,y2, st7789.RED)
    display.label(220,223,str(tempe1)+" C", st7789.RED)
    if count==319:
        display.oled_clear()

def graphic_temp2():
    global temp2_ant
    global count
    x1=count-1
    x2=count
    y1=220-int(temp2_ant*2)
    y2=220-int(tempe2*2)
    temp2_ant=tempe2
    display.label(110,0,"TEMPERATURA 2", st7789.RED)
    display.graph(10,0,10,240, st7789.WHITE)
    display.graph(0,220,320,220, st7789.WHITE)
    display.graph(x1,y1,x2,y2, st7789.RED)
    display.label(220,223,str(tempe2)+" C", st7789.RED)
    if count==319:
        display.oled_clear()

def display_selection():
    if encoder.value()==1:
        set_display()
    elif encoder.value()==0 or encoder.value()==2 or encoder.value()== 4 or encoder.value()==6:
        display.oled_clear()
    elif encoder.value()==3:
        graphic_caudal()
    elif encoder.value()==5:
        graphic_temp1()
    elif encoder.value()==7:
        graphic_temp2()

while((hzt1_tanque1.state() == 1) and (hzt1_tanque2.state() == 1)): 
    display.error(10, 10, 'Ambos tanques llenos')

while True:
    time.sleep(0.1)
    count+=1 
    if count==320: count=10
    measuring()
    display_selection()
    #blink()
    if((tempe2 <= sp2_temp) and not ultrasonic_1.on_off(0.2,ult1,sp_nivel)):
        bomba.on_pid(set_point=sp_caudal, procces_v=caudal)

    elif tempe1 <=sp1_temp and ultrasonic_1.on_off(0.2,ult1,sp_nivel):
        bomba.off()
        resistencia.set_state(1)
    elif activation:
        valve.on()
        while (ult1!=0):
            measuring()
            display_selection()
            time.sleep(0.1)
        valve.off()
        activation=False
    elif tempe1>= sp1_temp:
        bomba.off()
        resistencia.set_state(0)
        activation=True