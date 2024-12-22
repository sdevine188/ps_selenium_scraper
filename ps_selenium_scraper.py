import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import pandas as pd
import numpy as np
import math
from datetime import datetime
import win32clipboard
import re


# chromedriver
#https://googlechromelabs.github.io/chrome-for-testing/#stable

 # set wd
os.getcwd()
os.chdir("C:/Users/Stephen/Desktop/Python/ps_selenium_scraper")

# create ps_selenium_scraper function
def ps_selenium_scraper(month):

#////////////////////////////////////////////////////////////////////////


        # read in urls
        ps_urls = pd.read_csv("ps_urls.csv")
        
        
        #//////////////////////////////////////////////////////////////////////
        
        
        # read in username and password
        credentials = pd.read_csv("ps_username_and_password.csv")
        username = credentials["username"].values[0]
        password = credentials["password"].values[0]

        
        #//////////////////////////////////////////////////////////////////////
        
        
        # create article_output_df
        article_output_df = pd.DataFrame({"article_text" : []})
        
        
        #//////////////////////////////////////////////////////////////////////
        
        
        # start driver
        driver = webdriver.Chrome("chromedriver.exe")
        
        # set page load timeout
        driver.set_page_load_timeout(60)
        
        
        #//////////////////////////////////////////////////////////////////////
        
        
        # login
        driver.get(ps_urls.iloc[0].values[0][0:32] + "/account/login")
        time.sleep(2)
        driver.find_element_by_xpath("//input[@type = 'email']").send_keys(username)
        driver.find_element_by_xpath("//input[@type = 'password']").send_keys(password)
        driver.find_element_by_xpath("//button[@id = 'ccc-notify-accept']").click()   
