### THIS IS THE OLD MAIN.PY, SOME NON-DATABASE RELATED FUNCTIONS COULD STILL BE HERE ### 
import requests
from bs4 import BeautifulSoup
import re
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
import webbrowser
import json
from googlesearch import search 
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import traceback
from selenium import webdriver
from typing import Tuple
import os 
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import time
# from analyse import get_analyse_product_listing_csv
import sys
import os

# Add the 'src' directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from helpers.helperfunctions import replace_page_number, normalize_url

# undo the sys path append
sys.path = sys.path[:-1]


Base = declarative_base()


class Seller(Base):
    __tablename__ = 'sellers_beschrijvingen'
    name = Column(String, primary_key=True)
    handelsnaam = Column(String)
    topic = Column(String)
    totalResultsText = Column(String)
    totalResultsInt = Column(Integer)
    products_link = Column(String)
    # product_link = Column(String)
    seller_link = Column(String)
    vestigingsadres = Column(String)
    totaal_aanbod = Column(String)
    kvk_nummer = Column(String)
    btw_nummer = Column(String)
    email_adress = Column(String)  
    personal_website = Column(String)
    error = Column(String)

class WebCrawlerBol:
    def __init__(self, db_url="sqlite:///bol_verkopers.db"):
        self.seller_links = {}
        self.seller_data_updated = True
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()


    def save_to_db(self, seller_name, data):
        # Check if a seller with the given name already exists in the database
        existing_seller = self.session.query(Seller).filter_by(name=seller_name).first()

        if existing_seller:
            # If the seller exists, update their information
            existing_seller.totalResultsText = data['totalResultsText']
            existing_seller.totalResultsInt = data['totalResultsInt']
            existing_seller.handelsnaam = data['handelsnaam']
            existing_seller.products_link = data['products_link']
            existing_seller.seller_link = data['seller_link'] 
            existing_seller.topic = data['search_topic']
            existing_seller.vestigingsadres = data['vestigingsadres']
            existing_seller.totaal_aanbod = data['totaal_aanbod']
            existing_kvk_nummer = data['kvk_nummer']
            existing_btw_nummer = data['btw_nummer']
            existing_seller.kvk_nummer = existing_kvk_nummer if existing_kvk_nummer else existing_seller.kvk_nummer
            existing_seller.btw_nummer = existing_btw_nummer if existing_btw_nummer else existing_seller.btw_nummer
            existing_seller.error = data['error']
        else:
            # If the seller doesn't exist, create a new seller object and add it to the session
            new_seller = Seller(
                name=seller_name,
                handelsnaam=data['handelsnaam'],
                totalResultsText=data['totalResultsText'],
                totalResultsInt=data['totalResultsInt'],                
                products_link=data['products_link'],
                seller_link=data['seller_link'],
                topic=data['search_topic'],
                vestigingsadres=data['vestigingsadres'],
                totaal_aanbod=data['totaal_aanbod'],
                kvk_nummer=data['kvk_nummer'],
                btw_nummer=data['btw_nummer'],
                error=data['error']
            )
            self.session.add(new_seller)

        # Commit the changes to the database
        self.session.commit()

    def seller_exists(self, seller_name):
        existing_seller = self.session.query(Seller).filter_by(name=seller_name).first()
        if existing_seller:
            return True
        else:
            return False


    def close_connection(self):
        self.session.close()

    def get_soup(self, url):
        response = requests.get(url)
        page_content = response.content
        page_soup = BeautifulSoup(page_content, 'lxml')
        return page_soup

    def add_seller_links(self, start_url, search_topics):
        self.seller_data_updated = False

        # <a href="/nl/nl/s/?page=2&amp;searchtext=poster&amp;view=list" class="js_pagination_item" data-page-number="2">2</a>
        for search_topic in search_topics:
            search_url = start_url + search_topic
            page_soup = self.get_soup(search_url)
            pagination_items = page_soup.find_all(['a', 'li'], {'class': 'js_pagination_item'})
            # Iterate through the list of <a> elements
            largest_number = None
            for item in pagination_items:
                if item.has_attr('data-page-number'):
                    page_number = int(item['data-page-number'])
                    if largest_number is None or page_number > largest_number:
                        largest_number = page_number
            max_pages = largest_number
            href_next_page = pagination_items[0]['href']
            max_max_pages = 40 # after the 20th page, it will only find sellers that have already been found
            max_pages = max_max_pages if max_max_pages < max_pages else max_pages


            for i in range(1, int(max_pages)):
                # /nl/nl/s/?page=500&amp;searchtext=poster&amp;view=list
                href_next_page = replace_page_number(href_next_page, i)
                search_url_nextpage = "https://www.bol.com" + href_next_page
                page_soup = self.get_soup(search_url_nextpage)
                if page_soup:
                    print("succesful soup for", search_url_nextpage)
                else:
                    print('couldnt find pagesoup for', search_url_nextpage)
                # Find hrefs
                seller_link_divs = page_soup.find_all('a', {'data-test': 'party-link'})
                
                # Extract href attributes
                page_count = 0
                for link in seller_link_divs:
                    if self.seller_links.get('href'):
                        # if that link is already in the dict: skip
                        continue
                    page_count += 1
                    href = link.get('href')

                    self.seller_links[href] = search_topic

        


    def get_bedrijfs_informatie(self, page_soup_seller_page):
        try:
            try:
                handelsnaam = page_soup_seller_page.find('dt', string='Handelsnaam').find_next('dd').get_text(strip=True)
            except AttributeError:
                handelsnaam = None

            try:
                vestigingsadres = page_soup_seller_page.find('dt', string='Vestigingsadres').find_next('dd').get_text(strip=True)
            except AttributeError:
                vestigingsadres = None

            try:
                kvk_nummer = page_soup_seller_page.find('dt', string='KvK-nummer').find_next('dd').get_text(strip=True)
            except AttributeError:
                kvk_nummer = None

            try:
                btw_nummer = page_soup_seller_page.find('dt', string='Btw-nummer').find_next('dd').get_text(strip=True)
            except AttributeError:
                btw_nummer = None
            # find number of aanbod based on data-analytics-tag="seller_page:aanbod"
            # find the 'li' element with 'data-test="seller_offers"'
            try:
                seller_offers_li = page_soup_seller_page.find('li', {'data-test': 'seller_offers'})

                # find the 'span' element inside this 'li' element
                span = seller_offers_li.find('span')

                # use regular expressions to extract the number from the text of the 'span' element
                totaal_aanbod = int(re.search(r'\((\d+)\)', span.text).group(1))
                if not totaal_aanbod:
                    print("int gave 0, page_soup: ", page_soup_seller_page)
            except:
                print("error occurred, page soup: ", page_soup_seller_page)
                totaal_aanbod = 0
            err = 'None'
        except Exception as e:
            handelsnaam = ''
            vestigingsadres = ''
            kvk_nummer = ''
            btw_nummer = ''
            totaal_aanbod = None
            err = e

        seller_data_entry = {
            'handelsnaam': handelsnaam,
            'vestigingsadres': vestigingsadres,
            'kvk_nummer': kvk_nummer,
            'btw_nummer': btw_nummer,
            'totaal_aanbod': totaal_aanbod,
            'error': str(err)
        }
        return seller_data_entry

    def get_seller_data(self):
        if self.seller_data_updated:
            return self.seller_data
        else:
            new_seller_data = {}
            count = 0
            for products_link_path, search_topic in zip(self.seller_links.keys(), self.seller_links.values()):
                count += 1
                try:
                    # extract seller name from link
                    seller_name = products_link_path.split('/')[-3]
                    # skip if seller name is already in database
                    if self.seller_exists(seller_name):
                        continue

                    products_link = 'https://www.bol.com' + products_link_path
                    page_soup = self.get_soup(products_link)
                    
                    # find amount of products sold by seller
                    total_results = page_soup.find('p', {'class': 'total-results js_total_results'})
                    total_results_text = total_results.text.strip()
                    


                    
                    # get int of total results from total_results_text
                    total_amount = ''.join([char for char in total_results_text if char.isdigit()])  # More pythonic way to get digits
                    seller_data_entry = {
                        'totalResultsText': total_results_text,
                        'totalResultsInt': int(total_amount),
                        'products_link': products_link,
                        'search_topic': search_topic,
                    }

                    # go to first product link for the seller to reach their seller page
                    product_link = page_soup.find('a', {'class': 'list_page_product_tracking_target'})
                    product_link_path = product_link.get('href')
                    product_link = 'https://www.bol.com' + product_link_path
                    page_soup_first_product_link = self.get_soup(product_link)

                    # get to seller page using first product link 
                    seller_page = page_soup_first_product_link.find('a', {'class': 'product-seller__link'})
                    seller_page_path = seller_page.get('href')
                    seller_page = 'https://www.bol.com' + seller_page_path
                    page_soup_seller_page = self.get_soup(seller_page)

                    seller_data_entry.update({'seller_link': seller_page})
                    

                    # get seller data from seller page
                    if page_soup_seller_page:
                        bedrijfs_informatie_entry = self.get_bedrijfs_informatie(page_soup_seller_page)
                    else:
                        print("no page_soup_seller_page found for ", seller_page)
                        bedrijfs_informatie_entry = {
                            'handelsnaam': '',
                            'vestigingsadres': '',
                            'kvk_nummer': '',
                            'btw_nummer': '',
                            'totaal_aanbod': None,
                            'error': 'page_soup_seller_page is None'
                        }
                        

                    # Add seller's information to the seller_data_entry
                    seller_data_entry.update(bedrijfs_informatie_entry)
                    
                    totaal_aanbod = seller_data_entry.get('totaal_aanbod')
                    if not totaal_aanbod:
                        print("")

                    self.save_to_db(seller_name, seller_data_entry)

                except Exception as e:
                    print(e)

            self.seller_data = new_seller_data
            self.seller_data_updated = True
            return new_seller_data
        









