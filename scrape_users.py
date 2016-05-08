from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
import time,random,socket,unicodedata

def u_to_s(uni):
    return unicodedata.normalize('NFKD',uni).encode('ascii','ignore')

def randdelay(a,b):
    time.sleep(random.uniform(a,b))

def str_to_user(tgt,mystr):
    pos = tgt.find(mystr)
    if pos <= 1:
        return None
    else:
        return tgt[0:pos]
    
def runme(url, threshold = 100):
    browser = webdriver.Firefox()
    browser.get(url)
    while threshold > 0:        
        try:
            morenotes = browser.find_element_by_partial_link_text("Show more notes")
            if morenotes.is_displayed() == False:
                raise (NoSuchElementException)
            morenotes.click()
            randdelay(1,2)
            threshold -= 1
        except NoSuchElementException:
            try:
                loading = browser.find_element_by_class_name("notes_loading")
                if loading.is_displayed() == False:
                    break
            except NoSuchElementException:
                break
        except (StaleElementReferenceException, socket.error):
            x = 0
    lis = browser.find_elements_by_tag_name("li")
    reblogged = []
    liked = []
    for i in lis:
        teststr = u_to_s(i.text)
        test_re = str_to_user(teststr,"reblogged")
        test_li = str_to_user(teststr,"liked")
        if test_re is not None:
            reblogged.append(test_re)
        elif test_li is not None:
            liked.append(test_li)
    everybody = set(liked + reblogged)
    reblogged = set(reblogged)
    liked = set(liked)
    browser.close()
    return (everybody,reblogged,liked)   