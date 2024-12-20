"""
    Simulation of temperature curve for testing purpose.
"""
#   Includes error handling for sensor not found and keyboard interrupt to stop program
#   Fixed data, varable data and graph data are split over three different turtles.
#
#   Improvement:
#      1    Create buffer that holds the collected data
#      2    Use buffered data to delete previuou data points which enabled a rolling graph
#           which allows to see histiory data which is not apossible now as graph is deleted
#           at 00:00 hours,
import time
import datetime
import turtle
import math

fixed_scr = turtle.Turtle()                         # fixed_screen used for static graph data
var_scr = turtle.Turtle()
grph_scr = turtle.Turtle()

fixed_scr.screen.bgcolor('Light Blue')
fixed_scr.screen.screensize (1200, 700)
fixed_scr.screen.setup(width=1.0, height=1.0, startx=None, starty=None)
fixed_scr.hideturtle()
fixed_scr.penup()
fixed_scr.speed(0)                                  # Set turtle to max speed.
fixed_scr.clear()
fixed_scr.screen.tracer(0)
var_scr.screen.tracer(0)
var_scr.hideturtle()
var_scr.penup()
var_scr.speed(0)
var_scr.clear()

grph_scr.hideturtle()
grph_scr.penup()
grph_scr.clear()
grph_scr.screen.tracer(0)


def read_temp(x):
    """
        Simulate temperature curve
    """
    temp = round(19.30 + 2*math.sin(x*math.pi/10000), 2)
    return temp

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
    fixed_scr.screen.update()

def grph_scr_dot(x, temp):
    """
        Plot dot at give x and y coordinates
    """
    y = round(temp, 0)*10
    grph_scr.penup()
    grph_scr.goto (x, y)
    grph_scr.pendown()
    grph_scr.dot(4, 'Blue')
    grph_scr.penup()
    grph_scr.screen.update()

def fixed_text():
    """
        Printing fixed text on grahics fixed_screen
    """
    fixed_scr.color("Black")
    fixed_scr.hideturtle()
    fixed_scr.penup()
    fixed_scr.goto (-240, -100)
    fixed_scr.write("High temp   :", font=("Arial", 14, "normal"))
    fixed_scr.goto (-240, -130)
    fixed_scr.write("Low temp    :", font=("Arial", 14, 'normal'))
    fixed_scr.goto (-480, -100)
    fixed_scr.write("Actual temp :", font=("Arial", 14, "normal"))
    fixed_scr.goto (100, -100)
    fixed_scr.write("Up time      :", font=("Arial", 14, "normal"))
    fixed_scr.screen.update()

def txt_values(high, low, act, up):
    """
        Print actual values that go along the fixed text.
    """
    var_scr.hideturtle()
    var_scr.penup()
    var_scr.goto (-120, -100)                                  # Print actual values
    var_scr.write(high, font=("Arial", 14, "normal"))
    var_scr.goto (-120, -130)
    var_scr.write(low, font=('Arial', 14, 'normal'))
    var_scr.goto (-360, -100)
    var_scr.write(act, font=('Arial', 14, 'normal'))
    var_scr.goto (210, -100)
    var_scr.write(up, 14, font=("Arial", 14, "normal"))
    var_scr.screen.update()

def main():
    """"
        Loop indefinite temp reading and led flashing
    """
    buf_cnt=0
    fixed_scr_layout()                                      # Plot graph lines
    fixed_text()                                            # Print fixed text on fixed_screen
    timestr = datetime.datetime.now().strftime ("%H%M%S")   # Extract seconds from time string
    time_sec = timestr[4:6]
    count = 0
    time_t = 0
    temp_high = 0.00
    temp_low = 40.00
    temp = 0.00
    up_hrs=0
    up_min=0
    start_time=time.perf_counter()
    print ("Temperature fixed_script started at:", timestr, time_t)
    try:
        while True:
            if int(time_sec) == time_t:
                temp = read_temp(count)
                if int(round(temp,2)*100) > int(round(temp_high,2)*100):
                    temp_high = round(temp,2)
                if int(round(temp,2)*100) < int(round(temp_low, 2)*100):
                    temp_low = round(temp,2)
                var_scr.clear()                                         # Clear text fixed_screen
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
                    fixed_scr_hrs = timestr[0:2]
                    fixed_scr_min = timestr[2:4]
                    x = -480 + int(((int(fixed_scr_hrs)*60 + int(fixed_scr_min))/60)*40)
                    if x== -480:                                   # Erase graph @ 00:00
                        grph_scr.clear()
                        grph_scr.screen.update()
                    grph_scr_dot(x, temp)
            timestr = datetime.datetime.now().strftime ("%H%M%S")
            time_sec = timestr[4:6]
    except KeyboardInterrupt:                                       # Capture <CTRL> + c to stop
        print ("Program stopped by keyboard")

if __name__ == '__main__':
    main()