def find_all_products(seller: Seller):
    all_products_seller_page = requests.get(seller.products_link)
    all_products_seller_pagesoup = BeautifulSoup(all_products_seller_page.content, 'lxml')
    all_products = all_products_seller_pagesoup.find_all('a', {'class': 'product-title'})
    return all_products

def get_description_soup_from_product_page(product_page):
    product_pagesoup = BeautifulSoup(product_page.content, 'lxml')
    # get description using data-test="product-description"
    description = product_pagesoup.find('div', {'data-test': 'description'})
    description_content_list = description.contents
    if not description_content_list:
        return None
    else:
        # add all elements of content list to one string
        description_str = ''
        for content in description_content_list:
            description_str += str(content)
    return description_str

def get_title_soup_from_product_page(product_page):
    product_pagesoup = BeautifulSoup(product_page.content, 'lxml')
    title = product_pagesoup.find('span', {'data-test': 'title'})
    title_content_list = title.contents
    if not title_content_list:
        return None
    else:
        # add all elements of content list to one string
        title_str = ''
        for content in title_content_list:
            title_str += str(content)
    return title_str
    
    





def find_mail_and_website(seller: Seller) -> Tuple[str, str]:
    """
    Returns:
    The email address of the company, using webcrawling
    """
    link = find_best_link(seller)

    if link:
        ## method 1 - use beautifulsoup    
        company_page = requests.get(link)
        page_soup = BeautifulSoup(company_page.content, 'lxml')
        # find "@" in the html text
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'

        # Find all matches of the email pattern in the HTML
        email_addresses = re.findall(email_pattern, str(page_soup))
        email_addresses = list(set(email_addresses))
        # remove any mail adresses that are not 
        
        ## method 2 - use selenium for if mails are hidden in html using javascript
        if not email_addresses:
            option = webdriver.ChromeOptions()
            option.add_argument("--headless")
            browser = webdriver.Chrome(options=option)

            browser.get(link)
            # Get the page source
            page_source = browser.page_source

            # Find all matches of the email pattern in the page source
            email_addresses = re.findall(email_pattern, page_source)



        if len(email_addresses) > 1:
            try:
                # find best matching mail adress to handelsnaam
                similarity_scores = [fuzz.token_sort_ratio(seller.handelsnaam, email) for email in email_addresses]
                best_match_index = similarity_scores.index(max(similarity_scores))
                best_match_email = email_addresses[best_match_index]
                print(best_match_email)
                return best_match_email, link    
            except:
                return email_addresses[0], link
        elif len(email_addresses) == 1:
            print(email_addresses[0])
            return email_addresses[0], link
        else:
            return None, None
    
    ## MAIN METHOD 1.2 - Use kvk nummer on SERP, find mail from footer or elsewhere
    # url = "https://google.serper.dev/search"

    # payload = json.dumps({
    # "q": seller.kvk_nummer,
    # "gl": "nl",
    # "hl": "nl",
    # "autocorrect": False,
    # "num": 10,
    # })
    # headers = {
    # 'X-API-KEY': '0bf5839a4610086319710dbe983018d71beea104',
    # 'Content-Type': 'application/json'
    # }

    # response = requests.request("POST", url, headers=headers, data=payload)
    # json_data = response.json()
    # all_links = json_data['organic']
    
    
    
    ## METHOD 1 - use the information/contact box
    
    ## METHOD 2 - use social media: LinkedIn
    
    
    ## METHOD 3 - use social media: twitter/facebook
    
    
    
    return None, None

