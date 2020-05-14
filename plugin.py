# LoRa Packet Forwarder Plugin for Domoticz : connector to easily configure a LoRa Packet Forwarder to Domoticz
# Date : 05/2020
# https://github.com/Di-Ny/LoRaPacketForwarderDomoticzConfigurator
# Author: DiNy
#
#   Goal : 
#       - Start and configure the LoRa Packet Forwarder on Orange Pi
#       - Allow differents Semtech chips soldered on the box 
#
#   Concept : 
#       - Reconfigure the Packet forwarder for it's own LoRa devices and region (change SF, BW, frequency)
#       - Editing the settings will kill the LoRaPktFwrd process
#       - Restart the process, decode the gateway ID and the update the variable
#       - The heartbeat will chek that the process is still running, and if not try to restart it
#       - If a wrong config is put, the plugin will revert to the previous working config file
#
#   Requirements : 
#       - Install LoRa Packet Forwarder https://github.com/zhgzhg/LoRaPacketForwarder
#               The installation tree should be the same as : 
#                   [USER PATH]=/home/pi/LoRaPacketForwarder (for example) 
#                                   [USER PATH]/config.json
#                                   [USER PATH]/Makefile
#                                   [USER PATH]/LoRaPktFwrd
#                                   [USER PATH]/...
#
#       - Create and configure the first instance of the config.json 
#       - Compile and check "sudo /.LoRaPktFwrd" is working
#       - Python 3.5+ with packages : psutil, shutil
#
#   TODO :
#       - Waiting to add more parameters to be able to add interface (eth0, ppp0), individual inputs for Coding Rate, Lat, Lon, Alt, mail, ...
#       - Can be adapted to different packets forwarder with a bit of work 
# 
# 
# Credits : 
#   Based on the LoRa Packet Forwarder https://github.com/zhgzhg/LoRaPacketForwarder
#   Based on the Base Plugin Example
# License : CC BY-NC-SA
"""
<plugin key="lorapacketforwarder" name="LoRa Packet Forwarder" author="DiNy" version="0.0.1" wikilink="" externallink="">
    <description>
        <b>LoRa Packet Forwarder Configurator</b><br/>
        Important : the choosen LoRa packet forwarder is a 1-channel packet forwarder, it works great on an Orange Pi. It does not yet supports downlinks. <br/>
        This plugin is only a "config.json"-configurator for the packet forwarder, aiming to facilitate the reprogrammation of the LoRa chip from Domoticz, without editing the files.<br/>
        The aim of a packet forwarder is just to redirect LoRa messages to an UDP. It does not decrypts nor store them. Currently either ChirpStack (on localhost) or TheThingsNetwork are supported. These servers will allow a user to add his own LoRa devices, and then be able to decrypt the messages. <br/>
        <b>Parameters :</b>
        <ul style="list-style-type:square">
            <li>Address: the packet frowarder will send the LoRa messages to a Server. This is either an onboard ChirpStack server, or a cloud based TheThingsNetwork server.</li>
            <li>Frequency: The user should check that the frequency matches the LoRaWAN specifications in his country AND the Onboard chip soldered. Note that SX1276 sold for 868 MHz will have very poor performance at 434MHz. The hardware is built for a specific frequency! </li>
            <li>OnBoard chip: Select the soldered chip. RFM95W = SX1276. </li>
            <li>LoRa Configuration: 1-channel only. Check that it matches the LoRaWAN specifications for the choosen frequency. Alternativeley, non-LoRaWAN band are experimental only (greater range)  </li>
            <li>Lat, Lon, Alt: This is used if the gateway is declared in TTN or ChirpStack </li>
        </ul>
    </description>
    <params>        
        <param field="Mode1" label="Packet forwarder path" width="300px" required="true" default="/home/pi/LoRaPacketForwarder"/>
        <param field="Address" label="LoRa Server" required="true" width="200px">
            <options>
                <option label="Localhost" value="127.0.0.1" default="true"/>
                <option label="TTN EU" value="router.eu.thethings.network" />
                <option label="TTN US" value="router.us.thethings.network"/>
            </options>
        </param>
        <param field="Port" label="LoRa Server port" required="true" default="1700" width="75px"/>
        <param field="Mode2" label="OnBoard Chip" required="true" width="200px">
            <options>
                <option label="SX1272" value="SX1272"/>
                <option label="SX1273" value="SX1273" />
                <option label="SX1276" value="SX1276" default="true"/>
                <option label="SX1277" value="SX1277" />
                <option label="SX1278" value="SX1278" />
                <option label="RFM95" value="RFM95" />
                <option label="RFM96" value="RFM96" />
                <option label="RFM97" value="RFM97" />
                <option label="RFM98" value="RFM98" />
            </options>
        </param>
        <param field="Mode3" label="Frequency" required="true" width="200px">
            <options>
                <option label="EU868 - 868.100MHz" value="868.1" default="true"/>
                <option label="EU868 - 868.300MHz" value="868.3"/>
                <option label="EU868 - 868.500MHz" value="868.5"/>
                <option label="EU868 - 867.100MHz" value="867.1"/>
                <option label="EU868 - 867.300MHz" value="867.3"/>
                <option label="EU868 - 867.500MHz" value="867.5"/>
                <option label="EU868 - 867.700MHz" value="867.7"/>
                <option label="EU868 - 867.900MHz" value="867.9"/>
                <option label="EU868 - 868.800MHz" value="868.5"/>
                <option label="US915 - 903.900MHz" value="903.9"/>
                <option label="US915 - 904.100MHz" value="904.1"/>
                <option label="US915 - 904.300MHz" value="904.3"/>
                <option label="US915 - 904.500MHz" value="904.5"/>
                <option label="US915 - 904.900MHz" value="904.9"/>
                <option label="US915 - 905.100MHz" value="905.1"/>
                <option label="US915 - 905.300MHz" value="905.3"/>
                <option label="US915 - 904.600MHz" value="904.6"/>
            </options>
        </param>
        <param field="Mode4" label="LoRa Configuration" required="true" width="200px">
            <options>
                <option label="LoRaWAN DR0: SF12,BW125,CR4/5" value="0" default="true"/>
                <option label="LoRaWAN DR1: SF11,BW125,CR4/5" value="1"/>
                <option label="LoRaWAN DR2: SF10,BW125,CR4/5" value="2"/>
                <option label="LoRaWAN DR3: SF9,BW125,CR4/5" value="3"/>
                <option label="LoRaWAN DR4: SF8,BW125,CR4/5" value="4"/>
                <option label="LoRaWAN DR5: SF7,BW125,CR4/5" value="5"/>
                <option label="LoRaWAN DR6: SF7,BW250,CR4/5" value="6"/>
                <option label="DR0 Noise:            SF12,BW125, CR4/7" value="7"/>
                <option label="SF12 LongRange:       SF12,BW62.5,CR4/5" value="8"/>
                <option label="SF12 LongRange Noise: SF12,BW62.5,CR4/7" value="9"/>
                <option label="SF12 Ext LR:          SF12,BW31.25,CR4/5" value="10"/>
                <option label="SF12 Ext LR Noise:    SF12,BW31.25,CR4/7" value="11"/>
                <option label="DR2 Noise:            SF10,BW125,CR4/7" value="12"/>
                <option label="SF10 LongRange:       SF10,BW62.5,CR4/5" value="13"/>
                <option label="SF10 LongRange Noise: SF10,BW62.5,CR4/7" value="14"/>
                <option label="SF8  LongRange:       SF8,BW62.5,CR4/5" value="15"/>
            </options>
        </param>
        <param field="Mode5" label="Latitude,Longitude,Altitude,Mail" width="200px" required="true" default="43.0,0.3,10,contact@gmail.com"/>
        <param field="Mode6" label="Debug" width="75px">
            <options>
                <option label="True" value="Debug"/>
                <option label="False" value="Normal" default="true" />
            </options>
        </param>
    </params>
</plugin>
"""
import Domoticz
import json
import time
import datetime

