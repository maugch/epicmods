from fileinput import filename
from sys import argv
from os.path import exists,isfile,join
from os import listdir
from shutil import move,make_archive
from zipfile import ZipFile

from epicconfig import EpicConfig
from workshopcrawler import WorkshopCrawler

class ModChecker:

    def __init__(self,config_filename='config.json'):
        self._downlod_url = 'https://steamcommunity.com/sharedfiles/filedetails/?id='
        self.wscrawler = WorkshopCrawler()
        self._configFile = config_filename

        self.config = EpicConfig(self._configFile)
        self.config.load()
        
    def save(self):
        self.config.save()

    def checkConfiguration(self):
        ''' return configuration status'''
        if not self.config.checkDownloadPath():
            print('download Path not set. Please set it.')
            return False

        idlist = self.config.getIdsOfEmptyPaths()
        if len(idlist) > 0:
            print('Game paths for mods not set. Please set it.')
            return False
    
    def setDownloadPath(self):
        print('Please set a temporary directory where your will store temporarily your zip files.')
        p = input()
        self.config.setDownloadPath(p)

    def setAppPath(self,appId,appName):
        print('Please set the directory where the mods for {} will be installed:'.format(appName))
        newPath = input()
        if exists(newPath):
            res = self.config.setAppPath(appId,newPath)
        else:
            print('invalid path.')

    def checkUpdatesOnline(self,automatic = False):
        ''' checks for updates online. Doesn't save.'''
        print("Checking for updates online...")
        result = []
        appIDs= self.config.getAppsIds()
        if not appIDs:
            print('No game configured. Please add a Mod first. It will add a game automatically.')
            return
        for appId in appIDs:
            appName = self.config.getAppName(appId)
            print('Checking {} : {}'.format(appId,appName))
            for modId,mod in self.config.getAppMods(appId).items():
                newMod,_,_ = self.wscrawler.fetchModInfo(modId)
                if self.config.is_new(newMod,mod):
                    print('New version: mod {} {} dates n:{} o:{}'.format(modId,newMod['name'],newMod['date'],mod['date']))
                    self.config._setModMainData(appId,appName,modId,newMod)
                    result.append(modId)
                else:
                    print('Old version: mod {} {} date: n:{} o:{}'.format(modId,newMod['name'],newMod['date'],mod['date']))

        if len(result) > 0:
            print("please download the following mods from https://steamworkshopdownloader.io/ and copy them in your download dir: {}".format(self.config.getDownloadPath()))
            if not automatic:
                print("restart with the option -i.")
            for r in result:
                print('{}{}'.format(self._downlod_url,r))
            print()

    def addMod(self,url):
        modId = url.partition('id=')[2].partition('&')[0]
        self.addModId(modId)
    
    def addModId(self,modId):
        ''' add a Module and check if a path already exists for that game'''
        modInfo,appId,appName = self.wscrawler.fetchModInfo(modId)
        print('adding mod to known list: {}'.format(modInfo['name']))
        self.config._setModMainData(appId,appName,modId,modInfo)
        for k in modInfo['requirements'].keys():
            modInfo2,_,_ = self.wscrawler.fetchModInfo(k)
            print('adding mod (required) to known list: {}'.format(modInfo2['name']))
            self.config._setModMainData(appId,appName,k,modInfo2)

        if not self.config.appHasPath(appId):
            self.setAppPath(appId,appName)

    def installUpdates(self):
        print('Installing updates...')
        allMods = self.config.getAllModIds()
        dlpath = self.config.getDownloadPath()
        onlyfiles = [f for f in listdir(dlpath) if isfile(join(dlpath, f))]
        if len(onlyfiles) == 0:
            print("no updates found.")
        for mf in onlyfiles:
            if '_' in mf:
                modId = mf.partition('_')[0]
                if modId in allMods:
                    self._installMod(modId,dlpath,mf)
                else:
                    print("{} is not a mod or is not configured.".format(mf))
        
    def _installMod(self,modId,zipPath,fileName):
        appId = self.config.getAppId(modId)
        mods_root_path = self.config.getAppPathForMods(appId)
        if mods_root_path == '' :
            print ("invalid path for mods in game found. {} {}".format(appId,mods_root_path))
        elif appId == 0:
            print('invalid mod or game not configured. {}'.format(appId))
        else:
            self._backupOldMod(appId,modId,mods_root_path)
            try:
                src = join(zipPath,fileName)
                final_destination = join(mods_root_path,modId)
                print("extractiong mod in its path: {} {}".format(src,mods_root_path))
                move(src,join(mods_root_path,fileName))
                with ZipFile(join(mods_root_path,fileName),"r") as f:
                    f.extractall(final_destination)
                #todo: delete zips
                print('zip not deleted.')
            except Exception as e:
                print(e)

    def _backupOldMod(self,appId,modId,mods_root_path):
        old_mod_path = join(mods_root_path,modId)
        if exists(old_mod_path):
            print('creating a backup of {}'.format(old_mod_path))
            #todo: do not overwrite old backups?
            make_archive(old_mod_path,'zip',mods_root_path,modId)
        else:
            print('no old installation exists : {}'.format(old_mod_path))

def main(argv):
    
    print("Mods checker for Epic games")
    #mc = ModChecker('test.json')
    mc = ModChecker()
    mc.checkConfiguration()

    if len(argv) == 1:
        print('Use -h for help.')
        #mc.checkUpdatesOnline()
    elif (argv[1][0] != '-'):
        print("Unknown command.")
        print()
        printHelp()
    else:
        arg = argv[1][1]
        if arg == 'h':
            printHelp()
        elif arg == 'a':
            if len(argv) > 2 and argv[2].isdigit():
                id = argv[2]
                mc.addModId(id) 
                mc.save()
            else:
                print('missing or invalid ID')
        elif arg == 'u':
            if len(argv) > 2 :
                url = argv[2]
                mc.addMod(url)
                mc.save()
            else:
                print('missing or invalid URL')
        elif arg == 'c':
            mc.checkUpdatesOnline()
            mc.save()
        elif arg == 'l':
            supportedGames()
        elif arg == 'i':
            mc.installUpdates()
        elif arg == 't':
            mc.checkUpdatesOnline(automatic=True)
            print('Copy the resulting zip files in your download directory: {}'.format('xx'))
            print('Press enter once the file have been copied. If you misspress, you can always restart with just -i')
            mc.installUpdates()
            mc.save()
        elif arg == 'p':
            mc.setDownloadPath()
            mc.save()

def supportedGames():
    '''List of supported games'''
    print("Currently tested games:")
    print("Cities: Skylines")
    print("Help me adding more games!")

def printHelp():
    print("Little app that check on steam workshop if there are updates on mods of configured games.")
    print("It doesn't download mods by itself but it gives you the link to use with a downloader.")
    print("You then have to restart this application to install the updates")
    print('-h : this help')
    print("-c : check for updates")
    print("-i : install updates")
    print('-a [ID] : add a module')
    print('-u [url] : add a module with the whole url (for the lazy)')
    print("-l : list of supported games")
    print("-t : check and install updates")
    print("-p : set download path")

if __name__ == '__main__':
    main(argv)
    
#todo: find the mod's directory once the game is selected. 
#todo: remove zips.
#todo: add games
#todo: wait after checking for -i
#todo: use another host for mods status.
#todo: add GOG compatibility (aka. change name?)
