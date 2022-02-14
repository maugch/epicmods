import requests
from bs4 import BeautifulSoup
from os.path import join,exists
from time import time as ttime,sleep
import json
from datetime import datetime


import logging
import logging.config

from workshopcrawler import WorkshopCrawler


logger = logging.getLogger(__name__)

'''
	Json structure
    ver:
    downloadPath:
    paths:
        appId: path
    apps:
		appId:
			name:
            modpath:
			mods:
				modId:
					name:
					date:
					requirements:
						id
'''

class EpicConfig:

    def __init__(self,filename_data):
        self._data = {}
        self._fileData = filename_data
        self._wscrawler = WorkshopCrawler()
        self._version = '0.1'
    
    def load(self):
        if exists(self._fileData):
            with open(self._fileData, 'r') as f:
                self._data = json.load(f)
        else:
            print("file {} doesn't exists.".format(self._fileData))
            self._data = {}
            self._data['version'] = self._version
            self._data['downloadPath'] = ''
        

    def save(self):
        with open(self._fileData, 'w') as outfile:
            json.dump(self._data, outfile,indent=4)

    def checkDownloadPath(self):
        '''check that the download path exists (only)'''
        if not self._data['downloadPath']:
            return False
        if self._data['downloadPath'] == '':
            return False
        if exists(self._data['downloadPath']):
            return True
        else:
            return False

    def setDownloadPath(self,dp):
        if exists(dp):
            self._data['downloadPath'] = dp

    def getDownloadPath(self):
        return self._data['downloadPath']

    def getAppPathForMods(self,appId):
        ''' get the installation path for mods of a game'''
        if appId in self._data['paths'].keys():
            return self._data['paths'][appId]
        return ''

    '''
    def getModInfo(self,modId):
        for appId,app in self._data['apps'].items():
            if modId in app['mods'].keys():
                self.getModPath(appId)
    '''
    def getAppId(self,modId):
        '''get app id from mod id'''
        for appId,app in self._data['apps'].items():
            if modId in app['mods'].keys():
                return appId
        return 0

    def getAllModIds(self):
        '''get all modId of all apps'''
        result = []
        for app in self._data['apps'].values():
            for modId in app['mods'].keys():
                result.append(modId)
        return result

    def _setModMainData(self,appId,appName,modId,data):
        
        if 'apps' not in self._data :
            self._data['apps'] = {}

        if appId not in self._data['apps'].keys():
            # new app
            self._data['apps'][appId] = {}
            
        #else:
            # old app

        self._data['apps'][appId]['name'] = appName

        if 'mods' not in self._data['apps'][appId]:
            self._data['apps'][appId]['mods'] = {}

        if modId not in self._data['apps'][appId]['mods'].keys():
            self._data['apps'][appId]['mods'][modId] = {}

        self._data['apps'][appId]['mods'][modId] = data

    def getIdsOfEmptyPaths(self):
        result = []
        if 'paths' not in self._data:
            self._data['paths'] = {}
        for k in self._data['apps'].keys():
            if k not in self._data['paths'].keys():
                result.append(k)
        return result

    def setPath(self,appId,newPath):
        if appId not in self._data['paths'].keys():
            self._data['paths'][appId]= {}
        self._data['paths'][appId] = newPath
            

    def getAppName(self,appId):
        if appId in self._data['apps'].keys():
            return self._data['apps'][appId]['name']
        return 'unknown?'

    def getAppsIds(self):
        return self._data['apps'].keys()

    def getAppMods(self,appId):
        if appId not in self._data['apps'].keys():
            return None
        return self._data['apps'][appId]['mods']

    def _getDate(self,date1):
        fmt1 = '%d %b @ %I:%M%p'
        fmt2 = '%d %b, %Y @ %I:%M%p'
        try:
            res1 = datetime.strptime(date1,fmt1)
        except ValueError:
            res1 = datetime.strptime(date1,fmt2)

        if res1.year < 1940:
            today = datetime.now()
            res1 = res1.replace(year=today.year)
        return res1

    def is_new(self,newMod,oldMod):
        ''' return True if the first date is more recent than the second'''

        res1 = self._getDate(newMod['date']) 
        res2 = self._getDate(oldMod['date']) 
        if res1 > res2:
            return True
        else:
            return False
