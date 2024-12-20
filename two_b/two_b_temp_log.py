"""
    Led flash routine using PI GPIO pins and read temperature sensor
"""

#
#   Flash two leds using PI GPIO pin 14 and 18 as output.
#   Read DS18B20 temperature sensor data
#   Includes error handling for sensor not found and keyboard interrupt to stop program
#
#   Improvements:
#   For temp graph curve split grid and graph over two turtles, no redraw of grid required.
#   Add PIR sensor to enable LED flashing only when person is around. 
#   Considered code profiling as Pi zero runs on 90 - 100% CPU
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
    sys.exit(1)                                         # Force fixed_script end with return code 1
device_file = device_folder + '/w1_slave'

GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.OUT)
GPIO.output(18, GPIO.LOW)
GPIO.setup(14, GPIO.OUT)
GPIO.output(14, GPIO.LOW)

fixed_scr = turtle.Turtle()
txt = turtle.Turtle()

fixed_scr.fixed_screen.fixed_screensize (1200, 700)
fixed_scr.fixed_screen.setup(width=1.0, height=1.0, startx=None, starty=None)
fixed_scr.hideturtle()
fixed_scr.penup()
fixed_scr.speed(0)                                            # Set turtle to max speed.
fixed_scr.fixed_screen.tracer(0)
txt.fixed_screen.tracer(0)
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

def fixed_scr_layout():
    """
    Module used to create initial fixed_screen layout
    """
    for i in range (5):                             # y scale 50 / 10 degrees
        if i == 0:
            fixed_scr.pensize(2)
            fixed_scr.color('Black')
        else:
            fixed_scr.pensize(1)
            fixed_scr.color('Gray')
        fixed_scr.goto(-500, i*100-5)
        fixed_scr.write(i*10, font=('Arial', 8, "normal"))
        fixed_scr.goto(-480, i*100)                        # Start point x scale -480
        fixed_scr.pendown()
        fixed_scr.goto(480, i*100)
        fixed_scr.penup()
    for i in range (25):                            # x scale 40 / hour
        if i==0:
            fixed_scr.pensize(2)
            fixed_scr.color('Black')
        else:
            fixed_scr.pensize(1)
            fixed_scr.color('Gray')
        fixed_scr.goto(-480+i*40, -20)
        fixed_scr.write(i, font=('Arial', 8, "normal"))
        fixed_scr.goto (-480+i*40, 0)
        fixed_scr.pendown()
        fixed_scr.goto (-480+i*40, 400)
        fixed_scr.penup()
    fixed_scr.fixed_screen.update()

def fixed_scr_dot(x, temp):
    """
        Plot dot at give x and y coordinates
    """
    y = round(temp, 0)*10
    fixed_scr.penup()
    fixed_scr.goto (x, y)
    fixed_scr.pendown()
    fixed_scr.dot(2, 'Blue')
    fixed_scr.penup()
    fixed_scr.fixed_screen.update()

def fixed_text():
    """
        Printing fixed text on grahics fixed_screen
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
    txt.fixed_screen.update()

def main():
    """"
        Loop indefinite temp reading and led flashing
    """
    buf_cnt=0
    event = Event()
    fixed_scr_layout()
    fixed_text()                                            # Print fixed text on fixed_screen
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
    print ("Temperature fixed_script started at:", starttime, time_t)
    try:
        while True:
            if int(time_sec) == time_t:
                temp = read_temp()
#                print(timestr, time_t, temp, count, buf_cnt)
                if int(temp*1000) > int(temp_high*1000):
                    temp_high = temp
                if int(temp*1000) < int(temp_low*1000):
                    temp_low = temp
                txt.clear()                                             # Clear text fixed_screen
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
                    fixed_scr_hrs = timestr[0:2]
                    fixed_scr_min = timestr[2:4]
                    x = -480 + int(((int(fixed_scr_hrs)*60 + int(fixed_scr_min))/60)*40)
                    y = round(float(temp),0)
                    if x== -480:                                   # Re-draw fixed_screen at 00:00 hrs
                        fixed_scr.clear()
                        fixed_scr_layout()
                        fixed_scr.update()
                    fixed_scr_dot(x, y)
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
