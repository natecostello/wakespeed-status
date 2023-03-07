from can.listener import Listener
from instrument_logger import Instrument

# For documentation of IDs see:
# http://wakespeed.com/Wakespeed%20%20Communications%20and%20Configuration%20Guide%20v2.5.0-BETA.pdf
# http://www.rv-c.com/sites/rv-c.com/files/RV-C%20FullLayer-05-14-22_0.pdf
# https://www.ceniehoff.com/Documents/Ctrl_Hyperlink/TG39_uid252021133122.pdf
# https://tajhizkala.ir/doc/SAE/SAE-J1939-2007.pdf
# https://continuouswave.com/whaler/reference/PGN.html
# https://github.com/ttlappalainen/NMEA2000

#RV-C
CHARGER_STATUS =                            0x1FFC7
CHARGER_STATUS_2 =                          0x1FEA3
CHARGER_EQUALIZATION_STATUS =               0x1FF99
DM_RV =                                     0x1FECA

RVC_MASK = 0b00001111111111111111100000000
RVC_SHIFT = 8

#J1939 Status
ALTERNATOR_INFORMATION_MESSAGE =            0xFED5
J1939_MASK = 0b00000111111111111111100000000
J1939_SHIFT = 8

#NMEA-2000
NMEA_MASK = 0b00001111111111111111100000000
NMEA_SHIFT = 8

NMEA_ENGINE_PARAMETERS_RAPID_UPDATE =       0x1F200
NMEA_DC_DETAILED_STATUS =                   0x1F212
NMEA_CHARGER_STATUS =                       0x1F213
NMEA_BATTERY_STATUS =                       0x1F214
NMEA_CHARGER_CONFIGURATION_STATUS =         0x1F216
NMEA_BATTERY_CONFIGURATION_STATUS =         0x1F219
NMEA_CONVERTER_STATUS =                     0x1F306