def find_best_link(seller: Seller) -> str:
    # Method 1 - Use kvk nummer with google search
    method1_links = list(search(seller.kvk_nummer, start=1, stop=3)) # returns list of urls
    forbidden_websites = ['oozo', 'bizzy', 'drimble', 'kvk', 'drimble', 'bedrijvenpagina']

    # Method 2 - use handelsnaam with 'contact'
    method2_links = list(search(seller.handelsnaam + ' contact', start=1, stop=3)) # returns list of urls
    print('all contact links', method2_links)
    
    links = method1_links + method2_links
    
    valid_links = []
    for link in links:
        if all(forbidden_website not in link for forbidden_website in forbidden_websites):
            valid_links.append(link)
    links = valid_links
    
    for link in links:
        if 'contact' in link:
            return link
    
    # find most similar link using fuzz
    similarity_scores = [fuzz.token_sort_ratio(seller.handelsnaam, link) for link in links]
    best_match_index = similarity_scores.index(max(similarity_scores))
    best_match_link = links[best_match_index]
    
    #see if /contact exists
    if '/contact' in best_match_link:
        return best_match_link
    else:
        try:
            response = requests.get(normalize_url(best_match_link) + "/contact")
            if response.status_code == 200:
                return normalize_url(best_match_link) + "/contact"
        except:
            pass
    return best_match_link

