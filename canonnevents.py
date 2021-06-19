import threading
import requests
import sys
import json
try:
    # for Python2
    from Tkinter import Frame
    import Tkinter as tk
    from urllib import quote_plus
except ImportError:
    # for python 3
    import tkinter as tk
    from urllib.parse import quote_plus
    from tkinter import Frame


class whiteListGetter(threading.Thread):
    def __init__(self,callback):
        threading.Thread.__init__(self)
        self.callback=callback

    def run(self):
        #debug("getting whiteList")
        url="https://us-central1-canonn-api-236217.cloudfunctions.net/whitelist"
        r=requests.get(url)

        if not r.status_code == requests.codes.ok:
            print("whiteListGetter {} ".format(url))
            print(r.status_code)
            print(r.json())
            results=[]
        else:
           results=r.json()

        self.callback(results)

class whiteListSetter(threading.Thread):

    def __init__(self,cmdr, is_beta, system, station, entry, state,x,y,z,body,lat,lon,client):
        threading.Thread.__init__(self)
        self.cmdr=cmdr
        self.system=system
        self.is_beta=is_beta
        self.station=station
        self.body=body
        self.entry=entry
        self.state=state
        self.x=x
        self.y=y
        self.z=z
        self.lat=state.get("Latitude")
        self.lon=state.get("Longitude") 
        self.client=client
        self.odyssey=state.get("Odyssey")

    def run(self):
        url="https://us-central1-canonn-api-236217.cloudfunctions.net/postEvent"
        #url="http://192.168.0.72:8080"
        
        data = {
            "gameState": {
                "systemName": self.system,
                "systemCoordinates": [self.x, self.y, self.z],
                "bodyName": self.body,
                "station": self.station,
                "latitude": self.lat,
                "longitude": self.lon,
                "clientVersion": self.client,
                "isBeta": self.is_beta,
                "platform": "PC",
                "odyssey": self.odyssey
            },
            "rawEvent": self.entry,
            "eventType": self.entry.get("event"),
            "cmdrName": self.cmdr
        }
        
        
        r = requests.post(url, data=json.dumps(data, ensure_ascii=False).encode('utf8'),
        headers={"content-type": "application/json"})
        
        
        if not r.status_code == requests.codes.ok:
            print("whiteListSetter {} ".format(url))
            print(r.status_code)
            #print(r.json())
            results=[]
        else:
            try:
                #results=r.json()
                print(r)
            except Exception as e:
                print(e)
        



'''
  Going to declare this aa a frame so I can run a time
'''
class whiteList(Frame):

    whitelist = []
    systems={}

    def __init__(self, parent):
        Frame.__init__(
            self,
            parent
        )

    '''
        if all the keys match then return true
    '''
    @classmethod
    def matchkeys(cls,event,entry):

        ev=json.loads(event)
        for key in ev.keys():
            if not entry.get(key) == ev.get(key):
                return False

        return True


    @classmethod
    def journal_entry(cls,cmdr, is_beta, system, station, entry, state,client):
        try:
            #cache the the star positions
            if entry.get("StarSystem") and entry.get("StarPos"):
                print("HH caching star")
                print(entry.get("StarPos"))
                cls.systems[entry.get("StarSystem")]=entry.get("StarPos")
            
            for event in whiteList.whitelist:

                if cls.matchkeys(event.get("definition"),entry) and system:
                    if cls.systems.get(system):
                        print("HH Getting star")
                        print(cls.systems.get(system))
                        x,y,z=cls.systems.get(system)
                    else:
                        x,y,z=(None,None,None)
                    print("whiteListSetter")
                    whiteListSetter(cmdr, is_beta, system, station, entry, state,x,y,z,state.get("Body"),None,None,client).start()
        except Exception as e:
            print(e)


    '''
      We will fetch the whitelist on the hour
    '''

    def fetchData(self):
        whiteListGetter(self.whiteListCallback).start()
        self.after(1000*60*60*24,self.fetchData)


    def whiteListCallback(self,data):
        whiteList.whitelist=data
