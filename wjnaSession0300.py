#####################################################################################
####    wjnaSession01-02.py  Astrometry Test File
####    Version 2, June 4, 2023 Revised July 14, 2023
####    Version 3, Nov 16, 2023:  Import wjnaAstrometry instead of including the entire file
####      Corrected end of darkness message
####      Edited Moon rise, set and location routine to have clear variable names and use code from other classes
####    William Neubert
#####################################################################################

__version__ = "3.09"
__author__ = "William Neubert"

#  PROCESSING DIRECTIVES

#WJN_TEMPRHSENSOR = bool(False)

# IMPORT MODULES
# import time
import datetime
import math
import numpy as np
import PySimpleGUI as sg
import wjnaAstrometry0200 as wa

try:
  import wjnSHT30reader as wjnenv
  WJN_TEMPRHSENSOR = bool(True)
except:
  WJN_TEMPRHSENSOR = bool(False)
  print("Temperature Humidity Sensor:  ",WJN_TEMPRHSENSOR)

try:
  import wjnGPSReader0100 as wgps
  WJN_GPS = bool(True)
except:
  WJN_GPS = bool(False)
  print("GPS:  ",WJN_GPS)


#####################################################################################
####  INITIALIZE
#####################################################################################
global locationSelected

Configuration, LocationList = wa.wjnaLoadSettings()
versionMessage = __version__
wjnaGlobalConfig = {"GPSTimeOffset":False, "GPSTimeOffsetValue":datetime.timedelta(seconds=0.0)}
locationSelected = LocationList[0]
global session1
#
#  FUNCTIONS
#
def waTimeNow():
   """This return the current time, using the system time, plus an application defined offset.
   This is useful for use when the system does not have a real time clock, and having a GPS reference time."""
   wTimeNow = datetime.datetime.now()
   if wjnaGlobalConfig["GPSTimeOffset"] == True:
       wTimeNow += wjnaGlobalConfig["GPSTimeOffsetValue"]
   return wTimeNow

def waStartSession(startDateIn: datetime.datetime, locationIn: wa.waObserverLocation): # FROM THE SELECTED START DATE DETERMIN THE SESSION START DATE
  session = wa.waSession(startDateIn, locationIn)
  #sessionEvents = session.Events
  if startDateIn.hour < 12  and startDateIn < session.Sun1.Events["Rise"]:
    startDateIn = startDateIn - datetime.timedelta(days=1)
    session = wa.waSession(startDateIn, locationIn)
    print("Session start date reset to the previous evening")
  return session

def waPrintSessionText(sessionIn: wa.waSession):
    print(">>> ASTRONOMICAL OBERVING SESSION <<<")
    print(versionMessage)
    print("Astrometry engine ",wa.__version__)
    print(sessionIn.Site)
    # sessionDateSelected = sessionIn.SessionTime0
    sessionEvents = sessionIn.Events

    print("\n>> Start Date At Midnight")
    print("Local Time: "+sessionIn.SessionTime0.date.isoformat())
    print("UTC: ",sessionIn.SessionTime0.utc)
    print("JD: ",sessionIn.SessionTime0.JD())
    print("LST: "+wa.waHtoHMS(sessionIn.SessionTime0.LocalSiderealTime())," (" + wa.waMeridianEclipticalConstellation(sessionIn.SessionTime0.LocalSiderealTime())[0] + ")")

    # SUN
    #skyPosition1 = waSkyPosition(0,0)
    print("\n>> "+sessionIn.Sun1.name)
    print(sessionIn.Sun1.SkyPosition, sessionIn.Sun1.SkyPosition.EclipticConstellation[0])
    print("Geocentric:   ",wa.waDtoHMS(sessionIn.Sun1.SkyPosition.ra), wa.waDtoDMS(sessionIn.Sun1.SkyPosition.dec))
    print("Topocentric:  ",wa.waDtoHMS(sessionIn.Sun1.SkyPositionTopocentric.ra), wa.waDtoDMS(sessionIn.Sun1.SkyPositionTopocentric.dec))
    print("Sunset: ",sessionEvents["Sunset"].strftime("%H:%M"), "  Dusk: ",sessionEvents["Dusk"].strftime("%H:%M"))
    print("Morning Twilight: ",sessionEvents["Dawn"].strftime("%H:%M"), "  Sunrise: ",sessionEvents["Sunrise"].strftime("%H:%M"))

    #MOON
    moon1 = sessionIn.Moon1
    print("\n>> "+moon1.name," at start date midnight")
    print("Geocentric:   ",wa.waDtoHMS(moon1.SkyPosition.ra), " ", wa.waDtoDMS(moon1.SkyPosition.dec), moon1.SkyPosition.EclipticConstellation[0])
    print("Topocentric:  ",wa.waDtoHMS(moon1.SkyPositionTopocentric.ra), " ", wa.waDtoDMS(moon1.SkyPositionTopocentric.dec), moon1.SkyPosition.EclipticConstellation[0])
    print("Illumination:  {0:.0f}%".format(100*moon1.IlluminatedFraction))
    sessionMoonEvents = moon1.Events
    print("Rise: ",sessionMoonEvents["Rise"].strftime("%H:%M"), "  Set: ",sessionMoonEvents["Set"].strftime("%H:%M"))
    print(sessionMoonEvents["Description"])
    moon2 = sessionIn.Moon2
    print("\n>> "+moon2.name," at end date midnight")
    # print(wa.waDtoHMS(moon2.SkyPosition.ra), " ", wa.waDtoDMS(moon2.SkyPosition.dec), moon2.SkyPosition.EclipticConstellation[0])
    print("Geocentric:   ",wa.waDtoHMS(moon2.SkyPosition.ra), " ", wa.waDtoDMS(moon2.SkyPosition.dec), moon2.SkyPosition.EclipticConstellation[0])
    print("Topocentric:  ",wa.waDtoHMS(moon2.SkyPositionTopocentric.ra), " ", wa.waDtoDMS(moon2.SkyPositionTopocentric.dec), moon2.SkyPosition.EclipticConstellation[0])
    print("Illumination:  {0:.0f}%".format(100*moon2.IlluminatedFraction))
    sessionMoonEvents2 = moon2.Events
    print("Rise: ",sessionMoonEvents2["Rise"].strftime("%H:%M"), "  Set: ",sessionMoonEvents2["Set"].strftime("%H:%M"))
    print(sessionMoonEvents2["Description"])


    durationText = wa.waDecimalToDHMS(sessionEvents["Duration"],24,"HM")
    print("Duration of Darkness: ",durationText)
    return