import os
import psutil
import subprocess
import sys
from constants import *
from shutil import copy2

class BasePlugin:
    enabled = False

    def onStart(self):
        #Get the variables
        self.debugging = Parameters["Mode6"].strip()
        self.dt= str(datetime.datetime.now().strftime("%Y%m%d-%H%M%S"))
        self.path = Parameters["Mode1"].strip()
        if self.path.endswith('/'):
            self.path = self.path[:-1]
        self.serv = Parameters["Address"].strip()
        self.port = Parameters["Port"].strip()
        self.chip = Parameters["Mode2"].strip()
        self.freq = Parameters["Mode3"].strip()
        lora_config = DR_2_SFBW_EU868[ Parameters["Mode4"].strip() ]
        self.sf = lora_config[0]
        self.bw = lora_config[1]
        self.cr = lora_config[2]
        box_info = Parameters["Mode5"].strip()
        if (box_info.count("'") >=3 ):
            self.lat = box_info.split(",")[0]
            self.lon = box_info.split(",")[1]
            self.alt = box_info.split(",")[2]
            self.mail = box_info.split(",")[3]
        else:
            self.lat = "43.0"
            self.alt = "10"
            self.lon = "0.3"
            self.mail = "contact@gmail.com"
        #HARDCODED
        self.interface = ""#wait for more parameters to come 

        if self.debugging == "Debug":
            Domoticz.Debugging(2)
        DumpConfigToLog()
        #Debug data values 
        self.DumpLoRaToLog()
        Domoticz.Log("LoRa Packet Forwarder Plugin started")
        #ReConfigure the config.json 
        success = self.reWriteConfigFile()
        if not success:
            Domoticz.Log("Reconfigure config.json --> Failed")
            return 0
        #Create the Box ID variable if not exist 
        if len(Devices) == 0:
            #Create
            Domoticz.Device(Name="LoRa Gateway ID", TypeName="Text", Unit=GW_UNIT_ID, DeviceID="gatewayid").Create()
        #Start the process 
        success = self.startProcess()
        if success == 1:
            #remove the backup file
            os.system("sudo rm "+self.backupfile)
        else:
            Domoticz.Log("Trying to revert the config file...")
            copy2(self.backupfile,self.path+"/config.json")
            success = self.startProcess()
        #Update the ID
        if success:
            #update the box ID
            Devices[GW_UNIT_ID].Update(sValue=str(self.box_id), nValue=0)


    def reWriteConfigFile(self):
        #backup file 
        file = self.path+"/config.json"
        backup = self.path+"/config.bakDZ."+self.dt
        self.backupfile=backup
        copy2(file,backup)
        #open file 
        f= open(self.path+"/config.json","r+")
        config_file = json.load(f)
        Domoticz.Debug(str(config_file))

        #Re parameter
        config_file['ic_model']=self.chip
        config_file['spreading_factor']=int(self.sf)
        config_file['carrier_frequency_mhz']=float(self.freq)
        config_file['bandwidth_khz']=float(self.bw)
        config_file['coding_rate']=int(self.cr)
        config_file['latitude']=float(self.lat)
        config_file['longtitude']=float(self.lon)
        config_file['altitude_meters']=int(self.alt)
        #enable the right sevrer
        flag_enabled = 0
        Domoticz.Debug("Found "+str(len(config_file["servers"]))+" servers: ")
        for s in config_file["servers"]:
            debug_serv_name="- ["
            if str(s["address"]) == str(self.serv):
                s["enabled"]=True
                s["port"]=int(self.port)
                debug_serv_name+="X"
                flag_enabled = 1
            else:
                s["enabled"]=False
                debug_serv_name+=" "
            debug_serv_name+="]  "+str(s["address"])+":"+str(s["port"])
            Domoticz.Debug(debug_serv_name)
        if not flag_enabled:
            Domoticz.Log("Alert : no server enabled, Something is wrong with the config file")
            return 0
        #Save the new file 
        with open(self.path+"/config.json", '+w', encoding='utf-8') as j:
            json.dump(config_file, j, ensure_ascii=False, indent=4)
        return 1

    def startProcess(self):
        ##STARTs the process in monitoring mode. If success, then it starts it without log file
        #create dump file with rights 
        path=self.path
        log_file=path+"/nohup.out"
        os.chmod(log_file, 0o777)
        lf = open(log_file,"w")
        Domoticz.Debug("Starting the LoRaPacketForwarder")
        myPopen = subprocess.Popen(["./LoRaPktFwrd"], cwd=path, stdout=lf, stderr=subprocess.STDOUT)
        #wait for the initialisation and parse the output
        time.sleep(1)
        #hill the app to update the nohup.out
        os.system("sudo killall LoRaPktFwrd")
        time.sleep(1)
        lf.close()
        success = 0
        out = open(log_file, "r").read()

        if("LoRa chip setup success" in out):
            if ("ID (EUI-64): " in out):
                Domoticz.Log("LoRa chip setup success")
                Domoticz.Debug("ID found")
                self.box_id=str(out).split("ID (EUI-64): ")[1].split("\n")[0]
                Domoticz.Log("LoRaWAN Gateway ID: "+self.box_id)
                success = 1
        if not success :
            Domoticz.Log("LoRaPacketForwarder Failed to start")
            Domoticz.Debug("Log file :")
            Domoticz.Debug(str(out))
            return success
        
        #os.system("rm "+log_file)
        Domoticz.Debug("Restarting without nohup log")
        os.system("cd "+path+" && sudo nohup ./LoRaPktFwrd "+self.interface+" >/dev/null 2>&1 &")
        return success
        
    def onStop(self):
        Domoticz.Log("Killing LoRaPktFwrd process")
        os.system("sudo killall LoRaPktFwrd")
        time.sleep(2)

    def onConnect(self, Connection, Status, Description):
        Domoticz.Debug("onConnect called")

    def onMessage(self, Connection, Data):
        Domoticz.Debug("onMessage called")

    def onCommand(self, Unit, Command, Level, Hue):
        Domoticz.Debug("onCommand called for Unit " + str(Unit) + ": Parameter '" + str(Command) + "', Level: " + str(Level))

    def onNotification(self, Name, Subject, Text, Status, Priority, Sound, ImageFile):
        Domoticz.Debug("Notification: " + Name + "," + Subject + "," + Text + "," + Status + "," + str(Priority) + "," + Sound + "," + ImageFile)

    def onDisconnect(self, Connection):
        Domoticz.Debug("onDisconnect called")

    def onHeartbeat(self):
        PID = "NO PROCESS"
        for proc in psutil.process_iter(['pid', 'name', 'username']):
            if proc.info['name']=='LoRaPktFwrd':
                PID = str(proc.info['pid'])
        Domoticz.Debug("Heartbeat LoRaPktFwrd (PID: "+PID+")")
        if PID == "NO PROCESS":
            self.onStop()
            time.sleep(2)
            self.onStart()


    def DumpLoRaToLog(self):
        #Just a log of the main parameters 
        Domoticz.Debug("Path:           " + str(self.path))
        Domoticz.Debug("serv:           " + str(self.serv))
        Domoticz.Debug("chip:           " + str(self.chip))
        Domoticz.Debug("freq:           " + str(self.freq))
        Domoticz.Debug("sf:             " + str(self.sf))
        Domoticz.Debug("bw:             " + str(self.bw))
        Domoticz.Debug("cr:             4/" + str(self.cr))
        Domoticz.Debug("interface:      " + str(self.interface))
        Domoticz.Debug("lat:            " + str(self.lat))
        Domoticz.Debug("lon:            " + str(self.lon))
        Domoticz.Debug("alt:            " + str(self.alt))

