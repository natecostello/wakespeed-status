from can.listener import Listener
from instrument_logger import Instrument

# For documentation of IDs see:
# http://wakespeed.com/Wakespeed%20%20Communications%20and%20Configuration%20Guide%20v2.5.0-BETA.pdf
# http://www.rv-c.com/sites/rv-c.com/files/RV-C%20FullLayer-05-14-22_0.pdf
# https://www.ceniehoff.com/Documents/Ctrl_Hyperlink/TG39_uid252021133122.pdf
# https://tajhizkala.ir/doc/SAE/SAE-J1939-2007.pdf
# https://continuouswave.com/whaler/reference/PGN.html

#RV-C
CHARGER_STATUS =                            0x1FFC7
CHARGER_STATUS_2 =                          0x1FEA3
CHARGER_EQUALIZATION_STATUS =               0x1FF99
DM_RV =                                     0x1FECA

#J1939 Status
ALTERNATOR_INFORMATION_MESSAGE =            0xFED5

#NMEA-2000
ENGINE_PARAMETERS_RAPID_UPDATE =            0x1F200


class WakespeedMonitor(Listener, Instrument):
    pass
