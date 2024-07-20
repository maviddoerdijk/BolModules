from .init_db import WebCrawlerBol, Seller
from .mailsender import send_company_mail_with_smtp
from python_image.edit_image import add_trash_can_to_image
import requests
import time
import traceback


def run_sales_mails_for_search_term(search_term: str):
    
    crawler = WebCrawlerBol()
    # Normally, the search term would be passed as an argument to the function, but I have already run them for "prullenbank"
                # crawler.add_seller_links(start_url, search_topics)
                
                # seller_data = crawler.get_seller_data() 
                # add_mails()
                # crawler.close_connection()
    
    
                
    
    # get all emails
    sellers = crawler.session.query(Seller).all()
    for seller in sellers:
        count = 0
        if seller.email_adress:
            count += 1
            product_link_soup = crawler.get_soup(seller.products_link)
            # find a href in soup with class product-image
            all_product_titles = product_link_soup.find_all("a", class_="product-title")
            # # find product link with "prullenbak" in its title
            sent_mails = ['info@pimxl.nl','info@debries.eu','info@dealtraders.nl','info@dennepark.nl','info@koopalles.nl','sales@brender.nl']
            for product_title in all_product_titles:
                if "prullenbak" in product_title.text.lower():
                    product_href = product_title.get("href")
                    product_page = crawler.get_soup("https://bol.com/" + product_href)
                    print("product_page: " + "https://bol.com/" + product_href)
                    main_image = product_page.find("img", {'data-test':'product-main-image'})   
                    image_link = main_image.get("src")
                    print("image_link: ", image_link)
                    image = requests.get(image_link)
                    with open('temp/trashcan_image_bol.jpg', 'wb') as file:
                        file.write(image.content)
                    # add trash can to image
                    trashcan_image_path = add_trash_can_to_image('temp/trashcan_image_bol.jpg')
                    if not seller.email_adress in sent_mails:
                        try:
                            success = send_company_mail_with_smtp('../docs/New Template.html', trashcan_image_path, seller.handelsnaam, seller.topic, seller.email_adress)
                            sent_mails.append(seller.email_adress)
                            time.sleep(5)
                        except:
                            print('error sending mail')
                            print(traceback.print_exc())
                    time.sleep(5)
                    # if success:
                    #     print('Mail sent to ', seller.email_adress)
                    break
            
            
    #TODO:create new image with edit_image    
    #TODO: delete created image

        

if __name__ == "__main__":
    run_sales_mails_for_search_term(search_term="prullenbak")
    