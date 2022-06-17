from context import WakespeedMonitor
from time import sleep
import os
from instrument_logger import InstrumentLogger
import can
from can.notifier import Notifier

os.system("sudo rm *.csv")
os.system("sudo /sbin/ip link set can0 up type can bitrate 250000")


try:         
    wsm = WakespeedMonitor()
    bus = can.interface.Bus(channel='can0', bustype='socketcan', bitrate=250000)         
    notifier = Notifier(bus, [wsm])
    
    logger = InstrumentLogger()
    logger.addinstrument(wsm)
    wsm.start()
    sleep(3)

    logger.start()
    sleep(10)
    logger.stop()


    print("closing can connection")
    notifier.stop()
    bus.shutdown()
    os.system("sudo /sbin/ip link set can0 down")
            
except KeyboardInterrupt:
    print("closing can connection due to keyboard interrupt")
    notifier.stop()
    bus.shutdown()
    os.system("sudo /sbin/ip link set can0 down")
