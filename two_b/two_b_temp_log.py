"""
    Led flash routine using PI GPIO pins and read temperature sensor
"""

#
#   Flash two leds using PI GPIO pin 14 and 18 as output.
#   Read DS18B20 temperature sensor data
#   Includes error handling for sensor not found and keyboard interrupt to stop program
#
import time
import datetime
import glob
import sys
import turtle
from threading import Thread, Event

import RPi.GPIO as GPIO

BASE_DIR = '/sys/bus/w1/devices/'
try:
    device_folder = glob.glob(BASE_DIR + '28*')[0]
except IndexError:                                      # No folder 28-xxxxx found, no sensor found
    print ("DS18B20 sensor not found")
    print ("Program stopped")
    sys.exit(1)                                         # Force script end with return code 1
device_file = device_folder + '/w1_slave'

GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.OUT)
GPIO.output(18, GPIO.LOW)
GPIO.setup(14, GPIO.OUT)
GPIO.output(14, GPIO.LOW)

scr = turtle.Turtle()
txt = turtle.Turtle()

scr.screen.screensize (1200, 700)
scr.screen.setup(width=1.0, height=1.0, startx=None, starty=None)
scr.hideturtle()
scr.penup()
scr.speed(0)                                            # Set turtle to max speed.
scr.screen.tracer(0)
txt.screen.tracer(0)
txt.hideturtle()

def flash_led(event):
    """
        Flash led twice using Pi GPIO pins 14 and 18
    """
    t = 0
    while True:
        time_str = datetime.datetime.now().strftime ("%H%M%S")   # Extract seconds from time string
        sec = time_str[4:6]
        if int(sec) == t:
            t +=3
            GPIO.output(18, GPIO.HIGH)
            time.sleep(0.08)
            GPIO.output(18, GPIO.LOW)
            time.sleep(0.05)
            GPIO.output(14, GPIO.HIGH)
            time.sleep(0.08)
            GPIO.output(14, GPIO.LOW)
            time.sleep(0.05)
        if t >= 60:
            t=0
        if event.is_set():
            print('The thread was stopped prematurely.')
            break

def read_temp_raw():
    """
        Read file from Temp sensor
    """
    try:
        with open (device_file, 'r') as f:                  # For improved file handling
            lines = f.readlines()
        return lines
    except FileNotFoundError:
        print ("No Sensor found.")
def read_temp():
    """
        Extract temperature from Temp sensor file
    """
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        return temp_c

def scr_layout():
    """
    Module used to create initial screen layout
    """
    for i in range (5):                             # y scale 50 / 10 degrees
        if i == 0:
            scr.pensize(2)
            scr.color('Black')
        else:
            scr.pensize(1)
            scr.color('Gray')
        scr.goto(-500, i*100-5)
        scr.write(i*10, font=('Arial', 8, "normal"))
        scr.goto(-480, i*100)                        # Start point x scale -480
        scr.pendown()
        scr.goto(480, i*100)
        scr.penup()
    for i in range (25):                            # x scale 40 / hour
        if i==0:
            scr.pensize(2)
            scr.color('Black')
        else:
            scr.pensize(1)
            scr.color('Gray')
        scr.goto(-480+i*40, -20)
        scr.write(i, font=('Arial', 8, "normal"))
        scr.goto (-480+i*40, 0)
        scr.pendown()
        scr.goto (-480+i*40, 400)
        scr.penup()
    scr.screen.update()

def scr_dot(x, temp):
    """
        Plot dot at give x and y coordinates
    """
    y = round(temp, 0)*10
    scr.penup()
    scr.goto (x, y)
    scr.pendown()
    scr.dot(2, 'Blue')
    scr.penup()
    scr.screen.update()

def fixed_text():
    """
        Printing fixed text on grahics screen
    """
    txt.hideturtle()
    txt.penup()
    txt.goto (-240, -100)
    txt.write("High temp   :", font=("Arial", 14, "normal"))
    txt.goto (-240, -130)
    txt.write("Low temp    :", font=("Arial", 14, 'normal'))
    txt.goto (-480, -100)
    txt.write("Actual temp :", font=("Arial", 14, "normal"))


def txt_values(high, low, act):
    """
        Print actual values that go along the fixed text.
    """
    txt.hideturtle()
    txt.penup()
    txt.goto (-120, -100)                                  # Print actual values
    txt.write(high, font=("Arial", 12, "normal"))
    txt.goto (-120, -130)
    txt.write(low, font=('Arial', 12, 'normal'))
    txt.goto (-360, -100)
    txt.write(act, font=('Arial', 12, 'normal'))
    txt.screen.update()

def main():
    """"
        Loop indefinite temp reading and led flashing
    """
    buf_cnt=0
    event = Event()
    scr_layout()
    fixed_text()                                            # Print fixed text on screen
    t1 = Thread(target=flash_led, args=(event,), daemon=True)
    t1.start()
    print ('Led flash daemon started')
    timestr = datetime.datetime.now().strftime ("%H%M%S")   # Extract seconds from time string
    time_hrs = timestr[0:2]
    time_min = timestr[2:4]
    time_sec = timestr[4:6]
    count = 0
    time_t = 0
    temp_high = 0.00
    temp_low = 40.00
    temp = 0.00
    starttime = timestr
    start_time=time.perf_counter()
    print ("Temperature script started at:", starttime, time_t)
    try:
        while True:
            if int(time_sec) == time_t:
                temp = read_temp()
#                print(timestr, time_t, temp, count, buf_cnt)
                if int(temp*1000) > int(temp_high*1000):
                    temp_high = temp
                if int(temp*1000) < int(temp_low*1000):
                    temp_low = temp
                txt.clear()                                             # Clear text screen
                fixed_text()                                            # Update with fixed text
                txt_values(temp_high, temp_low, temp)                   # Update with variable data
                time_t +=3
                count +=1
                buf_cnt+=1
                if time_t >= 60:
                    time_t=0
                    end_time=time.perf_counter()
                    run_time = end_time - start_time
                    time_hrs = int (run_time/ 3600)
                    time_min = int ((run_time - (time_hrs*3600))/60)
                    print ('Run statitics:')
                    print ("Up time is:", time_hrs,":",time_min)
                    print ("High temp :", temp_high)
                    print ("Low temp:", temp_low)
                if buf_cnt>=30:
                    buf_cnt=0
                    timestr = datetime.datetime.now().strftime ("%H%M%S")
                    scr_hrs = timestr[0:2]
                    scr_min = timestr[2:4]
                    x = -480 + int(((int(scr_hrs)*60 + int(scr_min))/60)*40)
                    y = round(float(temp),0)
                    if x== -480:                                   # Re-draw screen at 00:00 hrs
                        scr.clear()
                        scr_layout()
                        scr.update()
                    scr_dot(x, y)
            timestr = datetime.datetime.now().strftime ("%H%M%S")
            time_sec = timestr[4:6]


    except KeyboardInterrupt:                                       # Capture <CTRL> + c to stop
        event.set()                                                 # Stop daemon
        print ("Thread event set")
        t1.join()                                                   # Wait for daemon to stop
        print ("Program ended by keyboard interrupt")
        GPIO.cleanup()


if __name__ == '__main__':
    main()
