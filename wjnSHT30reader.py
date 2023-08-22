#####################################################################################
####    wjnSHT30reader.py  SHT30 Temperature and Humidity Reader
####    Version 1, July 8, 2023
####    William Neubert
#####################################################################################

try:
    import math
    import board
    import busio
    import adafruit_sht31d
except:
    WJN_TEMPRHSENSOR = bool(False)

sht30 = bool(False)

class wjn_sht30:
    def __init__(self):
        self.name = "SHT30 Temperature and Humidity Sensor"
        self.status = False
        self.sensor1 = self.start()
    def start(self):
        try:
            i2c = busio.I2C(board.SCL, board.SDA)
            sensor = adafruit_sht31d.SHT31D(i2c)
            self.status = bool(True)
        except:
            self.status = bool(False)
        
        return sensor
    
    def get_Temperature(self):
        
        if self.status:
            return_value = round(self.sensor1.temperature,1)
        else:
            return_value = -99

        return return_value
    def get_RH(self):
        
        if self.status:
            return_value = round(self.sensor1.relative_humidity,0)
        else:
            return_value = -99

        return return_value
    
    def get_DP(self): # DEW POINT
        a = 6.112 # mBar
        b = 17.67; c = 243.5 # CELSIUS

        T = self.get_Temperature()
        rh = self.get_RH()/100
        gamma = math.log(rh) + b * T / (c + T)
        Tdp = round(c * gamma/(b - gamma),1)
        return Tdp