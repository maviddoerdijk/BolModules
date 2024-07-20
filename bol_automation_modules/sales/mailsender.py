import requests
from bs4 import BeautifulSoup
import re
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
from googlesearch import search 
import traceback
import os 
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import time
from string import Template
import base64
# from ..python_overig.helperfunctions import normalize_url, send_brevo_mail, replace_page_number
from helpers.helperfunctions import send_brevo_mail
from dotenv import load_dotenv
load_dotenv()







def send_all_mails(include_ai_description: bool = False) -> str:  
    db_url = 'sqlite:///bol_verkopers.db'
    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Query the database for all sellers
    sellers = session.query(Seller).all()
    count = 0 
    already_sent = []
    for seller in sellers:
        if "@" in seller.email_adress:
            print(seller.email_adress, seller.personal_website)
            for forbidden in ['jaato', 'bedrijvenpagina', 'viduate', 'senseglove', 'sense.info', 'arkansas', 'vme', 'telefoonboek', 'infinitygoods']:
                if forbidden in seller.email_adress:
                    print('forbidden')
                    continue
            if not 'nl' in seller.personal_website:
                print('forbidden because not nl')
                continue
            if seller.email_adress in already_sent:
                continue
            print('sending to ', seller.email_adress)
            mimemsg = MIMEMultipart("alternative")
            
            ## Create the body of the message
            if include_ai_description:
                subject = "Kansen voor Verbetering van uw Bol.com Listings"
                # find first product from product_link
                all_products = find_all_products(seller)
                first_product = all_products[0]
                link_to_first_product = 'https://bol.com' + first_product['href']
                
                product_page = requests.get(link_to_first_product)

                
                description_html = get_description_soup_from_product_page(product_page) # list of all html contents
                if description_html is None:
                    print('no description html')
                    continue
                
                
                title_str = get_title_soup_from_product_page(product_page)
                if not title_str:
                    print('no title html')
                    continue
                title_soup = BeautifulSoup(title_str, 'lxml')
                title_first_word = title_soup.text.split(' ')[0]
                
                
                # save description and title html to file
                with open(f'csv/{title_first_word}.txt', 'w', encoding='utf-8') as f:
                    f.write(str(title_str))
                
                with open(f'csv/{title_first_word}_description.html', 'w', encoding='utf-8') as f:
                    f.write(str(description_html))
                
                input_filename = 'csv/ListingAnalyse.xlsx'
                output_filename = 'csv/ListingAnalyse{title_first_word}.xlsx'
                
                # get_analyse_product_listing_csv(input_filename, output_filename, title_str, description_html)
                
                
                
                # save product {title, description, analysis} to db

                quit()                
                
                
                
                
                content_text = ""

                
            else:
                subject = "Kansen voor Verbetering van uw Bol.com Listings"
                # add text to the email
                content_text = f"""\
Hallo {seller.handelsnaam},

Ik kwam uw producten tegen op bol.com en uw persoonlijke website en merkte op dat er ruimte is voor optimalisatie. Toen vond ik deze contactgegevens op {seller.personal_website}. U biedt al sterke producten aan, maar met enkele aanpassingen in de content van uw listing kunnen we uw verkopen aanzienlijk verhogen. Denk hierbij aan professionele infographics, productbeschrijvingen, verbeteringen in de afbeeldingen, en meer.

Na veel ervaring op te doen in het bouwen van de content voor listings, en na samenwerking met veel bol salespartners, denk ik dat ik u hierin goed kan ondersteunen. Een aangescherpte productbeschrijving en verbeterde afbeeldingen kunnen al een groot verschil maken.

Zou u interesse hebben in een gratis en vrijblijvend gesprek van 15 minuten om de mogelijkheden te bespreken? U kunt een tijdstip kiezen via deze link: calendly.com/listinq/consult.

Als u meer wilt weten over het verbeteren van uw producten, kunt u mij altijd even bellen via (06 4066 9897) of een mailtje terug sturen!

Ik hoor graag van u.

Met vriendelijke groet,
David Moerdijk

P.S.
Bent u niet geïnteresseerd? Antwoord mij met "niet geïnteresseerd", waarna ik geen contact meer zal zoeken. 
                """
            mimemsg.attach(MIMEText(content_text, "plain"))
            
            
            sender = "davidmoerdijk@gmail.com"
            recipients = [seller.email_adress]
            password = os.getenv("APP_PASSWORD_DM")
            send_smtp(subject, mimemsg, sender, recipients, password)
            count += 1
            already_sent.append(seller.email_adress)
            
            time.sleep(20)

    

    return "mail sent"



