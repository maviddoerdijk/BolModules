import base64
import requests
import time
import os

class BolAPI:
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None
        self.token_expiry_time = 0  # To store when the token will expire
        self.base_url = 'https://api.bol.com'

    def get_access_token(self):
        """
        Fetches a new access token and updates the class with the token and expiration time.
        """
        # Encode the client_id and client_secret in Base64
        credentials = f'{self.client_id}:{self.client_secret}'
        encoded_credentials = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')

        # Token request URL and headers
        token_url = 'https://login.bol.com/token?grant_type=client_credentials'
        token_headers = {
            'Authorization': f'Basic {encoded_credentials}',
            'Accept': 'application/json'
        }

        # Request a new token
        response = requests.post(token_url, headers=token_headers)

        # Check if the request was successful
        if response.status_code == 200:
            token_data = response.json()
            self.access_token = token_data['access_token']
            # Calculate the expiry time based on the current time + 299 seconds
            self.token_expiry_time = time.time() + token_data['expires_in']
            print(f"New access token acquired: {self.access_token}")
        else:
            raise Exception(f"Failed to get access token: {response.status_code} - {response.text}")

    def _is_token_expired(self):
        """
        Checks if the current access token has expired.
        """
        return time.time() >= self.token_expiry_time

    def request(self, endpoint, params=None):
        """
        Makes a GET request to the API, ensuring the access token is valid.
        """
        # Refresh the token if it has expired
        if self.access_token is None or self._is_token_expired():
            self.get_access_token()

        # Set up the headers for the request with the OAuth2 bearer token
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Accept': 'application/vnd.retailer.v9+json'  # Add the correct Accept header
        }

        # Make the GET request
        url = self.base_url + endpoint
        response = requests.get(url, headers=headers, params=params)

        # Check if the request was successful
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"API request failed: {response.status_code} - {response.text}")


# Usage Example
if __name__ == "__main__":
    # Replace with your actual client ID and client secret
    client_id = os.environ.get('BOL_SELLER_ID')
    client_secret = os.environ.get('BOL_SELLER_SECRET')

    # Initialize the API client
    api_client = BolAPI(client_id, client_secret)

    # Define the URL and query parameters
    params = {
        'search-term': 'book',
        'period': 'MONTH',
        'number-of-periods': 1,
        'related-search-terms': 'true'
    }

    # Make the API request
    try:
        endpoint = '/retailer/insights/search-terms'
        response_data = api_client.request(endpoint, params)
        print(response_data)    
    except Exception as e:
        print(f"Error: {e}")
