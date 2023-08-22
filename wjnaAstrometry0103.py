#####################################################################################
####    wjnaAstrometry.py  Astrometry Module
####    Version 1.3, April 20, 2023 Revised August 12, 2023
####    William Neubert
#####################################################################################

__version__ = "1.3"
__author__ = "William Neubert"

# IMPORT MODULES
import datetime
import math
import numpy as np

#  DEFINE GLOBAL CONSTANTS

#
#  DEFINE FUNCTIONS
#
def waRadians(angleInDegrees):
    return math.pi*angleInDegrees/180.0

def waDegrees(angleInRadians):
    return 180.0*angleInRadians/math.pi

def waJulianDate(utcIn: datetime.datetime):
    #CALCULATE THE JULIAN DATE.  FROM JEAN MEEUS ASTRONOMICAL ALGORITHMS SECOND ADDITION CHAPTER 7.
    d = utcIn.day + (utcIn.hour + utcIn.minute/60 + utcIn.second/3600)/24
    m = utcIn.month
    y = utcIn.year

    if m < 3:
        m = m + 12
        y = y - 1
    
    a = math.floor(y/100)
    b = 2 - a + math.floor(a/4)
    JD = math.floor(365.25*(y+4716)) + math.floor(30.6001*(m+1)) + d + b - 1524.5;
    return JD;
    
def waDtoDMS(angleIn):
    # RECEIVE ANGLE IN DIGITAL DEGREES AND RETURN IN DMS FORMAT AS A STRING
    angleInAbs = math.fabs(angleIn)
    wDeg = math.floor(angleInAbs)
    wMin = math.floor(60 * (angleInAbs - wDeg))
    wSec = math.floor(60 * (60 * (angleInAbs - wDeg) - wMin))
    if angleIn >= 0:
        waDtoDMS = str(wDeg)+chr(176)+" "+str(wMin)+"m "+str(wSec)+"s"
    else:
        waDtoDMS = str(-wDeg)+chr(176)+" "+str(wMin)+"m "+str(wSec)+"s"
    return waDtoDMS


def waHtoHMS(hourIn):
    # RECEIVE TIME IN DIGITAL HOURS AND RETURN IN HMS FORMAT AS A STRING
    dTInAbs = math.fabs(hourIn)
    wHr = math.floor(dTInAbs)
    wMin = math.floor(60 * (dTInAbs - wHr))
    wSec = math.floor(60 * (60 * (dTInAbs - wHr) - wMin))
    returnString = str(wHr)+"h "+str(wMin)+"m "+str(wSec)+"s"
    return returnString

def waDtoHMS(angleIn):
    # RECEIVES TIME IN DEGREES AND RETURN IN HMS FORMAT AS A STRING
    while angleIn < 0:
        angleIn += 360.0
    waDtoHMS = waHtoHMS(24.0 * angleIn / 360.0)
    return waDtoHMS

# UNIVERSAL CONVERTER FROM DECIMAL ANGLES OR HOURS TO STRING 
def waDecimalToDHMS(angleIn,basisIn,formatIn):
    if basisIn == 360 and formatIn[0] == "D": # RECEIVE ANGLE IN DIGITAL DEGREES AND RETURN IN DMS FORMAT AS A STRING
        angleInAbs = math.fabs(angleIn)
        wDeg = math.floor(angleInAbs)
        wMin = math.floor(60 * (angleInAbs - wDeg))
        wSec = math.floor(60 * (60 * (angleInAbs - wDeg) - wMin))
        if angleIn >= 0:
            returnString = str(wDeg)+chr(176)+" "+str(wMin)+"m "
        else:
            returnString = str(-wDeg)+chr(176)+" "+str(wMin)+"m "
        if formatIn == "DMS":
            returnString += str(wSec)+"s "
    elif basisIn == 360 and formatIn[0]== "H": # RECEIVE ANGLE IN DIGITAL DEGREES AND RETURN IN HMS FORMAT AS A STRING
        while angleIn < 0:
            angleIn += 360.0
        angleIn = angleIn % 360
        dTInAbs = math.fabs(angleIn)
        wHr = math.floor(dTInAbs)
        wMin = math.floor(60 * (dTInAbs - wHr))
        wSec = math.floor(60 * (60 * (dTInAbs - wHr) - wMin))
        returnString = str(wHr)+"h "+str(wMin)+"m "
        if formatIn == "HMS":
            returnString += str(wSec)+"s "
    elif basisIn == 24:
        dTInAbs = math.fabs(angleIn)
        wHr = math.floor(dTInAbs)
        wMin = math.floor(60 * (dTInAbs - wHr))
        wSec = math.floor(60 * (60 * (dTInAbs - wHr) - wMin))
        returnString = str(wHr)+"h "+str(wMin)+"m "
        if formatIn == "HMS":
            returnString += str(wSec)+"s "
    else:
        returnString = angleIn
    return returnString

