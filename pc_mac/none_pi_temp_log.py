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
#   Add PIR sensor to enable LED flashing only when person is around
#   Considered code profiling as Pi zero runs on 90 - 100% CPU
#
import time
import datetime
import turtle
import math

scr = turtle.Turtle()
txt = turtle.Turtle()

scr.screen.bgcolor('Light Blue')
scr.screen.screensize (1200, 700)
scr.screen.setup(width=1.0, height=1.0, startx=None, starty=None)
scr.hideturtle()
scr.penup()
scr.speed(0)                                           # Set turtle to max speed.
scr.screen.tracer(0)
txt.screen.tracer(0)
txt.hideturtle()

def read_temp(x):
    """
        Simulate temperature curve
    """
    temp = round(20 + 2*math.sin(x*math.pi/1000), 2)
    return temp

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
    scr.dot(4, 'Blue')
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
    txt.goto (100, -100)
    txt.write("Up time      :", font=("Arial", 14, "normal"))


def txt_values(high, low, act, up):
    """
        Print actual values that go along the fixed text.
    """
    txt.hideturtle()
    txt.penup()
    txt.goto (-120, -100)                                  # Print actual values
    txt.write(high, font=("Arial", 14, "normal"))
    txt.goto (-120, -130)
    txt.write(low, font=('Arial', 14, 'normal'))
    txt.goto (-360, -100)
    txt.write(act, font=('Arial', 14, 'normal'))
    txt.goto (210, -100)
    txt.write(up, 14, font=("Arial", 14, "normal"))
    txt.screen.update()

def main():
    """"
        Loop indefinite temp reading and led flashing
    """
    buf_cnt=0
    scr_layout()
    fixed_text()                                            # Print fixed text on screen
    timestr = datetime.datetime.now().strftime ("%H%M%S")   # Extract seconds from time string
    time_sec = timestr[4:6]
    count = 0
    time_t = 0
    temp_high = 0.00
    temp_low = 40.00
    temp = 0.00
    up_hrs=0
    up_min=0
    starttime = timestr
    start_time=time.perf_counter()
    print ("Temperature script started at:", starttime, time_t)
    try:
        while True:
            if int(time_sec) == time_t:
                temp = read_temp(count)
                if int(temp) > int(temp_high):
                    temp_high = round(temp,2)
                if int(temp) < int(temp_low):
                    temp_low = round(temp,2)
                txt.clear()                                             # Clear text screen
                fixed_text()                                            # Update with fixed text
                txt_values(temp_high, temp_low, temp, str(up_hrs)+":"+str(up_min))
                time_t +=3                                              # Interval for updates
                count +=1
                buf_cnt+=1
                if time_t >= 60:
                    time_t=0
                    end_time=time.perf_counter()
                    run_time = end_time - start_time
                    up_hrs = int (run_time/ 3600)
                    up_min = int ((run_time - (up_hrs*3600))/60)
                    print ('Run statitics:')
                    print ("Up time is:", up_hrs,":",up_min)
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
                        scr.screen.update()
                    scr_dot(x, y)
            timestr = datetime.datetime.now().strftime ("%H%M%S")
            time_sec = timestr[4:6]
    except KeyboardInterrupt:                                       # Capture <CTRL> + c to stop
        print ("Program stopped by keyboard")

if __name__ == '__main__':
    main()