def send_smtp(subject, mimemsg: MIMEMultipart, sender, recipients, password):
    msg = mimemsg
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = ", ".join(recipients)
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp_server:
        smtp_server.login(sender, password)
        smtp_server.sendmail(sender, recipients, msg.as_string())
    # print("Message sent!")

def send_product_sample_mail(input_picture):
    # Create a multipart message and set headers
    mimemsg = MIMEMultipart("alternative")
    subject = "Kansen voor Verbetering van uw Bol.com Listings"
    # add image to the email
    mimemsg.attach(MIMEImage(open(input_picture, "rb").read(), name=os.path.basename(input_picture)))   
    
    sender = "info@listinq.nl"
    recipients = ["davidmoerdijk@gmail.com"]
    password = os.getenv("APP_PASSWORD_LISTINQ")
    send_smtp(subject, mimemsg, sender, recipients, password)
    return

def send_all_product_sample_mails():
    return



    
def send_company_mail(input_file_path, input_picture_path, company_name, recipient_email):
    with open(input_file_path, 'r', encoding='utf-8') as file:
        html_content = file.read()

    
    with open(input_picture_path, 'rb') as f:
        picture = f.read()
        
    
    # transform picture to svg
    encoded_image = base64.b64encode(picture).decode()
    t = Template(html_content)
    html_content = t.safe_substitute(bedrijfsnaam=company_name, encoded_image=encoded_image)
    with open("embedded_image.html", "w", encoding='utf-8') as file:
        file.write(html_content)
        
        
    return_msg = send_brevo_mail(recipient_email, html_content, f"Persoonlijk aanbod {company_name}!", customername=company_name)
    print(return_msg)
    return return_msg
    
def send_company_mail_with_smtp(input_file_path, input_picture_path, company_name, product_name, recipient_email):
    with open(input_file_path, 'r', encoding='utf-8') as file:
        html_content = file.read()

    
    with open(input_picture_path, 'rb') as f:
        picture = f.read()
        
    
    # transform picture to svg
    # encoded_image = base64.b64encode(picture).decode()
    t = Template(html_content) 
    # give a src for the image <img src="$imgsrc" alt="Embedded Image" width="280" height="280"> (for base64 -> data:image/jpeg;base64,$encoded_image )
    html_content = t.safe_substitute(bedrijfsnaam=company_name, imgsrc="cid:image1", productnaam=product_name)
    with open("embedded_image.html", "w", encoding='utf-8') as file:
        file.write(html_content)
        
    # Create a multipart message and set headers
    mimemsg = MIMEMultipart("alternative")
    subject = f"Aanvraag custom design {company_name}!"
    # add image to the email
    mimeimg = MIMEImage(picture, name=os.path.basename(input_picture_path))
    mimeimg.add_header('Content-ID', '<image1>')
    mimemsg.attach(mimeimg)   
    mimemsg.attach(MIMEText(html_content, "html"))
    
    sender = "info@listinq.nl"
    recipients = [recipient_email]
    password = os.getenv("APP_PASSWORD_LISTINQ")
    if not password:
        raise ValueError("Password not found")
    send_smtp(subject, mimemsg, sender, recipients, password)
    return


if __name__ == "__main__":
    # send_company_mail('../docs/New Template.html', '../pre_photos/extra/trashcan1.jpg', 'Bol.com bedrijf')
    send_company_mail_with_smtp('../docs/New Template.html', 'temp/trashcan_image.png', 'David Moerdijk Bedrijf', 'prullenbak', 'davidbenmoerdijk@gmail.com')

    # send_product_sample_mail(input_picture=os.path.join('post_photos_folders', 'trashcans', 'trashcan_voorbeeld.jpg'))
    
    
    
    
    
    
    
    
    
    
    
# brevo api