def waSessionUpdateNow(windowIn: sg.Window): # UPDATE THE "NOW" FIELDS OF THE WINDOW
    """Updates the current time values."""
    sessionTimeNow= wa.waSessionTime(waTimeNow(),session1.Site)
    windowIn['-LOCALTIME-'].update(sessionTimeNow.date.strftime("%X"))
    windowIn['-UTC-'].update(sessionTimeNow.utc.strftime("%H:%M"))
    windowIn['-LST-'].update(wa.waDecimalToDHMS(sessionTimeNow.LocalSiderealTime(),24,"HM") + \
          " (" + wa.waMeridianEclipticalConstellation(sessionTimeNow.LocalSiderealTime())[1] + ")")
    
    # TIME INTERVAL TO NEXT SESSION EVENT
    now = sessionTimeNow.date
    darknessStart = session1.Events["Darkness from"]
    darknessEnd = session1.Events["Darkness to"]
    darknessSunrise = session1.Events["Sunrise"]
    intervalString = ""
    message = ""
    if now <= darknessStart:
       interval = darknessStart - now
       message = "Darkness begins in "
       intervalString = wa.waTimeDeltaToDHMS(interval.total_seconds(),"DHM")
    elif now < darknessEnd:
      interval = darknessEnd - now
      message = "Darkness ends in "
      intervalString = wa.waTimeDeltaToDHMS(interval.total_seconds(),"DHM")
    elif now > darknessEnd and now <= darknessSunrise:
      interval = darknessSunrise - now
      message = "Sunrise in "
      intervalString = wa.waTimeDeltaToDHMS(interval.total_seconds(),"DHM")
    else:
       message = ""; intervalString = ""
    windowIn['-TIME_TO_DARKNESS_MESSAGE-'].update(message)
    windowIn['-TIME_TO_DARKNESS-'].update(intervalString)

    return

def waSessionNextDay(sessionIn: wa.waSession):
  # DETERMINE IF SESSION NEEDS TO ADVANCE TO THE NEXT DAY
  if datetime.datetime.now() > sessionIn.Events["Sunrise"]:
    update = True
  else:
    update = False
  return update


def  wjnaGetWeatherData(windowIn: sg.Window): # UPDATE THE WEATHER DATA
  """Update the weather data table."""
  if WJN_TEMPRHSENSOR:
    try:
      weather = sensor1.GetWeatherData()
      tableWeatherData = [[weather["Temperature"], weather["Relative Humidity"], weather["Dew Point"]]]
      windowIn['-WEATHERTABLE-'].update(values = tableWeatherData)
    except:
      pass
  return


