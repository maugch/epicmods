import requests
from bs4 import BeautifulSoup
from time import time as ttime,sleep

import logging
import logging.config

logger = logging.getLogger(__name__)



class WebCrawler:
    def __init__(self):
        self.time = 0
        #crawl delay = 2 seconds
        self.crawl_delay = 2

    def crawl(self,page_url):
        '''
        Crawl page 
        '''
        headers = {
            'User-Agent': 'slow-read',
            'From': 'slowread@domain.com' 
        }
        
        now_time = ttime()
        if self.time != 0 and (now_time-self.time < self.crawl_delay):
            timetw = self.crawl_delay-(now_time-self.time)
            sleep(timetw)

        r = requests.get(page_url, headers=headers)
        soup = BeautifulSoup(r.content,'lxml')
        
        self.time = ttime()
        
        if r is None:
            return None
    
        #dump(page_data)
        return soup


class WorkshopCrawler:

    def __init__(self):
        self._base_url = 'https://steamcommunity.com/sharedfiles/filedetails/?id='
        self._crawler = WebCrawler() 
        self._soup = None
        self._crawledId = ''

    def _crawl(self,id):
        logger.info('crawling {}'.format(id))
        self._crawledId = id
        return  self._crawler.crawl(self._base_url + id)

    def _getAppId(self):
        result = self._soup.findAll('a',attrs={'data-appid': True})
        logger.info(result)
        return result[0]['data-appid']

    def _getAppName(self):
        result = self._soup.findAll('div',{'class':'apphub_AppName'})
        logger.info(result)
        return result[0].text

    def _getModDate(self):
        result = self._soup.findAll('div',{'class':'detailsStatRight'})
        logger.info(result)
        return result[2].text

    def _getModName(self):
        result = self._soup.findAll('div',{'class':'workshopItemTitle'})[0].text
        return result

    def _getModRequirements(self):
        resList = {}
        result = self._soup.findAll('div',{'id':'RequiredItems'})
        if not result:
            return resList
        logger.info('requirements {}'.format(result))
        results = result[0].findChildren("a" , recursive=False)
        for r in results:
            reqName = r.text.strip()
            reqId = r['href'].partition('id=')[2]
            resList[reqId]= reqName
        return resList

    def fetchModInfo(self,id):
        ''' fetch mod info and appnId/name'''
        
        result = {}

        self._soup = self._crawl(id)

        appId = self._getAppId()
        appName = self._getAppName()

        name = self._getModName()
        result['name'] = name

        adate = self._getModDate()
        result['date'] = adate
            
        requirements = self._getModRequirements()

        result['requirements'] = {}
        
        for k,v in requirements.items():
            result['requirements'][k] = v
        
        return result,appId,appName

  
    def _getRequiredDLC(self):
        ''' savegames only?'''
        #use requiredDLCName
        '''<div class="requiredDLCContainer">
            <div class="requiredDLCItem">
                <a href="https://store.steampowered.com/app/369150">
                <img src="https://cdn.cloudflare.steamstatic.com/steam/apps/369150/capsule_184x69.jpg" style="vertical-align: middle; padding-right: 5px; width: 120px; height: 45px;"></a>
                <span class="requiredDLCName">
                    <a href="https://store.steampowered.com/app/369150">Cities: Skylines - After Dark</a>
                </span>
                <br clear="all">
            </div>
        '''
        return