#        time.sleep(2)
#        driver.find_element_by_xpath("//button[@class = 'remodal-close']").click() 
        time.sleep(2)
        driver.find_element_by_xpath("//input[@id = 'login-button']").click()  
        time.sleep(2)
        
        
        #//////////////////////////////////////////////////////////////////////

        
        # loop through urls getting text                  
        for i in list(range(0, ps_urls.shape[0])):
        
                # navigate to author url
                driver.get(ps_urls.iloc[i].values[0])
                time.sleep(2)
        
                # get article_url
                article_element = driver.find_elements_by_xpath("//ol[@id = 'tab-latest-commentaries-content']//a[@href][@title]")
                if len(article_element) == 0:
                        print(f"no articles found on {ps_urls.iloc[i].values[0]}")
                        continue
                article_url = article_element[0].get_attribute("href")
                prior_article_url = article_element[1].get_attribute("href")
                
                # skip over urls for PS on-point interviews
                if(article_url[0:42] == "https://www.project-syndicate.org/onpoint/"):
                        article_url = article_element[1].get_attribute("href")
                        prior_article_url = article_element[2].get_attribute("href")
                
                if(prior_article_url[0:42] == "https://www.project-syndicate.org/onpoint/"):
                        prior_article_url = article_element[2].get_attribute("href")
                
                
                #//////////////////////////////////////////////////////////////////////
                
                
                # navigate to article_url
                driver.get(article_url)
                time.sleep(2)
        
                # get article_month
                date_element = driver.find_elements_by_xpath("//div[@class = 'article__byline']/time[@itemprop = 'datePublished']")
                date = date_element[0].get_attribute("datetime")
                article_month = int(date[5:7])
                
                # get article_year
                date_element = driver.find_elements_by_xpath("//div[@class = 'article__byline']/time[@itemprop = 'datePublished']")
                date = date_element[0].get_attribute("datetime")
                article_year = int(date[0:4])
                
                # if there is a promotional popup blocking access to article text, then close it
                # note that the promotional popup close button currently is the 0th element returned,
                # but there are five matching elements returned, and even when the promo popup isn't shown, there
                # are still 4 matching elements returned. these throw an error if you try to click the 0th one though,
                # so maybe they are hidden buttons... either way, this code tries to click the 0th, and if that fails
                # it means the promo popup isnt shown, and so a dummy exception runs and the loop continues
                try:
                        driver.find_elements_by_xpath("//button[@aria-label = 'Close popup']")[0].click()
                except:
                        print("")
              
                
                # get author
                author_element = driver.find_elements_by_xpath("//span[@class = 'listing__author author']")
                author = author_element[0].text
                print(author)
                
                # if article_month = requested month and its an "onpoint" interview, skip to next author
                if(article_month == month and article_url.__contains__("https://www.project-syndicate.org/onpoint/")):
                        print(author + " has an OnPoint interview for this month, and will be skipped")
                        continue
                
                # get article_text
                body_text_elements = driver.find_elements_by_xpath("//div[@itemprop = 'articleBody']/p")
                article_text = []
                for i in list(range(0, len(body_text_elements))):
                        text_chunk = body_text_elements[i].text
                        article_text.append(text_chunk)
                article_text = " ".join(article_text)    
                article_text = "by: " + author + ". . . " + article_text       


                #//////////////////////////////////////////////////////////////////////
                
                
                # if article year is current and article_month matches requested month, then append article_text to article_output_df
                if(article_year == datetime.now().year and article_month == month):
                        article_text_df = pd.DataFrame({"article_text" : [article_text]})
                        article_output_df = article_output_df.append(article_text_df)
                        
                        
                #//////////////////////////////////////////////////////////////////////


                # if the current author only has articles for prior months, skip to next author 
                if(article_month < month and month != 12):
                        print(author + " does not have an article for this month")
                        continue
                
                
                #//////////////////////////////////////////////////////////////////////
                
                
                # if article_month is the month after the requested month, get the previous article
                if(article_month == (month + 1) or \
                     (article_month == 1 and month == 12)):
                        
                        # navigate to prior_article_url
                        driver.get(prior_article_url)
                        time.sleep(2)
                
                        # get article_month
                        date_element = driver.find_elements_by_xpath("//div[@class = 'article__byline']/time[@itemprop = 'datePublished']")
                        date = date_element[0].get_attribute("datetime")
                        article_month = int(date[5:7])
                        
                        # get article_year
                        date_element = driver.find_elements_by_xpath("//div[@class = 'article__byline']/time[@itemprop = 'datePublished']")
                        date = date_element[0].get_attribute("datetime")
                        article_year = int(date[0:4])
                        
                        # if article_month = requested month and its an "onpoint" interview, skip to next authoer
                        if(article_month == month and article_url.__contains__("https://www.project-syndicate.org/onpoint/")):
                                print(author + " has an OnPoint interview for this month, and will be skipped")
                                continue
                        
                        # if there is a promotional popup blocking access to article text, then close it
                        # note that the promotional popup close button currently is the 0th element returned,
                        # but there are five matching elements returned, and even when the promo popup isn't shown, there
                        # are still 4 matching elements returned. these throw an error if you try to click the 0th one though,
                        # so maybe they are hidden buttons... either way, this code tries to click the 0th, and if that fails
                        # it means the promo popup isnt shown, and so a dummy exception runs and the loop continues
                        try:
                                driver.find_elements_by_xpath("//button[@aria-label = 'Close popup']")[0].click()
                        except:
                                print("")
                        
                        # get article_text
                        body_text_elements = driver.find_elements_by_xpath("//div[@itemprop = 'articleBody']/p")
                        article_text = []
                        for i in list(range(0, len(body_text_elements))):
                                text_chunk = body_text_elements[i].text
                                article_text.append(text_chunk)
                        article_text = " ".join(article_text)    
                        article_text = "by: " + author + ". . . " + article_text
                        
                        # if article year is current and article_month matches requested month, then append article_text to article_output_df
                        if(article_month == month):
                                article_text_df = pd.DataFrame({"article_text" : [article_text]})
                                article_output_df = article_output_df.append(article_text_df)
                                                
                        # if the current author only has articles for prior months, skip to next author
                        if(article_month != month):
                                print(author + " does not have an article for this month")
                                continue
                        
                #//////////////////////////////////////////////////////////////////////
                
                
        # get total_article_count
        total_article_count = article_output_df.shape[0]

        # loop through article_text and add article_count_string
        for i in list(range(0, total_article_count)):
                article_count_string = "Project Syndicate. Article " + str(i + 1) + " of " + str(total_article_count) + ". "
                article_output_df.iloc[i , 0] = article_count_string + article_output_df.iloc[i , 0] + "{{split}}"    

        # remove weird characters
        article_output_df.article_text = article_output_df.article_text.replace("–", "-", regex = True)
        article_output_df.article_text = article_output_df.article_text.replace("’", "'", regex = True)
        article_output_df.article_text = article_output_df.article_text.replace("“", '"', regex = True)
        article_output_df.article_text = article_output_df.article_text.replace("”", '"', regex = True)

   
        #//////////////////////////////////////////////////////////////////////


        # write file
        file_name = "ps_text_" + str(month) + ".csv"
        article_output_df.to_csv(file_name, index = False)


#///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


# run ps_selenium_scraper
# ps_selenium_scraper(11)