def waGenerateMultidayLayout(sessionDateIn: wa.waSessionTime, locationIn: wa.waObserverLocation):
    """Creates darkness duration data for multiple days."""
    tableEvents = []
    for d in range(0,7):
        sessionA = wa.waSession(sessionDateIn + datetime.timedelta(days=d),locationIn)
        tableEvents.append([
           sessionA.SessionTime0.date.strftime("%Y-%m-%d %a"),
           sessionA.Events["Darkness from"].strftime("%H:%M"),
           sessionA.Events["Darkness to"].strftime("%H:%M"),
           wa.waDecimalToDHMS(sessionA.Events["Duration"],24,"HM"),
           "{0:}  {1:.0f}%".format(sessionA.Moon1.SkyPosition.EclipticConstellation[1], 100*sessionA.Moon1.IlluminatedFraction)
           ])

    return tableEvents

def wjnaGetGPSPosition():
    """This function gets GPS data, displays it and enables setting the current position and time to match the GPS."""
    global locationSelected

    # utcOffset = -6;dst = True
    utcOffset = locationSelected.UTCOffset;dst = locationSelected.DST
    if dst: 
      zoneoffset = datetime.timedelta(hours=utcOffset + 1)
    else:
      zoneoffset = datetime.timedelta(hours=utcOffset) 
    print("GPS: ",WJN_GPS)
    if WJN_GPS:
        gpsLayout = [
            [sg.Text("Time:  "), sg.Text("", key = "-GPSTIME-")],
            [sg.Text("Longitude:  "),sg.Text("", key="-GPSLON-"),sg.Text("Latitude:  "),sg.Text("", key="-GPSLAT-")],
            [sg.Text("Altitude:  "),sg.Text("", key="-GPSALT-"),sg.Text("HDOP:  "),sg.Text("", key="-GPSHDOP-")],
            [sg.Text("(no fix)", key="-GPSMESSAGE1-")],
            [sg.Text("UTC offset: "),sg.Spin([i for i in range(-12,12)], key='-UTC-',initial_value = utcOffset,enable_events=True, font = wLargeFont),
             sg.Text("  "),sg.Checkbox("DST",key='-DST-', enable_events=True, default=False)
             ],
            [sg.Button('Ok'),sg.Button('Cancel')]
            ]
        GPSWindow = sg.Window("GPS Location",gpsLayout,size=(600,300))
        try:
            wgps.wjngStartGPS()
        except:
            pass
        i = int(0); offsetSum = datetime.timedelta(seconds=0);
        while True:
            event, values = GPSWindow.read(timeout=400) # THE TIMEOUT MUST BE SHORT ENOUGH THAT THERE AREN'T NMEA SENTANCES WAITING IN THE BUFFER, AFFECTION REPORTED TIME.
            if event == sg.WIN_CLOSED or event == 'Cancel':
                break
            if event == 'Ok':
                locationSelected = wa.waObserverLocation("GPS",wa.waEarthPosition(gpsdata['lat'],gpsdata['lon'],gpsdata['alt']),'?',
                    values['-UTC-'],values['-DST-']) 
                print(locationSelected)
                wjnaGlobalConfig["GPSTimeOffsetValue"] = offset
                wjnaGlobalConfig["GPSTimeOffset"] = True
                print("Time offset:  ",str(offset))
                break
            try:
                gpsdata = wgps.wjngGetGPSData()
                i += 1
                reftime = datetime.datetime.now()
                GPSWindow['-GPSTIME-'].update(gpsdata['time'])
                GPSWindow['-GPSLON-'].update(wa.waDecimalToDHMS(gpsdata['lon'],360,"DMS"))
                GPSWindow['-GPSLAT-'].update(wa.waDecimalToDHMS(gpsdata['lat'],360,"DMS"))
                GPSWindow['-GPSALT-'].update("{0:.1f}".format(gpsdata['alt']))
                GPSWindow['-GPSHDOP-'].update("{0:.1f}".format(gpsdata['hdop']))
                offsetSum += datetime.datetime.strptime(gpsdata['time'],"%Y-%m-%d %H:%M:%S") - reftime
                offset = (offsetSum / i + zoneoffset)
                offsetSec = round(offset.total_seconds(),1)
                offsetString = "{}days {:02}h {:02}m {:02}s".format(math.floor(offsetSec // 86400),
                  math.floor(offsetSec % 86400 // 3600), 
                  math.floor(offsetSec % 3600 // 60), offsetSec % 60)
                wGPSMessage = "GPS Clock versus System Clock Offset:  "+offsetString
                GPSWindow['-GPSMESSAGE1-'].update(wGPSMessage)
            except:
                i = int(0); offsetSum = datetime.timedelta(seconds=0);
                wGPSMessage = "No fix"
                GPSWindow['-GPSMESSAGE1-'].update(wGPSMessage)
                pass
        GPSWindow.close()
    else:
        pass
    return


# START THE WEATHER SENSOR IF PRESENT
if WJN_TEMPRHSENSOR:
  try:
    global sensor1; sensor1 = wjnenv.wjn_sht30()
    global sensor1_firstpass; sensor1_firstpass = True
    print(sensor1.name,":  ",sensor1.status)
  except:
    WJN_TEMPRHSENSOR = False

#
#  MAIN UPDATE LOOP
#
wjnContinue = True
sessionStartDate = datetime.datetime.now()
while wjnContinue:
  #
  # START THE SESSION
  #
  session1 = waStartSession(sessionStartDate, locationSelected)
  session1Events = session1.Events
  durationText = wa.waDecimalToDHMS(session1Events["Duration"],24,"HM")
  waPrintSessionText(session1)
  #
  # GUI
  #
  wSmallFont = ("Arial",14)
  wMediumFont = ("Arial",18)
  wLargeFont = ("Arial",20)
  wHighlightFont = ("Arial Bold",20)
  sg.theme('DarkRed')
  sg.set_options(font=wSmallFont)

  sessionMidnightText = "At Midnight:  JD {jdtext:.4f}".format(jdtext=session1.SessionTime0.JD()) + "    LST " + \
    wa.waDecimalToDHMS(session1.SessionTime0.LocalSiderealTime(),24,"HMS") + \
      " (" + wa.waMeridianEclipticalConstellation(session1.SessionTime0.LocalSiderealTime())[1] + ")"

  tableHeadings = ['Sunset','Dusk','Dawn','Sunrise','Const']
  tableEvents = [[
    session1Events["Sunset"].strftime("%H:%M"),
    session1Events["Dusk"].strftime("%H:%M"),
    session1Events["Dawn"].strftime("%H:%M"),
    session1Events["Sunrise"].strftime("%H:%M"),
    session1.Sun1.SkyPosition.EclipticConstellation[1]
      ]]
  tableMoonHeadings = ['Moonrise','Moonset','Const','Illum%']
  tableMoonEvents = [[
    session1Events["Moonrise"].strftime("%m/%d %H:%M"),
    session1Events["Moonset"].strftime("%m/%d %H:%M"),
    session1.Moon1.SkyPosition.EclipticConstellation[1],
    "%3.0f" % (100.0*session1.Moon1.IlluminatedFraction)
      ]]
  tableMoonPhasesHeadings = ['Phase','Date (Local Time)']
  phases = session1.Moon1.Phases
  tableMoonPhasesData = []
  for i in range(0,5):
    tableMoonPhasesData.append([phases[i][0],phases[i][1].strftime("%B %d   %H:%M")])

  tableWeatherHeadings = ["  T(C)  ","  RH%  ","  DP(C)  "]
  tableWeatherData = [[0,0,0]]

  layout = [ 
      [sg.Input(session1.SessionTime0.date.strftime("%Y-%m-%d"),key = '-DATE-', size = (10,1), font=("Arial",14), text_color='Yellow', enable_events=True),
        sg.Text(sessionMidnightText)],
      [sg.Table(values=tableEvents, headings=tableHeadings, 
                header_text_color = 'yellow',
                auto_size_columns=True,
                justification = 'center',
                num_rows=1,
                hide_vertical_scroll = True
                ),
          sg.Table(values=tableMoonEvents, headings=tableMoonHeadings, 
              header_text_color = 'black',
              auto_size_columns=True,
              justification = 'center',
              num_rows=1,
              hide_vertical_scroll = True
              )],
      [sg.Text("Darkness from: "),sg.Text(session1.Events["Darkness from"].strftime("%H:%M"),font=wHighlightFont),
      sg.Text(" to "),sg.Text(session1.Events["Darkness to"].strftime("%H:%M"),font=wHighlightFont),
      sg.Text(" Duration: "),sg.Text(durationText,font=wHighlightFont)],
      [sg.HSeparator()],
      [sg.Text("Local Time Now:"),sg.Text("",key="-LOCALTIME-",font=wHighlightFont),
        sg.Text("UTC:"),sg.Text("",key="-UTC-",font=wHighlightFont),
        sg.Text("LST:"),sg.Text("",key="-LST-",font=wHighlightFont) 
        ],
      [sg.Text("",key = '-TIME_TO_DARKNESS_MESSAGE-'),sg.Text("",key = "-TIME_TO_DARKNESS-",font = wHighlightFont)],
      [sg.HSeparator()],
      [sg.Table(values = tableWeatherData, headings=tableWeatherHeadings, font = wMediumFont,
                header_text_color = 'yellow',
                auto_size_columns=True,
                justification = 'center',
                num_rows=1,
                key="-WEATHERTABLE-",
                enable_events=False,
                hide_vertical_scroll = True,
                visible = WJN_TEMPRHSENSOR
                )
        ]
      ]

  moon_layout = [
    [sg.Text(session1.Moon1.Events["Description"])],
    [sg.Text(session1.Moon2.Events["Description"])],
    [sg.Table(values=tableMoonPhasesData, headings=tableMoonPhasesHeadings,
              header_text_color = 'black',
              auto_size_columns=True,
              justification = 'center',
              num_rows=5,
              hide_vertical_scroll = True
              )
    ]
  ]

  weather_layout = [
    [sg.Checkbox("Log data", key='-LOG_WEATHER_DATA-')]
    ]

  multiday_layout = [
     [sg.Table(values=waGenerateMultidayLayout(sessionStartDate, locationSelected), headings=['Date','From','To','Duration',"Moon"],
        header_text_color = 'black',
        auto_size_columns=True,
        justification = 'left',
        num_rows=7,
        hide_vertical_scroll = True
        )
     ]
  ]
  
  LocationNameList = []
  for i in LocationList:
     LocationNameList.append(i.name)
  location_layout = [
    [sg.Text("Current location:  "),sg.Text(session1.Site)],
    [sg.Text("Select a location:  ")],
    [sg.Combo(LocationNameList, background_color='dark red',enable_events = True, key='-LOCATIONCOMBO-')],
    [sg.Checkbox("DST",key='-DST1-', default=locationSelected.DST, enable_events=True)],
    [sg.Button('Get GPS Data', key = '-GPS-',visible = WJN_GPS)],
    [sg.Checkbox("Enable offset to GPS clock",key='-GPSCLOCKOFFSET-', default=False, enable_events=True, visible = WJN_GPS)]
    ]

  tabgroup_layout = [
      [sg.Tab("Darkness Time", layout)],
      [sg.Tab("Moon",moon_layout)],
      [sg.Tab("Weather",weather_layout)],
      [sg.Tab("Outlook",multiday_layout)],
      [sg.Tab("Location", location_layout)]
    ]

  window_layout = [[sg.TabGroup(tabgroup_layout)],
      [sg.CalendarButton('Date', key = '-CALENDAR-', target = '-DATE-', format= '%Y-%m-%d'),
       sg.Button('Refresh', key = '-REFRESH-'),
       sg.Button('Close')]
      ]
  window = sg.Window("Darkness Calculator "+versionMessage+":  "+str(session1.Site),window_layout, size=(800,400))

  #
  # CURRENT TIMES UPDATE LOOP
  #
  while True:
    event, values = window.read(timeout=1000)
    # print(event,values)
    if event == sg.WIN_CLOSED or event == 'Close':
      wjnContinue = False 
      break
    elif event == '-DATE-' or event == '-REFRESH-':
      try:
        newStartDate = values['-DATE-'] + " 12:00:00"
        sessionStartDate = datetime.datetime.strptime(newStartDate, '%Y-%m-%d %H:%M:%S')
        break
      except:
        break
    elif event == '-LOCATIONCOMBO-':
      try:
        selection = values['-LOCATIONCOMBO-']
        locationSelected = LocationList[LocationNameList.index(selection)]
        print("New location selected")
        break
      except:
        pass
    elif event == '-DST1-':
      locationSelected.DST = values['-DST1-']
      # window.close()
      break # FORCE RECALCULATION
    elif event == '-GPS-':
      try:
        wjnaGetGPSPosition()
        values['-GPSCLOCKOFFSET-']=True
        print("New location selected")
        break
      except:
        pass
    elif event == '-GPSCLOCKOFFSET-':
      wjnaGlobalConfig["GPSTimeOffset"] = values['-GPSCLOCKOFFSET-']
    else:
       pass    
    
    if waSessionNextDay(session1):
      sessionStartDate = datetime.datetime.now()
      break

    waSessionUpdateNow(window)
    
    if WJN_TEMPRHSENSOR: 
      tableWeatherData = wjnaGetWeatherData(window)
    
    # window.refresh()
  window.close()
window.close()
