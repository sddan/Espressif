# -*- coding: utf-8 -*-
"""
Created on Sat Jun 23 16:03:58 2018

@author: Samuel
"""

import network, time, espsd, ujson
from umqtt.simple import MQTTClient
from machine import Timer

CONFIG = {
        "ip_addr" : "192.168.1.21",
        "subnet" : "255.255.255.0",
        "default_gateway" : "192.168.1.254",
        "dns_srv" : "192.168.1.254",
        "wifi_ssid" : "jalanara_2.4",
        "wifi_pw" : "hornbill",
        "mqtt_broker" : "192.168.1.12",
        "LED_run" : {"name" : "led_run",
                  "pin" : 16,
                  "activestate" : 0
                  },
        "DHT22" : {},
        "PIR" : {},
        "led_run_dly" : 5000,
        "main_sleep" : 7800,
        "location" : "nowhere"
    }

sta_if = network.WLAN(network.STA_IF)
ap_if = network.WLAN(network.AP_IF)

#Turning off AP mode
ap_if.active(False)
sta_if.active(True)

def load_config(filename):
    try:
        with open(filename) as f:
            newconfig = ujson.loads(f.read())
            CONFIG.update(newconfig)
            print("Loaded JSON config file")
    
    except(OSError, ValueError):
        print("Couldn't load JSON config file")

#Load config.json file, if it exists
load_config("config.json")

# Connecting to WiFi
sta_if.ifconfig( (CONFIG['ip_addr'], CONFIG['subnet'], CONFIG['default_gateway'], CONFIG['dns_srv']) )
print('Connecting to ', CONFIG['wifi_ssid'])
sta_if.connect(CONFIG['wifi_ssid'], CONFIG['wifi_pw'])

if not sta_if.isconnected():
    sta_if.active(True)
    sta_if.connect(CONFIG['wifi_ssid'], CONFIG['wifi_pw'])
    while not sta_if.isconnected():
        pass

print('Network config:', sta_if.ifconfig())

# Connecting to MQTT server
mqid = espsd.name + "_mqtt"
mq = MQTTClient(mqid ,CONFIG['mqtt_broker'])
mq.connect();

# Set device location
espsd.location = CONFIG['location']

# Setting up peripherals
led_run = espsd.LED(CONFIG['LED_run']['name'], CONFIG['LED_run']['pin'], CONFIG['LED_run']['activestate'])
dht22sense = espsd.dht22(CONFIG['DHT22']['name'], CONFIG['DHT22']['pin'])
#httpsrv = espsd.httpsrv(CONFIG['HTTP']['listen_addr'], CONFIG['HTTP']['port'])

# Callback to publish data via MQTT
def mqtt_pub(mq_obj, led = False, dht = False):
#    mq_obj.publish(espsd.name + "/PIR", pir.status)
    mq_obj.publish(espsd.name + "/alive", 'alive')
    
    if led != False:
        mq_obj.publish(espsd.name + "/LED", led.status)
    
    if dht != False:
        mq_obj.publish(espsd.name + "/temperature", dht22sense.temperature)
        mq_obj.publish(espsd.name + "/humidity", dht22sense.humidity)
    
    print('Published messages on individual topics')

def telegraf_mqtt_pub(mq_obj):
    mq_obj.publish(espsd.name + "/telegraf", ujson.dumps(espsd))
    print('Published message on single JSON object topic')

# Callback to blink onboard LED while main loop is running
def led_run_cb(tim):
    led_run.on()
    time.sleep(0.1)
    led_run.off()

# Sleep time to allow DHT22 to set up
time.sleep(3)

# Run status LED timer
led_run_timer = Timer(-1)
led_run_timer.init(period = CONFIG['led_run_dly'], mode = Timer.PERIODIC, callback = led_run_cb)

# DHT22 measure timer
dht22_timer = Timer(-1)

# Calculating DHT22 measure delay time, to account for built in 2.2s delay
if CONFIG['DHT22']['measure_dly'] < 2200:
    dht22_dly = 2200

else:
    dht22_dly = CONFIG['DHT22']['measure_dly']
    
dht22_timer.init(period = dht22_dly, mode = Timer.PERIODIC, callback = dht22sense.measure)

# Main loop
try:
    while True:
        mqtt_pub(mq)
        telegraf_mqtt_pub(mq)
        time.sleep_ms(CONFIG["main_sleep"])

except:
    # Turn on onboard LED to indicate program loop was broken
    led_run_timer.deinit()
    dht22_timer.deinit()
    led_run.on()
    print('End of main program')