class WakespeedMonitor(Listener, Instrument):

    def __init__(self):

        #RC-V CHARGER STATUS
        self.charge_voltage_target = 0
        self.charge_current_target = 0
        #self.charge_current_percent_max = 0
        #self.operating_state = 0
        #self.default_power_on_state = 0
        #self.auto_recharge_enable = 0
        #self.force_charge = 0

        #RC-V CHARGER STATUS_2
        #self.charger_priority = 0
        self.charging_voltage = 0
        #self.charging_current = 0
        self.charger_temperature = 0

        #J1939 ALTERNATOR_INFORMATION_MESSAGE
        self.alternator_speed = 0

        #NMEA ENGINE_PARAMETERS_RAPID_UPDATE
        self.engine_speed = 0

        #NMEA CHARGER_CONFIGURATION_STATUS
        # #traditionally current command limit %, but wakespeed uses for field drive
        # https://github.com/victronenergy/venus/issues/779#issuecomment-773434948
        self.field_drive = 0 


    @property
    def name(self) -> str:
        """Required for Instrument"""
        return "ws-can"


    @property
    def allmeasurements(self) -> 'dict':
        """Required for Instrument"""
        all_meas = {}
        for param in self.parameters:
            all_meas[param] = self.getmeasurement(param)
        return all_meas
    
    @property
    def parameters(self) -> 'list[str]':
        """Required for Instrument"""
        return [
            self.name + '.CVT.V', 
            self.name + '.CCT.A', 
            #self.name + '.CC Percent Max.%',
            #self.name + '.State.string',
            #self.name + '.POState.string',
            #self.name + '.Auto recharge.string',
            #self.name + '.Forced charge.string',
            
            #self.name + '.Charter Priority.integer'
            self.name + '.CV.V',
            self.name + '.CC.A',
            self.name + '.Alternator Temperature.C',

            self.name + '.Alternator Speed.RPM',

            self.name + '.Engine Speed.RPM',

            self.name + '.Field Drive.%']
    
    def getmeasurement(self, name: str) -> str:
        """Required for Instrument"""
        if (name == self.name + '.CVT.V'):
            return str(self.charge_voltage_target)
        if (name == self.name + '.CCT.A'):
            return str(self.charge_current_target)
        # if (name == self.name + '.State.string'):
        #     return str(self.operating_state)
        # if (name == self.name + '.Forced charge.string'):
        #     return str(self.force_charge)
        if (name == self.name + '.CV.V'):
            return str(self.charging_voltage)
        if (name == self.name + '.CC.A'):
            return str(self.charging_current)
        if (name == self.name + '.Alternator Temperature.C'):
            return str(self.charger_temperature)
        if (name == self.name + '.Alternator Speed.RPM'):
            return str(self.alternator_speed)
        if (name == self.name + '.Engine Speed.RPM'):
            return str(self.engine_speed)
        if (name == self.name + '.Field Drive.%'):
            return str(self.field_drive)


    def on_message_received(self, msg):
        """Requiremed method for Listener"""
        self.translateMessageAndUpdate(msg)

    def __call__(self, msg):
        """method for Listener"""
        self.on_message_received(msg)


    def translateMessageAndUpdate(self, message):
        #Extract RVC DGN
        dgn = (message.arbitration_id & RVC_MASK) >> RVC_SHIFT

        if dgn == CHARGER_STATUS:
            self.charge_voltage_target = round(0.05 * int.from_bytes(message.data[1:3], 'little'), 2)
            self.charge_current_target = round(-1600 + 0.05 * int.from_bytes(message.data[3:5], 'little'), 2)
            
        if dgn == CHARGER_STATUS_2:
            self.charging_voltage = round(0.05 * int.from_bytes(message.data[3:5], 'little'), 2)
            self.charging_current = round(-1600 + 0.05 * int.from_bytes(message.data[5:7], 'little'), 2)
            self.charger_temperature = round(-40 + 1.0 * message.data[7], 1)

        #Extract J1939 PGN
        pgn = (message.arbitration_id & J1939_MASK) >> J1939_SHIFT

        if pgn == ALTERNATOR_INFORMATION_MESSAGE:
            self.alternator_speed = round(0.5 * int.from_bytes(message.data[0:2], 'little'), 1)

        #Extract NMEA PGN
        pgn = (message.arbitration_id & NMEA_MASK) >> NMEA_SHIFT

        if pgn == NMEA_ENGINE_PARAMETERS_RAPID_UPDATE:
            self.engine_speed = round(0.25 * int.from_bytes(message.data[1:3], 'little'), 2)
        
        if pgn == NMEA_CHARGER_CONFIGURATION_STATUS:
            if message.data[5] != 0xFF:
                self.field_drive = round(1.0 * message.data[5])



                
        # if message.arbitration_id == BATTERY_VOLT_CURRENT_TEMP_ID:
        #     self.battery_voltage = round(0.01 * int.from_bytes(message.data[0:2], 'little'), 2)
        #     self.battery_current = round(0.1 * int.from_bytes(message.data[2:4], 'little', signed=True), 1)
        #     self.battery_temperature = round(0.1 * int.from_bytes(message.data[4:6], 'little'), 1)
            
        # if message.arbitration_id == MIN_MAX_CELL_VOLT_TEMP_ID:
        #     self.min_cell_voltage = round(0.001 * int.from_bytes(message.data[0:2], 'little'), 3)
        #     self.max_cell_voltage = round(0.001 * int.from_bytes(message.data[2:4], 'little'), 3)
        #     self.min_temperature = int.from_bytes(message.data[4:6], 'little') - KELVN_TO_C
        #     self.max_temperature = int.from_bytes(message.data[6:8], 'little') - KELVN_TO_C
            
        # if message.arbitration_id == RATED_CAPACITY:
        #     self.rated_capacity = int.from_bytes(message.data[0:2], 'little')
        #     if self.rated_capacity > 250:
        #         self.rated_capacity += 1
            
        # if message.arbitration_id == CHEM_HWVERS_CAPACITY_SWVERS_ID:
        #     self.remaining_capacity = int.from_bytes(message.data[4:6], 'little')

        # if message.arbitration_id == ALARM_WARNING_ID:
        #     self.alarmBytes = message.data[0:4]
        #     bits = ''
        #     for byte in self.alarmBytes:
        #         bits += '{0:0>8b}'.format(byte) + ' '
        #     self.alarmBits = bits[:-1]

        #     self.warningBytes = message.data[4:8]
        #     bits = ''
        #     for byte in self.warningBytes:
        #         bits += '{0:0>8b}'.format(byte) + ' '
        #     self.warningBits = bits[:-1]