def waTimeDeltaToDHMS(timeDeltaIn: float, formatIn: str):
    """This function accepts a time difference in seconds and returns a formatting string.
    The format string must be DHMS or DHM where D = Days, H = Hours, M = min, S = Second.
    If the time difference is less than a day, only the hour, min and sec portion will be returned."""
    DAYDIVISOR = 86400 # SECONDS IN A DAY
    offsetString = ''

    if timeDeltaIn > DAYDIVISOR:
        offsetString = "{}days ".format(math.floor(timeDeltaIn // DAYDIVISOR))
    offsetString += "{:02}h {:02}m".format(
        math.floor(timeDeltaIn % 86400 // 3600), 
        math.floor(timeDeltaIn % 3600 // 60))
    if formatIn[-1] == 'S':
        offsetString +=  " {:02}s".format(timeDeltaIn % 60)

    return offsetString

    
def MeridianEclipticalConstellation(right_ascention_in: float):
    """This function returns the constellation given the right ascention in hours.  It does not correct for declination, so is only valid at the meridian."""
    ra = right_ascention_in*360/24 # CONVERT TO DEGREES
    epsilon0 = 23.43929111 # OBLIQUITY IN DEGREES OF EPOCH 2000.0 NOT ADJUSTED FOR PROCESSION
    returnvalue = ["---","---"]
    try:
        el = waDegrees( math.atan2( math.sin(waRadians(ra)) * math.cos(waRadians(epsilon0)), math.cos(waRadians(ra)) ))
        if el < 0: el += 360
        cons = np.array([[0,"Pisces","PSC"],
            [29.05,"Aries","ARI"],[53.775,"Taurus","TAU"],[90.447,"Gemini","GEM"],
            [118.25,"Cancer","CNC"],[138.33,"Leo","LEO"],[174.1,"Virgo","VIR"],
            [218.129,"Libra","LIB"],[241.208,"Scorpio","SCO"],[248.205,"Ophiuchus","OPH"],
            [266.65,"Sagittarius","SAG"],[302.1996,"Capricornus","CAP"],[327.8,"Aquarius","AQR"],
            [351.972,"Pisces","PSC"]
            ])
        for i in range(0,14):
            if float(cons[i][0]) > el:
                i -= 1
                returnvalue = cons[i,1:3]
                break
    except:
        returnvalue=["---","---"]

    return returnvalue


#
#  DEFINE CLASSES
#
class waEarthPosition:
    def __init__(self,latitudeIn,longitudeIn,altitudeIn):
        self.latitude = latitudeIn
        self.longitude = longitudeIn
        self.altitude = altitudeIn
    
    def __str__(self):
        return f"{waDtoDMS(self.latitude)}, {waDtoDMS(self.longitude)}, {self.altitude} meters"
    
class waObserverLocation:
    def __init__(self,nameIn,waEarthPositionIn,timeZoneNameIn,UTCOffsetIn, DST_in: bool):
        self.name = nameIn
        self.EarthPosition = waEarthPositionIn
        self.timeZoneName = timeZoneNameIn
        self.UTCOffset = UTCOffsetIn
        self.DST = DST_in
    
    def __str__(self):
        return f"{self.name} {self.EarthPosition} {self.timeZoneName} ({self.UTCOffset}) DST: {self.DST}"

class waSessionTime():
    def __init__(self,dateIn: datetime.datetime,locationIn: waObserverLocation):
        self.date = dateIn
        self.location = locationIn
        if locationIn.DST:
            self.UTCOffset = locationIn.UTCOffset + 1
        else:
            self.UTCOffset = locationIn.UTCOffset
        self.utc = self.date - datetime.timedelta(hours=self.UTCOffset)
        self.JCentury = self.JCentury()
        
    def JD(self):
        #CALCULATE THE JULIAN DATE.  FROM JEAN MEEUS ASTRONOMICAL ALGORITHMS SECOND ADDITION CHAPTER 7.
        d = self.utc.day + (self.utc.hour + self.utc.minute/60 + self.utc.second/3600)/24
        m = self.utc.month
        y = self.utc.year

        if m < 3:
            m = m + 12
            y = y - 1
        
        a = math.floor(y/100)
        b = 2 - a + math.floor(a/4)
        JD = math.floor(365.25*(y+4716)) + math.floor(30.6001*(m+1)) + d + b - 1524.5;
        # self.JD = wjnaJulianDate(self.utc)
        return JD
    def JCentury(self):
        JCentury = float((self.JD() - 2451545.0)/36525)
        return JCentury
    def SiderealTime(self):
        #SIDEARL TIME AT GREENWICH
        jCent = (self.JD() - 2451545.0)/36525
        #jCent = self.JCentury()
        SiderealTime = ((280.46061837+360.98564736629*(self.JD() - 2451545)+0.000387933*math.pow(jCent,2)-math.pow(jCent,3)/38710000)) % 360; # VALUE IN DEGREES
        SiderealTime = 24*SiderealTime / 360; # VALUE IN HOURS
        return SiderealTime
    def LocalSiderealTime(self):
        #LOCAL SIDERAL TIME AT CURRENT LOCATION
        LocalSiderealTime =  (self.SiderealTime() + 24*self.location.EarthPosition.longitude/360) % 24; # WEST LON AS NEGATIVE.  VALUE IN HOURS.
        return LocalSiderealTime

class waSkyPosition:
    def __init__(self,raIn,decIn):
        self.ra = raIn
        self.dec = decIn
        self.EclipticLongitude = self.GetEclipticLongitude()
        self.EclipticConstellation = self.GetEclipticConstellation(self.EclipticLongitude)
    
    def __str__(self) -> str:
        return f"RA degrees: {self.ra}, DEC degrees: {self.dec}"
    
    def GetEclipticLongitude(self):
        epsilon0 = 23.43929111 # OBLIQUITY IN DEGREES OF EPOCH 2000.0 NOT ADJUSTED FOR PROCESSION
        try:
            el = waDegrees( math.atan2( \
                (math.sin(waRadians(self.ra)) * math.cos(waRadians(epsilon0)) + math.tan(waRadians(self.dec)) * math.sin(waRadians(epsilon0)) ),
                math.cos(waRadians(self.ra)) \
                ))
            if el < 0: el += 360
        except:
            el = -1 # INDICATION OFN AN ERROR
        return el
    
    def GetEclipticLongitudeFromRA(self):
        #THIS USES ONLY THE RA COMPONENT
        epsilon0 = 23.43929111 # OBLIQUITY IN DEGREES OF EPOCH 2000.0 NOT ADJUSTED FOR PROCESSION
        try:
            el = waDegrees( math.atan2( math.sin(waRadians(self.ra)) * math.cos(waRadians(epsilon0)), math.cos(waRadians(self.ra)) ))
            if el < 0: el += 360
        except:
            el = -1 # INDICATION OFN AN ERROR
        return el
    
    def GetEclipticConstellation(self, EclipticLongIn: float):
        cons = np.array([[0,"Pisces","PSC"],
            [29.05,"Aries","ARI"],[53.775,"Taurus","TAU"],[90.447,"Gemini","GEM"],
            [118.25,"Cancer","CNC"],[138.33,"Leo","LEO"],[174.1,"Virgo","VIR"],
            [218.129,"Libra","LIB"],[241.208,"Scorpio","SCO"],[248.205,"Ophiuchus","OPH"],
            [266.5,"Sagittarius","SAG"],[302.1996,"Capricornus","CAP"],[327.8,"Aquarius","AQR"],
            [351.972,"Pisces","PSC"]
            ])
        for i in range(0,14):
            if float(cons[i][0]) > EclipticLongIn:
                i -= 1
                break
        return cons[i,1:3]
    

class waSkyObject:
    def __init__(self,nameIn,skyPositionIn: waSkyPosition, sessionTimeIn: waSessionTime):
        self.name = nameIn
        self.SkyPosition = skyPositionIn
        self.SessionTime = sessionTimeIn
        self.LApparent = 0.0
        self.Events = {"Rise": 0, "Transit": 0, "Set": 0, "Dawn": 0, "Dusk": 0}

    def __str__(self) -> str:
        print(f"{self.name}")

    def GetPosition(self):
        # FUNCTION TO BE OVERIDDEN.  BY DEFAULT IT ONLY RETURNS THE CURRENT POSITION
        return waSkyPosition(self.SkyPosition.Ra,self.SkyPosition.dec)

    def GetEvents(self,skyPositionIn: waSkyPosition):
        # TODO:  MAKE PRECISE
        # RISE TRANSIT SET TIMES

        # TRANSIT TIME
        # time0 = waSessionTime(datetime.datetime(self.SessionTime.date.year,self.SessionTime.date.month,self.SessionTime.date.day,12,0,0),self.SessionTime.location)
        # localSiderealTime = time0.LocalSiderealTime()
        # m0 = skyPositionIn.ra/360 - localSiderealTime/24
        # transitTime = time0.date + datetime.timedelta(days=m0)

        # # RISE TIME
        # h0 = waRadians(-0.8333)
        # phi= waRadians(time0.location.EarthPosition.latitude)
        # dec = waRadians(skyPositionIn.dec)
        # H0 = waDegrees(math.acos( (math.sin(h0) - math.sin(phi) * math.sin(dec))/ \
        #                (math.cos(phi) *  math.cos(dec)) ) \
        #                 )
        # m1 = m0 - H0/360.0
        # riseTime = time0.date + datetime.timedelta(days=m1)

        # # SET TIME
        # m2 = m0 + H0/360.0
        # setTime = time0.date + datetime.timedelta(days=m2)

        #  # MORNING TWILIGHT TIME (DAWN)
        # h0 = waRadians(-18.0)
        # phi= waRadians(time0.location.EarthPosition.latitude)
        # dec = waRadians(skyPositionIn.dec)
        # H0 = waDegrees(math.acos( (math.sin(h0) - math.sin(phi) * math.sin(dec))/ \
        #                (math.cos(phi) *  math.cos(dec)) ) \
        #                 )
        # m1 = m0 - H0/360.0
        # dawnTime = time0.date + datetime.timedelta(days=m1)

        # # EVENING TWILIGHT TIME (DUSK)
        # m2 = m0 + H0/360.0
        # duskTime = time0.date + datetime.timedelta(days=m2)
        
        # return {"Rise": riseTime, "Transit": transitTime, "Set": setTime, "Dawn": dawnTime, "Dusk": duskTime}
        pass

class waSun(waSkyObject):
    def __init__(self, nameIn, sessionTimeIn: waSessionTime):
        super().__init__(nameIn, waSkyPosition(0,0), sessionTimeIn)
        self.name = "Sun"
        #self.SessionTime = sessionTimeIn
        self.SkyPosition = self.GetPosition(self.SessionTime)
        self.Events = self.GetEvents(self.SkyPosition)

    def GetPosition(self, sessionTimeIn: waSessionTime):
        # EQUATIONS FROM ASTRONOMICAL ALGORITHMS BY JEAN MEEUS, CHAPTER 25
        #waT = self.SessionTime.JCentury()
        waT = sessionTimeIn.JCentury
        # MEAN EQUINOX
        L0 = (280.46646 + 36000.76983 * waT + 0.0003032 * math.pow(waT,2)) % 360.0
        # MEAN ANOMALY
        M = (357.52911 + 35999.05029 * waT - 0.0001537 * math.pow(waT,2)) % 360.0
        # ECCENTRICTY
        e = 0.016780634 - 0.000042037 * waT - 0.0000001267 * math.pow(waT,2)
        # SUN'S EQUATION OF CENTER
        C = (1.914602 - 0.004817 * waT - 0.000014 * math.pow(waT,2) )* math.sin(waRadians(M)) + \
            (0.019993 - 0.000101 * waT) * math.sin(2*waRadians(M)) + \
            0.000289 * math.sin(3*waRadians(3*M))
        LTrue = L0 + C
        TrueAnomaly = M + C
        # SUN'S RADIUS VECTOR
        R = 1.000001018*(1-math.pow(e,2))/(1 + e*math.cos(waRadians(TrueAnomaly)))
        # APPARENT LONGITUDE
        Omega = 125.04 - 1934.136 * waT
        LApparent = LTrue - 0.00569 - 0.00478 * math.sin(waRadians(Omega))
        # ADJUSTED OBLIQUITY OF THE ECLIPTIC
        epsilon0 = 23.43929111 + ( -46.8150 * waT -0.00059 * math.pow(waT,2) + 0.001813 * math.pow(waT,3))/3600.0
        epsilon = epsilon0 + .00256 * math.cos(waRadians(Omega))
        numerator = math.cos( waRadians(epsilon) )*math.sin( waRadians(LApparent) )
        denominator = math.cos( waRadians(LApparent) )
        apparentRa = waDegrees( math.atan2(numerator,denominator) )
        apparentDec = waDegrees( math.asin(math.sin( waRadians(epsilon) ) * math.sin( waRadians(LApparent) )))

        return waSkyPosition(apparentRa,apparentDec)
    
    def GetEvents(self,skyPositionIn: waSkyPosition):
        # TODO:  MAKE PRECISE
        # RISE TRANSIT SET TIMES

        # TRANSIT TIME
        time0 = waSessionTime(datetime.datetime(self.SessionTime.date.year,self.SessionTime.date.month,self.SessionTime.date.day,12,0,0),self.SessionTime.location)
        localSiderealTime = time0.LocalSiderealTime()
        m0 = skyPositionIn.ra/360 - localSiderealTime/24
        transitTime = time0.date + datetime.timedelta(days=m0)

        # RISE TIME
        h0 = waRadians(-0.8333)
        phi= waRadians(time0.location.EarthPosition.latitude)
        dec = waRadians(skyPositionIn.dec)
        H0 = waDegrees(math.acos( (math.sin(h0) - math.sin(phi) * math.sin(dec))/ \
                       (math.cos(phi) *  math.cos(dec)) ) \
                        )
        m1 = m0 - H0/360.0
        riseTime = time0.date + datetime.timedelta(days=m1)

        # SET TIME
        m2 = m0 + H0/360.0
        setTime = time0.date + datetime.timedelta(days=m2)

         # MORNING TWILIGHT TIME (DAWN)
        h0 = waRadians(-18.0)
        phi= waRadians(time0.location.EarthPosition.latitude)
        dec = waRadians(skyPositionIn.dec)
        H0 = waDegrees(math.acos( (math.sin(h0) - math.sin(phi) * math.sin(dec))/ \
                       (math.cos(phi) *  math.cos(dec)) ) \
                        )
        m1 = m0 - H0/360.0
        dawnTime = time0.date + datetime.timedelta(days=m1)

        # EVENING TWILIGHT TIME (DUSK)
        m2 = m0 + H0/360.0
        duskTime = time0.date + datetime.timedelta(days=m2)
        
        return {"Rise": riseTime, "Transit": transitTime, "Set": setTime, "Dawn": dawnTime, "Dusk": duskTime}



class waMoon(waSkyObject):
    def __init__(self, nameIn, sessionTimeIn: waSessionTime):
        super().__init__(nameIn, waSkyPosition(0,0), sessionTimeIn)
        self.name = "Moon"
        self.SkyPosition = self.GetPosition2(self.SessionTime)
        self.IlluminatedFraction = round(self.GetIllumination(),4)
        self.Phases = self.GetPhases(self.SessionTime.date)

    def GetPosition(self, sessionTimeIn: waSessionTime):
        # THIS PROGRAM COMPUTES THE TIMES OF MOONRISE AND MOON- SET ANYWHERE IN THE WORLD.
        # FROM SKY & TELESCOPE, JULY, 1989, PAGE 78.

        # MOONRISE-MOONSET
        # B5 = Latitude, L5 = Longitude (West is negative)
        # H = Time Zone (hours ahead of UTC)    Dim B5, L5 As Double
 
        #boolFirstPass = bool(True)

        B5 = sessionTimeIn.location.EarthPosition.latitude # LATITUDE
        L5 = sessionTimeIn.location.EarthPosition.longitude # LONGITUDE
        H = -1 * sessionTimeIn.UTCOffset #PROGRAM USES HOURS BEHIND UTC

        Ma = np.empty([4,4])
        wHold = str("")
        # riseTime = sessionTimeIn.date; setTime = sessionTimeIn.date
        riseTime = datetime.datetime(1900,1,1,0,0,0); setTime = datetime.datetime(1900,1,1,0,0,0) # WJN - SET TO THESE DEFAULT VALUES FOR THE SITUATION WHERE THE MOON DOES NOT RISE OR SET
        waMoonRiseSet1 = ""
        
        P1 = np.pi; P2 = 2 * P1; R1 = P1 / 180
        K1 = 15 * R1 * 1.0027379
        strS = "Moonset "
        strR = "Moonrise "
        strM1 = "NO MOONRISE THIS DATE"
        strM2 = "NO MOONSET THIS DATE"
        strM3 = "MOON DOWN ALL DAY"
        strM4 = "MOON UP ALL DAY"

        L5 = L5 / 360
        Z0 = H / 24

        # CALENDAR --> JD
        # INPUT "Y,M,D ";Y,M,D
        Y = math.floor(sessionTimeIn.date.year)
        M = math.floor(sessionTimeIn.date.month)
        D = math.floor(sessionTimeIn.date.day) #WJN
        G = 1
        if Y < 1582: G = 0
        D1 = math.floor(D); F = D - D1 - 0.5
        J = -math.floor(7 * (math.floor((M + 9) / 12) + Y) / 4)
        if G != 0:
            S = np.sign(M - 9); a = math.fabs(M - 9)
            J3 = math.floor(Y + S * math.floor(a / 7))
        J3 = -math.floor((math.floor(J3 / 100) + 1) * 3 / 4)
        J = J + math.floor(275 * M / 9) + D1 + G * J3
        J = J + 1721027 + 2 * G + 367 * Y
        if F < 0:
            F = F + 1; J = J - 1
        t = (J - 2451545) + F

        # LST AT 0H ZONE TIME
        T0 = t / 36525
        S = 24110.5 + 8640184.813 * T0
        S = S + 86636.6 * Z0 + 86400 * L5
        S = S / 86400; S = S - math.floor(S)
        T0 = S * 360 * R1
        # LST AT CURRENT TIME ZONE
        t = t + Z0
        
        # POSITION LOOP
        for i in range(1,4):
            # FUNDAMENTAL ARGUMENTS
            L = 0.606434 + 0.03660110129 * t
            M = 0.374897 + 0.03629164709 * t
            F = 0.259091 + 0.0367481952 * t
            D = 0.827362 + 0.03386319198 * t
            n = 0.347343 - 0.00014709391 * t
            G = 0.993126 + 0.0027377785 * t
            L = L - math.floor(L); M = M - math.floor(M)
            F = F - math.floor(F); D = D - math.floor(D)
            n = n - math.floor(n); G = G - math.floor(G)
            L = L * P2; M = M * P2; F = F * P2
            D = D * P2; n = n * P2; G = G * P2
            V = 0.39558 * math.sin(F + n)
            V = V + 0.082 * math.sin(F)
            V = V + 0.03257 * math.sin(M - F - n)
            V = V + 0.01092 * math.sin(M + F + n)
            V = V + 0.00666 * math.sin(M - F)
            V = V - 0.00644 * math.sin(M + F - 2 * D + n)
            V = V - 0.00331 * math.sin(F - 2 * D + n)
            V = V - 0.00304 * math.sin(F - 2 * D)
            V = V - 0.0024 * math.sin(M - F - 2 * D - n)
            V = V + 0.00226 * math.sin(M + F)
            V = V - 0.00108 * math.sin(M + F - 2 * D)
            V = V - 0.00079 * math.sin(F - n)
            V = V + 0.00078 * math.sin(F + 2 * D + n)
            U = 1 - 0.10828 * math.cos(M)
            U = U - 0.0188 * math.cos(M - 2 * D)
            U = U - 0.01479 * math.cos(2 * D)
            U = U + 0.00181 * math.cos(2 * M - 2 * D)
            U = U - 0.00147 * math.cos(2 * M)
            U = U - 0.00105 * math.cos(2 * D - G)
            U = U - 0.00075 * math.cos(M - 2 * D + G)
            W = 0.10478 * math.sin(M)
            W = W - 0.04105 * math.sin(2 * F + 2 * n)
            W = W - 0.0213 * math.sin(M - 2 * D)
            W = W - 0.01779 * math.sin(2 * F + n)
            W = W + 0.01774 * math.sin(n)
            W = W + 0.00987 * math.sin(2 * D)
            W = W - 0.00338 * math.sin(M - 2 * F - 2 * n)
            W = W - 0.00309 * math.sin(G)
            W = W - 0.0019 * math.sin(2 * F)
            W = W - 0.00144 * math.sin(M + n)
            W = W - 0.00144 * math.sin(M - 2 * F - n)
            W = W - 0.00113 * math.sin(M + 2 * F + 2 * n)
            W = W - 0.00094 * math.sin(M - 2 * D + G)
            W = W - 0.00092 * math.sin(2 * M - 2 * D)
            #COMPUTE RA, DEC, DIST
            #WJN - RA(Radians) IS STORED IN A5, DEC(Radians) IS STORED IN D5 AND DISTANCE STORED IN R5
            S = W / math.sqrt(U - V * V)
            A5 = L + math.atan(S / math.sqrt(1 - S * S))
            S = V / math.sqrt(U); D5 = math.atan(S / math.sqrt(1 - S * S))
            R5 = 60.40974 * math.sqrt(U) # DISTANCE
            # if boolFirstPass:
            #     dReturnMoonRA = waDegrees(A5); dReturnMoonDec = waDegrees(D5) # 'WJN
            #     #dReturnJD = J #WJN
            #     boolFirstPass = False
            Ma[i, 1] = A5; Ma[i, 2] = D5; Ma[i, 3] = R5
            #print("DEBUG",waDecimalToDHMS(24*waDegrees(A5)/360,24,"HM"),waDecimalToDHMS(waDegrees(D5),360,"DM")) # DEBUG
            t = t + 0.5
        dReturnMoonRA = waDegrees(Ma[1,1]); dReturnMoonDec = waDegrees(Ma[1,2]) # 'WJN
        if Ma[2, 1] <= Ma[1, 1]:
            Ma[2, 1] = Ma[2, 1] + P2
        if Ma[3, 1] <= Ma[2, 1]:
            Ma[3, 1] = Ma[3, 1] + P2
        Z1 = R1 * (90.567 - 41.685 / Ma[2, 3])
        S = math.sin(B5 * R1); C = math.cos(B5 * R1)
        Z = math.cos(Z1); M8 = 0; W8 = 0
        A0 = Ma[1, 1]; D0 = Ma[1, 2]

        for C0 in range(0,24):  # WJN:  RANGE OBJECT MUST GO THROUGH ALL HOURS 0 - 23
            P = (C0 + 1) / 24
            F0 = Ma[1, 1]; F1 = Ma[2, 1]; F2 = Ma[3, 1]
            # 3-POINT INTERPOLATION
            a = F1 - F0; B = F2 - F1 - a
            F = F0 + P * (2 * a + B * (2 * P - 1))
            A2 = F
            F0 = Ma[1, 2]; F1 = Ma[2, 2]; F2 = Ma[3, 2]
            # 3-POINT INTERPOLATION
            a = F1 - F0; B = F2 - F1 - a
            F = F0 + P * (2 * a + B * (2 * P - 1))
            D2 = F
            # TEST AN HOUR FOR AN EVENT
            L0 = T0 + C0 * K1; L2 = L0 + K1
            if A2 < A0: A2 = A2 + 2 * P1
            H0 = L0 - A0; H2 = L2 - A2
            H1 = (H2 + H0) / 2 # HOUR ANGLE
            D1 = (D2 + D0) / 2 # DEC
            if C0 <= 0:
                V0 = S * math.sin(D0) + C * math.cos(D0) * math.cos(H0) - Z
            V2 = S * math.sin(D2) + C * math.cos(D2) * math.cos(H2) - Z
            if np.sign(V0) != np.sign(V2):
                V1 = S * math.sin(D1) + C * math.cos(D1) * math.cos(H1) - Z
                a = 2 * V2 - 4 * V1 + 2 * V0; B = 4 * V1 - 3 * V0 - V2
                D = B * B - 4 * a * V0
                
                if D >= 0:
                    D = math.sqrt(D)
                    if (V0 < 0 and V2 > 0): waMoonRiseSet1 = waMoonRiseSet1 + " " + strR
                    if (V0 < 0 and V2 > 0): M8 = 1
                    if (V0 > 0 and V2 < 0): waMoonRiseSet1 = waMoonRiseSet1 + " " + strS
                    if (V0 > 0 and V2 < 0): W8 = 1
                    E = (-B + D) / (2 * a)
                    if (E > 1 or E < 0): E = (-B - D) / (2 * a)
                    T3 = C0 + E + 1 / 120 # ROUND OFF
                    H3 = math.floor(T3); M3 = math.floor((T3 - H3) * 60)
                    #PUT THE EVENT DATE AND TIME IN THE RETURN VARIABLES (WJN)
                    #wHold = str(sessionTimeIn.date.year) + "/" + str(sessionTimeIn.date.month) + "/" + str(sessionTimeIn.date.day) + " "
                    wHold = sessionTimeIn.date.strftime("%Y/%m/%d")  + " "
                    if (V0 < 0 and V2 > 0): 
                        ReturnMoonRise = wHold + "{:02d}:{:02d}".format(H3,M3)
                        waMoonRiseSet1 = waMoonRiseSet1 + " " + ReturnMoonRise
                        riseTime = datetime.datetime(sessionTimeIn.date.year,sessionTimeIn.date.month,sessionTimeIn.date.day,H3,M3)
                    elif (V0 > 0 and V2 < 0):
                        ReturnMoonSet = wHold + "{:02d}:{:02d}".format(H3,M3)
                        waMoonRiseSet1 = waMoonRiseSet1 + " " + ReturnMoonSet
                        setTime = datetime.datetime(sessionTimeIn.date.year,sessionTimeIn.date.month,sessionTimeIn.date.day,H3,M3)
                    else:
                        pass
                    H7 = H0 + E * (H2 - H0)
                    N7 = -math.cos(D1) * math.sin(H7)
                    D7 = C * math.sin(D1) - S * math.cos(D1) * math.cos(H7)
                    A7 = math.atan(N7 / D7) / R1 # TODO Verify this does not need to be atan2
                    if D7 < 0: A7 = A7 + 180
                    if A7 < 0: A7 = A7 + 360
                    if A7 > 360: A7 = A7 - 360
                    waMoonRiseSet1 = waMoonRiseSet1 + ",  AZ= {} deg".format(int(A7))
            A0 = A2; D0 = D2; V0 = V2
        
        #   SPECIAL MESSAGE ROUTINE
        if (M8 == 0) and (W8 == 0):
            if V2 < 0: waMoonRiseSet1 += " " + strM3
            if V2 > 0: waMoonRiseSet1 += " " + strM4
        else:
            if M8 == 0: waMoonRiseSet1 += " " + strM1
            if W8 == 0: waMoonRiseSet1 += " " + strM2
        waMoonRiseSet1 = waMoonRiseSet1.strip() # GET RID OF THE LEADING WHITE SPACE
        self.Events = {"Rise": riseTime, "Set": setTime, "Description": waMoonRiseSet1}
        return waSkyPosition(dReturnMoonRA,dReturnMoonDec)
    
    def GetPosition2(self, sessionTimeIn: waSessionTime):
        # THIS PROGRAM COMPUTES THE TIMES OF MOONRISE AND MOON- SET ANYWHERE IN THE WORLD.
        # FROM SKY & TELESCOPE, JULY, 1989, PAGE 78.
        # UPGRATED BY W NEUBERT FOR IMPROVED ACCURACY USING JEAN MEEUSS'S ASTRONOMICAL ALGORITHMS, SECOND EDITION

        # MOONRISE-MOONSET
        # B5 = Latitude, L5 = Longitude (West is negative)
        # H = Time Zone (hours ahead of UTC)    Dim B5, L5 As Double
 
        #boolFirstPass = bool(True)

        B5 = sessionTimeIn.location.EarthPosition.latitude # LATITUDE
        L5 = sessionTimeIn.location.EarthPosition.longitude # LONGITUDE
        H = -1 * sessionTimeIn.UTCOffset #PROGRAM USES HOURS BEHIND UTC

        Ma = np.empty([4,4])
        wHold = str("")
        # riseTime = sessionTimeIn.date; setTime = sessionTimeIn.date
        riseTime = datetime.datetime(1900,1,1,0,0,0); setTime = datetime.datetime(1900,1,1,0,0,0) # WJN - SET TO THESE DEFAULT VALUES FOR THE SITUATION WHERE THE MOON DOES NOT RISE OR SET
        waMoonRiseSet1 = ""
        
        P1 = np.pi; P2 = 2 * P1; R1 = P1 / 180
        K1 = 15 * R1 * 1.00273790935 # WJN ADDED SIGNIFICANT DIGITS.  THIS CONVERTS TIME IN HOURS TO SIDERIAL TIME IN DEGREES
        strS = "Moonset "
        strR = "Moonrise "
        strM1 = "NO MOONRISE"
        strM2 = "NO MOONSET"
        strM3 = "MOON DOWN ALL DAY"
        strM4 = "MOON UP ALL DAY"

        L5 = L5 / 360
        Z0 = H / 24

        # CALENDAR --> JD
        # INPUT "Y,M,D ";Y,M,D
        Y = math.floor(sessionTimeIn.date.year)
        M = math.floor(sessionTimeIn.date.month)
        D = math.floor(sessionTimeIn.date.day) #WJN
        G = 1
        if Y < 1582: G = 0
        D1 = math.floor(D); F = D - D1 - 0.5
        J = -math.floor(7 * (math.floor((M + 9) / 12) + Y) / 4)
        if G != 0:
            S = np.sign(M - 9); a = math.fabs(M - 9)
            J3 = math.floor(Y + S * math.floor(a / 7))
        J3 = -math.floor((math.floor(J3 / 100) + 1) * 3 / 4)
        J = J + math.floor(275 * M / 9) + D1 + G * J3
        J = J + 1721027 + 2 * G + 367 * Y
        if F < 0:
            F = F + 1
            J = J - 1
        t = (J - 2451545) + F
        #t = sessionTimeIn.JD() - 2451545 + DJ + F + sessionTimeIn.UTCOffset/24 # WJN

        # LST AT 0H ZONE TIME
        T0 = t / 36525 # JULIAN CENTURY
        S = 24110.59 + 8640184.812866 * T0 + .093104 * math.pow(T0,2) - .0000062 * math.pow(T0,3) # WJN:  See Jeans Equation 12.2
        S = S + 86636.555368 * Z0 + 86400 * L5 # WJN:  Jeans Page 87
        S = S / 86400; S = S - math.floor(S)
        T0 = S * 360 * R1
        #T0 = 2*np.pi*sessionTimeIn.LocalSiderealTime()/24 + np.pi # WJN
        # LST AT CURRENT TIME ZONE
        t = t + Z0
        
        # POSITION LOOP
        for i in range(1,4):
            # FUNDAMENTAL ARGUMENTS
            L = 0.60643457694 + 0.036601101318 * t - 9.130334E-18 * math.pow(t,2) # MOON'S MEAN LONGITUDE, EQUATION 47.1
            M = 0.37489832333 + 0.036291647084 * t + 5.0558658602E-17 * math.pow(t,2) # MOON'S MEAN ANOMALY
            F = 0.25908915278 + 0.036748195112 * t - -2.113349E-17 * math.pow(t,2) # MOON'S ARGUMENT OF LATITUDE, EQUATION 47.5
            D = 0.82736164472 + 0.033863191984 * t - 1.0884565358E-17 * math.pow(t,2) # MEAN ELONGATION OF THE MOON, EQUATION 47.2
            n = 0.34734596639 - 0.000147093793 * t + 1.200373E-17 * math.pow(t,2) # MEAN ASCENDING NODE LONGITUDE, EQUATION 47.7
            G = 0.99313641444 + 0.002737778560 * t - 8.8839430312E-19 * math.pow(t,2) # SUN'S MEAN ANOMALY, EQUATION 47.3
            L -= math.floor(L); M -= math.floor(M)
            F -= math.floor(F); D -= math.floor(D)
            n -= math.floor(n); G -= math.floor(G)
            L *= P2; M *= P2; F *= P2
            D *= P2; n *= P2; G *= P2
            V = 0.39558 * math.sin(F + n) + \
                0.082 * math.sin(F) + \
                0.03257 * math.sin(M - F - n) + \
                0.01092 * math.sin(M + F + n) + \
                0.00666 * math.sin(M - F) - \
                0.00644 * math.sin(M + F - 2 * D + n) - \
                0.00331 * math.sin(F - 2 * D + n) - \
                0.00304 * math.sin(F - 2 * D) - \
                0.0024 * math.sin(M - F - 2 * D - n) + \
                0.00226 * math.sin(M + F) - \
                0.00108 * math.sin(M + F - 2 * D) - \
                0.00079 * math.sin(F - n) + \
                0.00078 * math.sin(F + 2 * D + n)
            U = 1 - 0.10828 * math.cos(M) - \
                0.0188 * math.cos(M - 2 * D) - \
                0.01479 * math.cos(2 * D) + \
                0.00181 * math.cos(2 * M - 2 * D) - \
                0.00147 * math.cos(2 * M) - \
                0.00105 * math.cos(2 * D - G) - \
                0.00075 * math.cos(M - 2 * D + G)
            W = 0.10478 * math.sin(M) - \
                0.04105 * math.sin(2 * F + 2 * n) - \
                0.0213 * math.sin(M - 2 * D) - \
                0.01779 * math.sin(2 * F + n) + \
                0.01774 * math.sin(n) + \
                0.00987 * math.sin(2 * D) - \
                0.00338 * math.sin(M - 2 * F - 2 * n) -\
                0.00309 * math.sin(G) - \
                0.0019 * math.sin(2 * F) - \
                0.00144 * math.sin(M + n) - \
                0.00144 * math.sin(M - 2 * F - n) - \
                0.00113 * math.sin(M + 2 * F + 2 * n) - \
                0.00094 * math.sin(M - 2 * D + G) - \
                0.00092 * math.sin(2 * M - 2 * D)
            #COMPUTE RA, DEC, DIST
            #WJN - RA(Radians) IS STORED IN A5, DEC(Radians) IS STORED IN D5 (EARTH RADII) AND DISTANCE STORED IN R5
            S = W / math.sqrt(U - V * V)
            A5 = L + math.atan(S / math.sqrt(1 - S * S))
            S = V / math.sqrt(U); D5 = math.atan(S / math.sqrt(1 - S * S))
            R5 = 60.40974 * math.sqrt(U) # WJN:  DISTANCE IN EARTH RADII
            Ma[i, 1] = A5; Ma[i, 2] = D5; Ma[i, 3] = R5
            Ma[i, 0] = t # WJN:  STORE THE TIME FOR POTENTIAL FUTURE USE IN POSITION AT A SPECIFIC TIME 
            #print("DEBUG",waDecimalToDHMS(24*waDegrees(A5)/360,24,"HM"),waDecimalToDHMS(waDegrees(D5),360,"DM")) # DEBUG
            t = t + 0.5
        dReturnMoonRA = waDegrees(Ma[3,1]) % 360; dReturnMoonDec = waDegrees(Ma[3,2]); dReturnT = t # 'WJN MOON'S GEOCENTRIC POSITION AT MIDNIGHT END OF DAY
        if Ma[2, 1] <= Ma[1, 1]:
            Ma[2, 1] = Ma[2, 1] + P2
        if Ma[3, 1] <= Ma[2, 1]:
            Ma[3, 1] = Ma[3, 1] + P2
        Z1 = R1 * (90.567 - 41.685 / Ma[2, 3])
        S = math.sin(B5 * R1); C = math.cos(B5 * R1)
        Z = math.cos(Z1); M8 = 0; W8 = 0
        A0 = Ma[1, 1]; D0 = Ma[1, 2]

        for C0 in range(0,24):  # WJN:  RANGE OBJECT MUST GO THROUGH ALL HOURS 0 - 23
            P = (C0 + 1) / 24
            F0 = Ma[1, 1]; F1 = Ma[2, 1]; F2 = Ma[3, 1]
            # 3-POINT INTERPOLATION FOR RA
            a = F1 - F0; B = F2 - F1 - a
            F = F0 + P * (2 * a + B * (2 * P - 1))
            A2 = F
            F0 = Ma[1, 2]; F1 = Ma[2, 2]; F2 = Ma[3, 2]
            # 3-POINT INTERPOLATION FOR DEC
            a = F1 - F0; B = F2 - F1 - a
            F = F0 + P * (2 * a + B * (2 * P - 1))
            D2 = F
            # TEST AN HOUR FOR AN EVENT
            L0 = T0 + C0 * K1; L2 = L0 + K1
            if A2 < A0: A2 = A2 + 2 * P1
            H0 = L0 - A0; H2 = L2 - A2
            H1 = (H2 + H0) / 2 # HOUR ANGLE
            D1 = (D2 + D0) / 2 # DEC
            if C0 <= 0:
                V0 = S * math.sin(D0) + C * math.cos(D0) * math.cos(H0) - Z
            V2 = S * math.sin(D2) + C * math.cos(D2) * math.cos(H2) - Z
            if np.sign(V0) != np.sign(V2):
                V1 = S * math.sin(D1) + C * math.cos(D1) * math.cos(H1) - Z
                a = 2 * V2 - 4 * V1 + 2 * V0; B = 4 * V1 - 3 * V0 - V2
                D = B * B - 4 * a * V0
                
                if D >= 0:
                    D = math.sqrt(D)
                    if (V0 < 0 and V2 > 0): waMoonRiseSet1 = waMoonRiseSet1 + " " + strR
                    if (V0 < 0 and V2 > 0): M8 = 1 # WJN:  M8 IS 1 IF A MOONRISE OCCURS AND 0 IF NOT
                    if (V0 > 0 and V2 < 0): waMoonRiseSet1 = waMoonRiseSet1 + " " + strS
                    if (V0 > 0 and V2 < 0): W8 = 1 # WJN:  W8 IS 1 IF A MOONSET OCCURS AND 0 IF NOT
                    E = (-B + D) / (2 * a)
                    if (E > 1 or E < 0): E = (-B - D) / (2 * a)
                    T3 = C0 + E + 1 / 120 # ROUND OFF
                    H3 = math.floor(T3); M3 = math.floor((T3 - H3) * 60)
                    #PUT THE EVENT DATE AND TIME IN THE RETURN VARIABLES (WJN)
                    #wHold = str(sessionTimeIn.date.year) + "/" + str(sessionTimeIn.date.month) + "/" + str(sessionTimeIn.date.day) + " "
                    wHold = sessionTimeIn.date.strftime("%Y/%m/%d")  + " "
                    if (V0 < 0 and V2 > 0): 
                        ReturnMoonRise = wHold + "{:02d}:{:02d}".format(H3,M3)
                        waMoonRiseSet1 = waMoonRiseSet1 + " " + ReturnMoonRise
                        riseTime = datetime.datetime(sessionTimeIn.date.year,sessionTimeIn.date.month,sessionTimeIn.date.day,H3,M3)
                    elif (V0 > 0 and V2 < 0):
                        ReturnMoonSet = wHold + "{:02d}:{:02d}".format(H3,M3)
                        waMoonRiseSet1 = waMoonRiseSet1 + " " + ReturnMoonSet
                        setTime = datetime.datetime(sessionTimeIn.date.year,sessionTimeIn.date.month,sessionTimeIn.date.day,H3,M3)
                    else:
                        pass
                    H7 = H0 + E * (H2 - H0)
                    N7 = -math.cos(D1) * math.sin(H7)
                    D7 = C * math.sin(D1) - S * math.cos(D1) * math.cos(H7)
                    A7 = math.atan(N7 / D7) / R1
                    if D7 < 0: A7 = A7 + 180
                    if A7 < 0: A7 = A7 + 360
                    if A7 > 360: A7 = A7 - 360
                    waMoonRiseSet1 = waMoonRiseSet1 + ",  AZ= {} deg".format(int(A7))
            A0 = A2; D0 = D2; V0 = V2
        
        #   SPECIAL MESSAGE ROUTINE
        if (M8 == 0) and (W8 == 0):
            if V2 < 0: waMoonRiseSet1 += " " + strM3
            if V2 > 0: waMoonRiseSet1 += " " + strM4
        else:
            if M8 == 0: waMoonRiseSet1 += " " + strM1
            if W8 == 0: waMoonRiseSet1 += " " + strM2
        waMoonRiseSet1 = waMoonRiseSet1.strip() # GET RID OF THE LEADING WHITE SPACE
        self.Events = {"Rise": riseTime, "Set": setTime, "Description": waMoonRiseSet1}
        return waSkyPosition(dReturnMoonRA,dReturnMoonDec)
    
    def GetIllumination(self):
        #  CHAPTER 48 OF ASTRONOMICAL ALGORITHMS, SECOND ADDTION BY JEAN MEEUS
        wTcent = float(self.SessionTime.JCentury)
        D = 297.8501921+445267.111403*wTcent-0.0018819*pow(wTcent,2)+pow(wTcent,3)/545868-pow(wTcent,4)/113065000 % 360 # MEAN ELONGATION OF THE MOON, EQUATION 47.2
        M = 357.5291092+35999.0502909*wTcent-0.0001536*pow(wTcent,2)+pow(wTcent,3)/24490000 % 360 # SUN'S MEAN ANOMALY, EQUATION 47.3
        M2 = 134.9633964+477198.8675055*wTcent+0.0087414*pow(wTcent,2)+pow(wTcent,3)/69699-pow(wTcent,4)/14712000 % 360 # MOON'S MEAN ANOMALY
        i = 180-D-6.289*math.sin(waRadians(M2))+2.1*math.sin(waRadians(M))-1.274*math.sin(waRadians(2*D-M2))- \
            0.658*math.sin(waRadians(2*D))-0.214*math.sin(waRadians(2*M2))-0.11*math.sin(waRadians(D)) # PHASE ANGLE, EQUATION 48.4
        k = (1 + math.cos(waRadians(i)))/2 # ILLUMINATED FRACTION OF THE MOON, EQUATION 48.1
        round(k,4)
        return k
    def GetPhases(self, dateIn: datetime.datetime):
        """Returns the phases of the moon and associated dates near the date and time provided.  See Jean Meeus, Chapter 40.
        Restults can be tested using https://aa.usno.navy.mil/data/MoonFraction."""
        #  GET THE UPCOMING PHASES.  SEE JEAN MEEUS CHAPTER 49
        k_to_phases = {0:"New", 0.25:"1st Quarter", 0.5:"Full", 0.75:"3rd Quarter", 1:"New2"}
        phases = []

        daynumber = dateIn.timetuple().tm_yday # DAY NUMBER OF THE YEAR
        year = dateIn.year + daynumber/365.25
        k = round(math.floor(4*(year - 2000.0)*12.3685)/4.0,2) - 0.25 # MAKES K HAVE FRACTIONAL VALUES THAT ARE MULTIPLES OF 0.25 OF A LUNAR CYCLE
        #k = math.floor(k)
        for i in range(0,6):
            T = k / 1236.85
            JDE = 2451550.09766+29.530588861*k - 0.00015437*T*T + 0.00000015*math.pow(T,3) + 0.00000000073*math.pow(T,4)
            JDE_delta = JDE - 2451550.09766859
            phasedate = datetime.datetime(2000,1,6,18,14) + datetime.timedelta(days=JDE_delta)
            phases.append([k_to_phases[k-math.floor(k)],phasedate])
            k += 0.25
        return phases

class waSession():
    def __init__(self, dateIn: datetime.datetime, siteLocationIn: waObserverLocation):
        self.Site = siteLocationIn
        self.SessionTime0 = waSessionTime(datetime.datetime(dateIn.year,dateIn.month,dateIn.day,23,59,59),siteLocationIn) # SESSION DAY AT MIDNIGHT
        self.SessionTime1 = waSessionTime(datetime.datetime(dateIn.year,dateIn.month,dateIn.day,12,0,0),siteLocationIn) # CURRENT DAY START OF SESSION
        self.SessionTime2 = waSessionTime(self.SessionTime1.date + datetime.timedelta(days=1),siteLocationIn) # NEXT DAY END OF SESSION
        #self.SessionTime2 = waSessionTime(datetime.datetime(dateIn.year,dateIn.month,dateIn.day + 1,12,0,0),siteLocationIn) # NEXT DAY END OF SESSION
        self.Sun1 = waSun("Sun",self.SessionTime1)
        self.Sun2 = waSun("Sun",self.SessionTime2)
        self.Moon1 = waMoon("Moon",self.SessionTime0)
        self.Moon2 = waMoon("Moon",self.SessionTime2)
        self.Events = self.GetEvents()
    
    def GetEvents(self):
        """The returns the key darkness events of a session based on the sun and moon."""
        # CALCULATE DURATION OF DARKNESS

        # SUN EVENTS
        Sun1 = waSun("Sun",self.SessionTime1) # SUN ON BEGINNING DAY
        Sun2 = waSun("Sun",self.SessionTime2) # SUN ON END DAY
        sun1Events = Sun1.Events
        sun2Events = Sun2.Events
        sunset1 = sun1Events["Set"]
        dusk1 = sun1Events["Dusk"]
        dawn2 = sun2Events["Dawn"]
        sunrise2 = sun2Events["Rise"]

        # MOON EVENTS
        Moon1 = waMoon("Moon",self.SessionTime1)
        Moon2 = waMoon("Moon",self.SessionTime2)
        moon1Events = Moon1.Events
        moon2Events = Moon2.Events
        moonrise1 = moon1Events["Rise"]
        moonset1 = moon1Events["Set"]
        moonrise2 = moon2Events["Rise"]
        moonset2 = moon2Events["Set"]
        
        darkness_start = 0; darkness_end = 0
        
        # DARKNESS BASED ON EVENT TIMES
        if (moonrise1>dusk1):
            darkness_start = dusk1
            darkness_end = moonrise1
            moonriseLatest = moonrise1
            moonsetLatest = moonset2
            print("Session events condition 1")
        elif (moonset1>dusk1):
            darkness_start = moonset1
            darkness_end = min(dawn2,moonrise2)
            moonriseLatest = moonrise2
            moonsetLatest = moonset1
            print("Session events condition 2")
        elif (moonrise2<dawn2):
            darkness_start = max(dusk1,moonset1)
            darkness_end = moonrise2
            moonriseLatest = moonrise2
            moonsetLatest = moonset1
            print("Session events condition 3")
        elif (moonset2<dawn2):
            darkness_start = moonset2
            darkness_end = min(dawn2,moonrise2)
            moonriseLatest = moonrise2
            moonsetLatest = moonset2
            print("Session events condition 4")
        elif moonrise1 < dusk1 and moonset2 > dawn2:
            if moonrise1 > moonset1:
                darkness_start = dusk1
                darkness_end = dusk1
                moonriseLatest = moonrise1
                moonsetLatest = moonset2
                print("Session events condition 5")
            else:
                darkness_start = dusk1
                darkness_end = dawn2
                moonriseLatest = moonrise1
                moonsetLatest = moonset2
                print("Session events condition 6")
        else:
            darkness_start = dusk1
            darkness_end = dawn2 # DARKNESS STARTS AND ENDS AT DUSK SINCE MOON IS UP ALL NIGHT
            moonriseLatest = moonrise2
            moonsetLatest = moonset1
            print("Session events condition 7")

        
        #  EVENTS BASED ON SEQUENCE
        
        wEvents = []
        # if moonrise1 > moonset1:
        #     if moonrise1 > dusk1:
        #         print("Session condition B1")
        #         wEvents.append(["Moonset1",moonset1,False])
        #         wEvents.append(["Dusk",dusk1,False])
        #         wEvents.append(["Moonrise1",moonrise1,True])
        #         darkness_start = moonrise1; darkness_end = moonrise1
        #         moonriseLatest = moonrise1
        #     else:
        #         print("Session condition B2")
        #         wEvents.append(["Moonset1",moonset1,False])
        #         wEvents.append(["Moonrise1",moonrise1,True])
        #         wEvents.append(["Dusk",dusk1,False])
        #         darkness_start = dusk1
        #         moonriseLatest = moonrise1;moonsetLatest = moonset2
        # else:
        #     if moonset1 > dusk1:
        #         print("Session condition B3")
        #         wEvents.append(["Moonrise1",moonrise1,True])
        #         wEvents.append(["Dusk",dusk1,False])
        #         wEvents.append(["Moonset1",moonset1,False])
        #         darkness_start = moonset1
        #         moonsetLatest = moonset1;moonriseLatest = moonrise2
        #     else:
        #         print("Session condition B4")
        #         wEvents.append(["Moonrise1",moonrise1,True])
        #         wEvents.append(["Dusk",dusk1,False])
        #         wEvents.append(["Moonset1",moonset1,False])
        #         darkness_start = dusk1
        #         moonsetLatest = moonset1;moonriseLatest = moonrise1
        
        # if moonrise2 < moonset2:
        #     if moonrise2 < dawn2:
        #         print("Session condition B5")
        #         wEvents.append(["Moonrise2",moonrise2,True])
        #         wEvents.append(["Dawn",dawn2,False])
        #         wEvents.append(["Moonset1",moonset2,False])
        #         darkness_end = moonrise2
        #         moonriseLatest = moonrise2
        #     else:
        #         print("Session condition B6")
        #         wEvents.append(["Dawn",dawn2,False])
        #         wEvents.append(["Moonrise2",moonrise2,True])
        #         wEvents.append(["Moonset2",moonset2,False])
        #         darkness_end = dawn2
        #         moonriseLatest = moonrise2;
        # else:
        #     if moonset2 < dawn2:
        #         print("Session condition B7")
        #         wEvents.append(["Moonset2",moonset2,False])
        #         wEvents.append(["Dawn",dawn2,False])
        #         wEvents.append(["Moonrise2",moonrise2,True])
        #         darkness_start = moonset2;darkness_end = dawn2
        #         moonsetLatest = moonset2;moonriseLatest = moonrise1
        #     else:
        #         print("Session condition B8")
        #         wEvents.append(["Dawn",dawn2,False])
        #         wEvents.append(["Moonset2",moonset2,False])
        #         wEvents.append(["Moonrise2",moonrise2,True])
        #         darkness_end = moonrise1
        #         moonriseLatest = moonrise1

        print(wEvents)
        if (darkness_end > darkness_start):
            darkness_duration = darkness_end - darkness_start
            darkness_duration = darkness_duration.total_seconds()/(3600) # HOURS
        else:
            darkness_duration = 0

        sessionEvents = {"Sunset": sunset1, "Dusk": dusk1, "Dawn": dawn2, "Sunrise": sunrise2, 
                         "Moonrise": moonriseLatest, "Moonset": moonsetLatest,
                         "Darkness from": darkness_start, "Darkness to": darkness_end, "Duration": darkness_duration
                         }
        return sessionEvents