from context import TemperatureMonitor
import time

tm = TemperatureMonitor('28-01205b5301d7', 'garage')

measurement = tm.parameters[0]

while True:
    temp = tm.getmeasurement(measurement)
    print("The " + measurement + " is " + temp)
    time.sleep(5)