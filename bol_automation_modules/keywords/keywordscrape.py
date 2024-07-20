from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pickle

driver = webdriver.Firefox()  # or webdriver.Chrome()
login = True

if login:
    driver.get("https://login.bol.com/login?client_id=gatekeeper")

    # Wait for the page to load
    time.sleep(2)

    username = driver.find_element(By.NAME, "j_username")
    password = driver.find_element(By.NAME, "j_password")

    username.send_keys("davidmoerdijk@gmail.com")
    password.send_keys("Lobbie031@")

    # Submit form
    password.send_keys(Keys.RETURN)

    # Wait for the page to load
    time.sleep(2)


    # After logging in, save the cookies to a file
    pickle.dump(driver.get_cookies(), open("bol_seller_cookies.pkl", "wb"))
    
# load the cookies into your browser
if not login:
    driver.get("https://partner.bol.com/sdd/selleranalysis/search-trends/")
    cookies = pickle.load(open("bol_seller_cookies.pkl", "rb"))
    for cookie in cookies:
        cookie['sameSite'] = 'None'
        driver.add_cookie(cookie)

    
time.sleep(2)


search_trends_url = "https://partner.bol.com/sdd/selleranalysis/search-trends/"
payload = "?search-1=koffiezetapparaat&period=DAY&number-of-periods=30"
driver.get(search_trends_url + payload)

# Wait for the page to load
time.sleep(2)

# find           <div class="puik-row" id="related-queries-area"></div>
related_queries = driver.find_elements(By.ID, "related-queries-area")
# .text -> 'koffiezetapparaat\nTotaal zoekvolume: 19930\n\nGerelateerde zoekterm\nVolume\nsenseo\n6651\nkoffiezetapparaat met thermoskan\n3013\nkoffiezetapparaat bonen\n1330\nkoffiezetapparaat filterkoffie\n1287\nkoffiezetapparaat dolce gusto\n712\nkoffiezetapparaat cups\n617\nkoffiezetapparaat philips\n454\nkoffiezetapparaat nespresso\n307\nkoffiezetapparaat senseo\n301\nkoffiezet apparaat\n265'
for rq in related_queries:
    print(rq.text)
    print("")


# find all class="related-queries-title"
related_queries_titles = related_queries.find_elements(By.CLASS_NAME, "related-queries-title")
for title in related_queries_titles:
    print(title.text)


# find total volume using <span class="title-total-indicator">
total_volume = driver.find_element(By.CLASS_NAME, "title-total-indicator")
print(total_volume.text)

# get parent of total volume
parent = total_volume.find_element(By.XPATH, "..")
# get the child of parent usin <h5 class="seller-analysis__title-small">koffie</h5>
child = parent.find_element(By.CLASS_NAME, "seller-analysis__title-small")
print(child.text)

# now find next total_volume after the first
total_volume = child.find_element(By.XPATH, "following-sibling::span")

print(total_volume)
print(total_volume.text)

driver.close()


