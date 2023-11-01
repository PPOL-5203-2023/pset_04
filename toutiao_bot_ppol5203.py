# toutiao bot PPOL 5203

#import libraries from selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait # available since 2.4.0
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

# import other libraries
import time
import string
import pandas as pd
import numpy as np

# utils functions
def sleep_random_time(range_):
    '''
    :param range_: a tuple of the range of wait times
    ex: (0,30) would randomly sleep between 0 and 30 seconds
    '''
    if isinstance(range_, int):
        time.sleep(np.random.choice(range(range_)))
    elif isinstance(range_, tuple):
        min_time, max_time = range_
        if isinstance(min_time, float):
            min_time = int(math.ceil(min_time))
        if isinstance(max_time, float):
            max_time = int(math.floor(max_time))

        time.sleep(np.random.choice(range(min_time, max_time)))

class ToutiaoBot():
    '''
    Returns a Bot to interact with the Toutiao Webpage
    
        :param 
            headless (bool): True spins up a headless browser. Default equals to False.  
    '''
    # create instance attributes -----------------

    def __init__(self, headless=False):
        if headless==True:
            options = Options()
            
            # HEADLESS OPTIONS
            options.add_argument('--headless=new')
            options.add_argument("window-size=1920,1080")
            self.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), 
                                      options=options)
                
            # bypass OS security
            options.add_argument('--no-sandbox')
            # overcome limited resources
            options.add_argument('--disable-dev-shm-usage')
            # don't tell chrome that it is automated
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            # disable images
            prefs = {"profile.managed_default_content_settings.images": 2}
            options.add_experimental_option("prefs", prefs)

            # Setting Capabilities
            capabilities = webdriver.DesiredCapabilities.CHROME.copy()
            capabilities['acceptSslCerts'] = True
            capabilities['acceptInsecureCerts'] = True

            self.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), 
                                      options=options)
        else:
            self.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
    
    # method to close the bot -----------------------------
        
    def close(self):
        '''
        close the bot
        '''
        self.driver.close()
    
    # method to visit the home feed -----------------------------

    def go_home_feed(self):
        '''
        Sends the bot to the main toutiao homepage
        '''
        url = "https://www.toutiao.com/"
        # go to home toutia
        self.driver.get(url)
        # add some wait time
        self.element = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="root"]/div/div[5]/div[2]/div[1]/div/a')))
    
    
    # method to open a article -----------------
    
    def go_article(self, article_url, time_read):
        '''
        sends the bot to a seed article
            :param 
                article_url: str, string wiht the full url for the article
                time_read: int, time to spend "reading" the article
        '''
        # go to seed vide
        self.driver.get(article_url)
        
        # add some wait time
        #self.element = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 
         #                                                                               '.media-info .user-info')))
        
        # time to stay in the article
        time.sleep(time_read)
            
    
    # method to collect articles metadata. -------------------------------
    
    def collect_metadata_article(self, article_url, time_read):
        '''
        sends the bot to a see article and collects the url metadata
            :param 
                article_url: str, string wiht the full url for the article
                time_read: int, time to spend "reading" the article

        '''
        
        # navigate to the article
        self.go_article(article_url, time_read)
            
        
        # create a dictionary
        collector = dict()
        collector["video_url"] = article_url
        
        # scrape article information
        
        # author info
        try: 
            author_info = self.driver.find_element(By.CSS_SELECTOR, ".media-info .user-info")
            author_info_ = author_info.text.split("\n")
            collector["author_info_abbrv"] = author_info_[0]
            collector["author_info_full_name"] = author_info_[1]
        except:
            collector["author_info_abbrv"] = ""
            collector["author_info_full_name"] = ""
        # link to author
        try: 
            collector["author_link"] = author_info.find_element(By.CLASS_NAME, "user-avatar").get_attribute("href")
        except:
            collector["author_link"] = ""
        # title
        try:
            title = self.driver.find_element(By.CLASS_NAME, "article-content h1")
            collector["title"] = title.text
        except:
            collector["title"] =""
        # text
        try:
            text_boxes= self.driver.find_elements(By.CSS_SELECTOR, 'p[data-track]')
            collector["text"] = " ".join([t.text for t in text_boxes])
        except:
            collector["text"] = ""
        # reactions
        try:
            likes = self.driver.find_element(By.CLASS_NAME, "detail-like")
            comments = self.driver.find_element(By.CLASS_NAME, "detail-interaction-comment")
            collector["likes"] = likes.text
            collector["n_comments"] = comments.text
        except:
            collector["likes"] = ""
            collector["n_comments"] = ""  
        # add time of the publication
        try:
            time_= self.driver.find_element(By.CSS_SELECTOR, '.original-tag+ span')
            collector["time"] = time_.text
        except:
            collector["time"] = ""

        # return
        return collector
    
    
    ### method to collect related articles --------------------------------
    
    def collect_related_articles(self, article_url, time_read):
        '''
        sends the bot to a see article and collects the related articles reccomended from the same author
            :param 
                article_url: str, string wiht the full url for the article
                time_read: int, time to spend "reading" the article

        '''

        
        # navigate to the article
        self.go_article(article_url, time_read)
            
        
        # create a dictionary
        collector = dict()
        collector["video_url"] = article_url
        
        # collect related article
        try:
            related = self.driver.find_elements(By.CSS_SELECTOR, ".related-list-item")
            collector["link_related"]=[r.find_element(By.TAG_NAME, "a").get_attribute("href") for r in related]
            collector["text_related"] = [r.find_element(By.CLASS_NAME, "title").text for r in related]
        except: 
            collector["link_related"] =""
            collector["text_related"] =""
            
        return collector

    ### method to collect hot topics from a article --------------------------------
    
    def collect_hot_topic_from_article(self, article_url, time_read):
        '''
        sends the bot to a see article and collects the hot topics reccomended in the articles page
            :param 
                article_url: str, string wiht the full url for the article
                time_read: int, time to spend "reading" the article

        '''

        
        # navigate to the article
        self.go_article(article_url, time_read)
            
        
        # create a dictionary
        collector = dict()
        collector["video_url"] = article_url
        
        # collect related article
        try:
            related = self.driver.find_elements(By.CSS_SELECTOR, ".article-item")
            collector["link_hot_topic"]=[r.get_attribute("href") for r in related]
            collector["text_hot_topic"] = [r.get_attribute("aria-label") for r in related]
        except: 
            collector["link_hot_topic"] =""
            collector["text_text_topic"] =""
            
        return collector

    ### method to collect reccomendations from a article --------------------------------
    def collect_rec_from_article(self, article_url, time_read):
        '''
        sends the bot to a see article and collects the recommendations from the articles page
            :param 
                article_url: str, string wiht the full url for the article
                time_read: int, time to spend "reading" the article

        '''

        
        # navigate to the article
        self.go_article(article_url, time_read)
            
        
        # create a dictionary
        collector = dict()
        collector["video_url"] = article_url
        
        # scrool down to the bottom of the page
        time.sleep(np.random.choice(range(3, 7)))
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);") 
        time.sleep(np.random.choice(range(3, 7)))
        
        try: 
            rec = self.driver.find_elements(By.CSS_SELECTOR, ".feed-card-article-l .title")
            # collect reccomend
            if len(rec)>0:
                pass
            else:
                time.sleep(np.random.choice(range(3, 7)))
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);") 
                rec= self.driver.find_elements(By.CSS_SELECTOR, ".feed-card-article-l .title")

            try:
                collector["links"]=[r.get_attribute("href") for r in rec]
                collector["text"]=[r.get_attribute("aria-label") for r in rec]
                collector["title"]=[r.get_attribute("title") for r in rec]

                # code to clean later. some of the links are coming without text

                # clean text
                #text_=[r.get_attribute("aria-label") for r in rec]
                #text_=["" if text is None else str(text) for text in text_]

                # clean title
                #title_=[r.get_attribute("title") for r in rec]
                #title_=["" if text is None else str(text) for text in title_]

                # combine text and title
                #z = zip(text_, title_)
                #collector["title"]=["".join(z_) for z_ in z]
            except:
                collector["links"]=""
                collector["text"]=""
                collector["title"]=""
        except:
            pass
        
        return collector
    
     ### method to collect reccomendations from a article --------------------------------
    def collect_rec_from_home(self, user_id):
        '''
        sends the bot to home page and collects the recommendations

        '''

        # navigate to the article
        self.go_home_feed()
            
        
        # create a dictionary
        collector = dict()
        collector["user_id"] = user_id
        
        # scrool down to the bottom of the page
        time.sleep(np.random.choice(range(3, 7)))
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);") 
        time.sleep(np.random.choice(range(3, 7)))
        rec = self.driver.find_elements(By.CSS_SELECTOR, ".feed-card-article-l .title")

        
        # collect reccomend
        if len(rec)>0:
            pass
        else:
            time.sleep(np.random.choice(range(3, 7)))
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);") 
            rec = self.driver.find_elements(By.CSS_SELECTOR, ".feed-card-article-l .title")
                         
        try:
            collector["links"]=[r.get_attribute("href") for r in rec]
            collector["title"]=[r.get_attribute("aria-label") for r in rec]
            collector["text"]=[r.text for r in rec]
            
            # code to clean later. some of the links are coming without text
           
            # clean text
            #text_=[r.get_attribute("aria-label") for r in rec]
            #text_=["" if text is None else str(text) for text in text_]

            # clean title
            #title_=[r.get_attribute("title") for r in rec]
            #title_=["" if text is None else str(text) for text in title_]

            # combine text and title
            #z = zip(text_, title_)
            #collector["title"]=["".join(z_) for z_ in z]
        except:
            collector["links"]=""
            collector["text"]=""
            collector["title"]=""
        return collector
   
    ##### method to read articles on toutiao -------------------------
    
    def action_read_article(self, article_url, time_read):   
        '''
        sends the bot to a see article and collects the url metadata
            :param 
                article_url: str, string wiht the full url for the article
                time_read: int, time to spend "reading" the article

        '''
        
        # navigate to the article
        self.go_article(article_url, time_read)
        
        # replicate some common user behavior
        
        # 1 - move mouse to the author of the article
        try: 
            element = self.driver.find_element(By.CSS_SELECTOR, ".media-info .user-info")
            action = ActionChains(self.driver)
            action.move_to_element(element).pause(np.random.choice(range(10))).perform()
        except Exception as error: 
            print("Error occured when trying to move the mouse to the source", error)
        
        # 2 - move the mouse back to the main title
        try: 
            title_elem = self.driver.find_element(By.CLASS_NAME, "article-content h1")
            action = ActionChains(self.driver)
            action.move_to_element(title_elem).pause(np.random.choice(range(10))).perform()
        except Exception as error:
            print("Error occured when trying to move the mouse to the source", error)
        
        # 3 - scroll down through the article
        try:
        # get a proxy for the length of the article
            text_boxes= self.driver.find_elements(By.CSS_SELECTOR, 'p[data-track]')
            len_text = len(text_boxes)
            #scroll down and spend some time in the article
            for idx, par in enumerate(text_boxes):
                time.sleep(np.random.choice(range(3, 7)))
                self.driver.execute_script("arguments[0].scrollIntoView();", par)
                print(f'Reading the paragraph:{idx}')
        except Exception as error:
            print("An exception occurred:", error)         
        
        # 4 - scroll back to the title
        try:
            self.driver.execute_script("arguments[0].scrollIntoView();", title_elem)
        except Exception as error:
            print("An exception occurred:", error)         
            
            