#####################################################################################
####    wjnSHT30reader.py  SHT30 Temperature and Humidity Reader
####    Version 1, July 8, 2023
####    Version 2, November 19, 2023
####        Created a get measurement function to return data in library
####    William Neubert
#####################################################################################

__version__ = "2.2"
__author__ = "William Neubert"

try:
    import math
    import board
    import busio
    import adafruit_sht31d
except:
    WJN_TEMPRHSENSOR = bool(False)

EWMA_Gamma = 0.5 # EXPONENTIALLY WEIGHTED MOVING AVERAGE
sht30 = bool(False)

class wjn_sht30:

    def __init__(self):
        self.name = "SHT30 Temperature and Humidity Sensor"
        self.status = False
        self.sensor1 = self.start()
        # self.FirstPass = bool(True)
        self.Temperature = self.get_Temperature()
        self.RH = self.get_RH()
        self.DewPoint = self.get_DP()

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
            self.Temperature = round(self.sensor1.temperature,1)
            return_value = self.Temperature
        else:
            return_value = -99

        return return_value
    
    def get_RH(self):    
        if self.status:
            self.RH = round(self.sensor1.relative_humidity,0)
            return_value = self.RH
        else:
            return_value = -99

        return return_value
    
    def get_DP(self): # DEW POINT
        a = 6.112 # mBar
        b = 17.67; c = 243.5 # CELSIUS

        T = self.Temperature
        rh = self.RH/100
        gamma = math.log(rh) + b * T / (c + T)
        self.DewPoint = round(c * gamma/(b - gamma),1)
        return self.DewPoint
    
    def GetWeatherData(self): # UPDATE THE WEATHER DATA
        try:
            self.Temperature = round((1 - EWMA_Gamma) * self.Temperature + EWMA_Gamma * self.get_Temperature(),2)
            self.RH = round((1 - EWMA_Gamma) * self.RH + EWMA_Gamma * self.get_RH(),0)
            self.DewPoint = round((1 - EWMA_Gamma) * self.DewPoint + EWMA_Gamma * self.get_DP(),1)
            returnData = {"Temperature": round(self.Temperature,1), "Relative Humidity":self.RH, "Dew Point":self.DewPoint, "Message":"Data valid", "Status": bool(True)}
        except:
            returnData = {"Temperature": -99, "Relative Humidity":0, "Dew Point":-99, "Message":"Warning:  Data not valid", "Status": bool(False)}
        return returnData