def add_mails() -> list:
    """

    Returns:
    List of all emails, and also saves them to the db.
    """

    db_url = 'sqlite:///bol_verkopers.db'
    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Query the database for all sellers
    sellers = session.query(Seller).all()

    mail_list = []

    for seller in sellers:
        try:
            # skip sellers that already have an email address
            if not seller.totaal_aanbod:
                continue
            if (getattr(seller, "email_adress", None) and "@" in seller.email_adress) or int(seller.totaal_aanbod) > 1000:
                continue
            # Generate an email address using the handelsnaam
            email_address, personal_website = find_mail_and_website(seller)
            if not email_address:
                continue
            # Update the seller's email address in the database
            seller.email_adress = email_address
            seller.personal_website = personal_website
            mail_list.append(email_address)  # Add the generated email to the mail_list
            session.commit()
        except Exception as e:
            seller.email_adress = f"None - error occurred: {e}"
            seller.personal_website = f"None - error occurred: {e}"
            session.commit()
            traceback.print_exc()
            continue

    # Commit the changes to the database
    session.commit()
            

    # Commit the changes to the database
    session.commit()

    # Close the session
    session.close()

    return mail_list

if __name__ == "__main__":
    start_url = 'https://www.bol.com/nl/nl/s/?searchtext='
    search_topics = ['laptop', 'kettingslot', 'schoenenrek', 'etui', 'handdoek']
    crawler = WebCrawlerBol()
    crawler.add_seller_links(start_url, search_topics)
    
    seller_data = crawler.get_seller_data() 
    add_mails()
    crawler.close_connection()
    
    # get all emails
    sellers = crawler.session.query(Seller).all()
    for seller in sellers:
        if seller.email_adress:
            print(seller.email_adress)
            print(seller.products_link)
            print(seller.personal_website)
            print("----")
        
