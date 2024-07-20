import os
from requests_oauthlib import OAuth1
from dotenv import load_dotenv
import requests
from PIL import Image
import base64

class ResourceLib:
    """ResourceLib is a class that provides existing resources in the form of images.
    Methods of this class can be used to e.g. get images from a bol link, or to get an icon of a "arrow" based on the keyword "arrow"
    """
    
    def __init__(self):
        load_dotenv()
        self.path = "resources"
        if not os.path.exists(self.path):
            os.makedirs(self.path)
        self.auth = OAuth1(os.getenv('NOUN_KEY'), os.getenv('NOUN_SECRET'))
        self.endpoint = "https://api.thenounproject.com/v2"
        self.hexa_color_dict = {'white': 'ffffff', 'black': '000000'}
        self.resources = []
        
    def get_icon_from_keyword(self, keyword, color="white", size=25):
        """Downloads an icon based on the provided keyword."""
        
        if not color in self.hexa_color_dict.keys():
            raise Exception(f"Color {color} is not supported. Choose from {self.hexa_color_dict.keys()}")

        
        
        url = f"{self.endpoint}/icon?query={keyword}&limit=1&thumbnail_size=84&blacklist=1&limit_to_public_domain=1"
        response = requests.get(url, auth=self.auth)
        # check if request was successful with status code 200
        if response.status_code == 200:
            icon_data = response.json()
            icon_id = icon_data["icons"][0]["id"]
            url = f"{self.endpoint}/icon/{icon_id}/download?color={self.hexa_color_dict.get(color)}&filetype=png&size={size}"
            response = requests.get(url, auth=self.auth)
        else:
            raise Exception(f"Could not find icon. Status code: {response.status_code}")
        if response.status_code == 200:
            icon_data = response.json()
            base_64_str = icon_data["base64_encoded_file"]
            base_64_bytes = base64.b64decode(base_64_str)
            content_type = icon_data["content_type"]
            content_extension = content_type.split("/")[1]
            local_path = f"{self.path}/{keyword}.{content_extension}"
            with open(local_path, "wb") as f:
                f.write(base_64_bytes)
            icon_resource = IconResource(local_path, base_64_bytes)
            self.resources.append(icon_resource)
            return icon_resource
        else:
            raise Exception(f"Could not download icon. Status code: {response.status_code}")

class Resource:
    def __init__(self, local_path, img_data):
        self.local_path = local_path
        self.img_data = img_data
    
    def get_image_path(self):
        return self.local_path

class BolImagesResource(Resource):
    pass

class IconResource(Resource):
    def show(self):
        """Display the image."""
        img = Image.open(self.local_path)
        img.show()
    pass


if __name__ == "__main__":
    resource_lib = ResourceLib()
    resource = resource_lib.download_icon("trashcan")
    path = resource.get_image_path()
    print(path)
    