import re
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
import os
from dotenv import load_dotenv
load_dotenv()

def normalize_url(url, with_protocol=True):
    regex = r"^(https?:\/\/)?(www\.)?([-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*))"
    match = re.match(regex, url)

    if match:
        protocol = match.group(1) if match.group(1) else "https://"
        domain = match.group(3)

        # Group 1: https://
        # Group 2: www.
        # Group 3: example.com/test

        # Removing path and other segments to only get the domain
        domain_end_index = domain.find("/")
        if domain_end_index != -1:
            domain = domain[:domain_end_index]

        if with_protocol:
            return f"{protocol}{domain}"
        else:
            return domain
    else:
        return "Invalid URL"
    
def send_brevo_mail(recipient:str, html_content:str, subject:str, customername = "Klant"):
    """
    recipient: str, email address of the recipient
    html_content: str, the html content of the email
    subject: str, the subject of the email
    
    returns json with message and response or error 
    ```{message:..., response:...}``` or ```{message:..., error:...}```
    """
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = os.getenv("SENDINBLUE_API_KEY")

    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
    # subject = "from the Python SDK!"
    sender = {"name":"ListinQ","email":"info@listinq.nl"}
    # html_content = "<html><body><h1>This is my first transactional email </h1></body></html>"
    to = [{"email":recipient,"name":customername}]
    params = {"parameter":"My param value","subject":"New Subject"}
    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(to=to, html_content=html_content, sender=sender, subject=subject)

    try:
        api_response = api_instance.send_transac_email(send_smtp_email)
        return {"message": "Mail sent", "response": api_response}
    except ApiException as e:
        print("Exception when calling SMTPApi->send_transac_email: %s\n" % e)
        return {"message": "Mail not sent", "error": str(e)}
    

def replace_page_number(url, new_page_number): 
    # Use a regular expression to find the page number in the URL
    pattern = r'page=(\d+)'
    match = re.search(pattern, url)
    
    if match:
        # If a match is found, extract the current page number
        current_page_number = match.group(1)
        
        # Replace the current page number with the new page number
        new_url = re.sub(pattern, f'page={new_page_number}', url)
        return new_url
    else:
        # If no match is found, return the original URL
        return url
    
    
    
def hello_world():
    return print("hello world")