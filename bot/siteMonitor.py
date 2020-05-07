import urllib.request
import difflib
import time
from bs4 import BeautifulSoup
import re

request_time = 10
    
    
    
#code for diff
def diff(first, second):
        
        item_list = []
        
        second = set(second)
        
        for item in first:
            if item not in second:
                item_list.append(item)
        
        return item_list



def takeDifferences(lists, i):
    
    
    for new, old in zip(lists[i+1], lists[i]):
        
        differences = diff(new, old)
        
        #not empty list
        if(differences != []):
            if len(differences) < 2:
                print(differences)
            else:
                print("Lot of news pal!")    
        else:
           # print("We have to go deeper")
            if i < len(lists)-3:
                i += 2
                takeDifferences(lists, i)
            else:
                break    
            #save previous changes

    
#save site content    
url = "https://www.wykop.pl/wykopalisko/najnowsze/"
html = urllib.request.urlopen(url).read()
soup = BeautifulSoup(html, "html.parser")

#repeat
while(True):
    
    time.sleep(request_time)
    url2 = "https://www.wykop.pl/wykopalisko/najnowsze/"
    html2 = urllib.request.urlopen(url2).read()
    soup2 = BeautifulSoup(html2, "html.parser")
    
    #region for lists of tags
    lists = []
    
    #lists.append(soup.find_all([ 'h1']))
    #lists.append(soup2.find_all([ 'h1']))
 
     
    lists.append(soup.find_all([ 'h2']))
    lists.append(soup2.find_all([ 'h2']))
        
    lists.append(soup.find_all([ 'h3']))
    lists.append(soup2.find_all([ 'h3']))
        
    lists.append(soup.find_all([ 'h4']))
    lists.append(soup2.find_all([ 'h4']))
    
        
    lists.append(soup.find_all([ 'h5']))
    lists.append(soup2.find_all([ 'h5']))
    
        
    lists.append(soup.find_all([ 'p']))
    lists.append(soup2.find_all([ 'p']))

    #here for now, idk why when it was first appended
    #it was not diff-able
    #probably no h1 tags on site
    
    lists.append(soup.find_all([ 'h1']))
    lists.append(soup2.find_all([ 'h1']))

    #end region of lists
    
    
    takeDifferences(lists, 0)
       
    soup = soup2
