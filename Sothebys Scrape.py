# -*- coding: utf-8 -*-
"""
Daniel Gilhuly
QAC386
"""
#%% DriverSetup
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
driver= webdriver.Chrome(ChromeDriverManager().install())
import numpy as np
import pandas as pd
import re
import time
from selenium.webdriver.common.by import By

#%% Cleanup and click functions

def Cleanup_Auction_Search(a):
    temp1 = []
    for x in a:
        temp1.append(x.text)
    return temp1


def Pattern_Match(d, pattern1):
    # find identation as to sort through to find individual elements i.e. artist, artwork, estimates
    regex = re.compile(pattern1)
    temp1 = []
    temp2 = []
    j= 0
    for i, match in enumerate(regex.finditer(d)):
        a= [match.span()]
        temp1 += a
    while (j+2) <= len(temp1):
        e= d[(temp1[j][1]):(temp1[(j+1)][0])]
        temp2.append(e)
        j += 1
    return temp2
    
def Clean_Individual_Cards(z):
    # make it pretty
    temp1 = []
    i = 0
    while (i+1) < len(z):
        if z[i] == "Estimate: ":
            temp1.append(z[(i+1)])
            i += 2
        elif z[i] == "LOT SOLD:":
            temp1.append(z[(i+1)] + " " + z[(i+2)])
            i += 3           
        else:
            temp1.append(z[i])
            i +=1
    return (temp1)

def cleanup_auctions_eras(z):
    #create 2 lists 1 = text of eras, 2 = link
    lst1 = []
    lst2 = []
    for x in z:
        if (x.text) == "":
            pass
        elif (x.text) == "Contemporary Art" or "Impressionist & Modern Art" or "19th Century European Paintings" or "American Art":
            lst1.append(x.text)
            lst2.append(x)
        else:
            pass
    return (np.column_stack([lst1, lst2]))



#%% Didnt end up using due to time but will later
def go_end_of_page(wd):
    SCROLL_PAUSE_TIME = 2.7

    # Get scroll height
    last_height = wd.execute_script("return document.body.scrollHeight")
    
    while True:
        # Scroll down to bottom
        wd.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    
        # Wait to load page
        time.sleep(SCROLL_PAUSE_TIME)
    
        # Calculate new scroll height and compare with last scroll height
        new_height = wd.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

def scroll():
    driver.get("https://www.sothebys.com/en/results?locale=en")
    driver.execute_script("window.scrollTo(0, 950);")
    time.sleep(2)


#%% Get to Auctions and Deal with Search Box for Eras
def find_auctions_Search():
    scroll()
    driver.find_elements(By.XPATH,"""/html/body/main/div/div/div[2]/dialog/div[1]/div/form/div[2]/div[2]/div[3]/div[2]/span""") #xpath will be deprecated soon
    Eras_Class= driver.find_elements(By.CLASS_NAME, "SearchControlCheckbox")
    Era_and_Link = cleanup_auctions_eras(Eras_Class)
    return Era_and_Link


#%% Names of Auctions, Date of Auctions

def Auctions_scrape():
    Auction_titles= driver.find_elements(By.CLASS_NAME,"Card-title")
    Date_and_Location  = driver.find_elements(By.CLASS_NAME,"Card-details")
    Auctions = Cleanup_Auction_Search(Auction_titles)
    Date_Locations = Cleanup_Auction_Search(Date_and_Location)
    LinktoAuctions= driver.find_elements(By.CLASS_NAME,"AuctionActionLink-link")
    z= np.column_stack([Auctions, Date_Locations, LinktoAuctions])
    try:
        if z[0][0] == "Original Racing Posters, 1925–1972" or "Manga": #these ones were being difficult
            z = np.delete(z,0,0)
        else:
            pass
    except:
        pass
    return z
        


#%% Get Individual Auctions/Arists/Artworks/Prices WIP

def AAAP_scrape():
    Individual_Data = []
    AAAP = driver.find_elements(By.CLASS_NAME,"css-1ilyui9")
    for x in AAAP:
        a = Pattern_Match(x.text, "\n")
        b = Clean_Individual_Cards(a)
        Individual_Data.append(b)
    return (Individual_Data)



#%% create dataset
data = pd.DataFrame(columns = ["Era", "Auction", "Date/Location", "Artist/Artwork", "Expected Price" "Price Sold"])
def create_data2(z1, i1, i2 ,i3):
    
    while i1 < len(find_auctions_Search()):
        #Eras
        Era_and_Link = find_auctions_Search()
        data.loc[z1,"Era"] = Era_and_Link[i1][0]
        time.sleep(3)
        Era_and_Link[i1][1].click()
        time.sleep(5)
        while i2 < 2: #broken somehow -- Auctions_scrape())
            #Auction, Date, Location
            Auctions_Date_Loc = Auctions_scrape()
            data.loc[z1,"Era"] = Era_and_Link[i1][0]
            data.loc[z1,"Auction"] = Auctions_Date_Loc[i2][0]
            data.loc[z1, "Date/Location" ] = Auctions_Date_Loc[i2][1]
            #Auctions_Date_Loc[i2][2].click()
            #while i3 < len(AAAP_scrape()) :
                #Artwork, Artist, Price
                #Art_Artist_Price = AAAP_scrape()
                #data.loc[z1,"Era"] = Era_and_Link[i1][0]
                #data.loc[z1,"Auction"] = Auctions_Date_Loc[i2][0]
                #data.loc[z1, "Date/Location" ] = Auctions_Date_Loc[i2][1]
                #data.loc[z1, "Artist/Artwork"] = Art_Artist_Price[i3][0]
                #data.loc[z1, "Expected Price"] = Art_Artist_Price[i3][1]
                #try:
                    #data.loc[z1, "Price Sold"] = Art_Artist_Price[i3][2]
                #except:
                    #pass
                #z1 += 1
                #i3 += 1
                #print("lower " + "z1 = " + str(z1) + " i3 = " + str(i3))
            z1 += 1
            i2 += 1
            i3 = 0
            print("mid " + "z1 = " + str(z1) + " i3 = " + str(i3) + " i2 = " + str(i2))
            #Era_and_Link1 = find_auctions_Search()
            #time.sleep(3)
            #Era_and_Link1[i1][1].click()
        z1 += 1
        i1 += 1
        i2 = 0
        i3 = 0
        print("upper " + "z1 = " + str(z1) + " i3 = " + str(i3) + " i2 = " + str(i2) + " i1 = " + str (i1))


data = create_data2(0, 0, 0, 0)


#%% Finish
zzz = data.to_excel("Daniel's Sotheby's Auction Results1")
driver.close()





        


# %%
