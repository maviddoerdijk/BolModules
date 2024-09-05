from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pickle
import os
from dotenv import load_dotenv
import re
import random
from selenium.webdriver.firefox.options import Options
load_dotenv()


# Set random user-agent
def random_user_agent():
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_3) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (iPad; CPU OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0",
        "Mozilla/5.0 (Linux; Android 11; SM-G998B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Mobile Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/91.0.864.59",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1"
    ]
    return random.choice(user_agents)

# Sleep for a random time between requests to mimic human behavior
def sleep_random_time():
    time.sleep(random.uniform(1, 3))

def get_keyword_volumes(keywords):

    def parse_related_queries(text):
        main_keyword_pattern = re.compile(r'^(.*?)\sTotaal zoekvolume:\s(\d+)', re.MULTILINE)
        main_keyword_match = main_keyword_pattern.search(text)
        
        if not main_keyword_match:
            return {}
        
        main_keyword = main_keyword_match.group(1).strip()
        total_volume = main_keyword_match.group(2).strip()
        
        text = text.replace("Gerelateerde zoekterm Volume", "")
        
        related_keywords_pattern = re.compile(r'([\w\s]+?)\s(\d+)', re.MULTILINE)
        related_keywords_matches = related_keywords_pattern.findall(text)
        
        result = {
            'main keyword': main_keyword,
            'total volume': total_volume
        }
        
        for i, (keyword, volume) in enumerate(related_keywords_matches):
            if i == 0:
                keyword = keyword.replace(total_volume, "").strip()
            result[f'keyword{i+1}'] = keyword.strip()
            result[f'volume{i+1}'] = volume.strip()
        
        return result

    # Initialize the driver with random user agent options
    options = Options()
    options.set_preference("general.useragent.override", random_user_agent())
    driver = webdriver.Firefox(options=options)  # or webdriver.Chrome(options=options)

    try:
        login = True
        if login:
            driver.get("https://login.bol.com/login?client_id=gatekeeper")
            sleep_random_time()

            username = driver.find_element(By.NAME, "j_username")
            password = driver.find_element(By.NAME, "j_password")

            username.send_keys(os.getenv('BOL_SELLER_MAIL'))
            password.send_keys(os.getenv('BOL_SELLER_PASSWORD'))
            password.send_keys(Keys.RETURN)

            sleep_random_time()

            os.chdir('C:/Users/david/Documents/GitHub/BolModules/BolModules/bol_automation_modules/keywords')
            pickle.dump(driver.get_cookies(), open("resources/bol_seller_cookies.pkl", "wb"))

        else:
            driver.get("https://partner.bol.com/sdd/selleranalysis/search-trends/")
            cookies = pickle.load(open("resources/bol_seller_cookies.pkl", "rb"))
            for cookie in cookies:
                cookie['sameSite'] = 'None'
                driver.add_cookie(cookie)

        sleep_random_time()
        keyword_data = []

        for keyword in keywords:
            try:
                search_trends_url = "https://partner.bol.com/sdd/selleranalysis/search-trends/"
                payload = f"?search-1={keyword}&period=DAY&number-of-periods=30"
                driver.get(search_trends_url + payload)

                sleep_random_time()

                related_queries = driver.find_elements(By.ID, "related-queries-area")
                for rq in related_queries:
                    print('rq:')
                    print(rq.text)
                    print("")

                if "Totaal zoekvolume: 0" in related_queries[0].text:
                    continue

                volumes_dict = parse_related_queries(related_queries[0].text)

                keyword_data.append({'keyword': volumes_dict['main keyword'], 'monthly_search_volume': volumes_dict['total volume']})
                for i in range(1, (len(volumes_dict) - 2) // 2):
                    keyword_data.append({'keyword': volumes_dict[f'keyword{i}'], 'monthly_search_volume': volumes_dict[f'volume{i}']})
            except Exception as e:
                print(f"Error processing keyword {keyword}: {e}")
                continue
    finally:
        # Ensure the driver is closed
        driver.close()

    return keyword_data


if __name__ == "__main__":
    keywords = ['koffiezetapparaat', 'another keyword']
    print(get_keyword_volumes(keywords))