global _plugin
_plugin = BasePlugin()

def onStart():
    global _plugin
    _plugin.onStart()

def onStop():
    global _plugin
    _plugin.onStop()

def onConnect(Connection, Status, Description):
    global _plugin
    _plugin.onConnect(Connection, Status, Description)

def onMessage(Connection, Data):
    global _plugin
    _plugin.onMessage(Connection, Data)

def onCommand(Unit, Command, Level, Hue):
    global _plugin
    _plugin.onCommand(Unit, Command, Level, Hue)

def onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile):
    global _plugin
    _plugin.onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile)

def onDisconnect(Connection):
    global _plugin
    _plugin.onDisconnect(Connection)

def onHeartbeat():
    global _plugin
    _plugin.onHeartbeat()

    # Generic helper functions
def DumpConfigToLog():
    for x in Parameters:
        if Parameters[x] != "":
            Domoticz.Debug( "'" + str(x) + "':'" + str(Parameters[x]) + "'")
    Domoticz.Debug("Device count: " + str(len(Devices)))
    for x in Devices:
        Domoticz.Debug("Device:           " + str(x) + " - " + str(Devices[x]))
        Domoticz.Debug("Device ID:       '" + str(Devices[x].ID) + "'")
        Domoticz.Debug("Device Name:     '" + Devices[x].Name + "'")
        Domoticz.Debug("Device nValue:    " + str(Devices[x].nValue))
        Domoticz.Debug("Device sValue:   '" + Devices[x].sValue + "'")
        Domoticz.Debug("Device LastLevel: " + str(Devices[x].LastLevel))
    return