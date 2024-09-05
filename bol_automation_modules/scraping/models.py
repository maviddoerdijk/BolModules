"""
Define all models (given as Classes) for the keywords module here.
"""
import json
import os

from keywordscrape import get_keyword_volume
from scraping.bol_api_connection import BolAPI


class TopKeywords:
    """
    Class that saves all top useful keywords (length undefined) including their importance for this product and monthly search volume.
    """
    # 
    def __init__(self, product_title):
        self.product_title = product_title
        self.keywords_data = []
        self.initialize_bol_api()
        
    def initialize_bol_api(self):
        client_id = os.environ.get('BOL_SELLER_ID')
        client_secret = os.environ.get('BOL_SELLER_SECRET')

        # Initialize the API client
        self.bol_api_client = BolAPI(client_id, client_secret)
        
        

    def add_keyword(self, keyword, importance, monthly_search_volume):
        # check if importance is an int 1-10
        if not isinstance(importance, int) or importance < 1 or importance > 10:
            try:
                importance = int(importance)
            except:
                raise ValueError("Importance should be an integer between 1 and 10.")

        # check if monthly_search_volume is an int
        if not isinstance(monthly_search_volume, int):
            try:
                monthly_search_volume = int(monthly_search_volume)
            except Exception as e:
                raise ValueError(f"Monthly search volume should be an integer. You gave '{monthly_search_volume}' of type {type(monthly_search_volume)}. Conversion of types went wrong because {e}")
        
        # check if keyword in keywords_data
        if any(keyword_data['keyword'] == keyword for keyword_data in self.keywords_data):
            # raise ValueError(f"Keyword '{keyword}' already exists in the keywords data.")
            return None
        
        self.keywords_data.append({
            'keyword': keyword,
            'importance': importance,
            'monthly_search_volume': monthly_search_volume
        })
        return True
    
    def _get_all_keywords(self):
        return [element['keyword'] for element in self.keywords_data]
    
    def get_volumes_legacy(self, max_recursion_depth=3, input_keywords=[]):
        # keep a list of all keywords that have already been parsed on website for volumes
        parsed_keywords = []
        
        recursion_round = 1
        if not input_keywords:
            # first round gets volumes for all words in title
            all_words_in_title = self.product_title.split('-')
            all_words_in_title = [keyword.strip() for keyword in all_words_in_title]
            print("ALL KEYWORDS IN TITLE")
            print(all_words_in_title)
            keyword_data = get_keyword_volumes(all_words_in_title)
        else:
            keyword_data = get_keyword_volumes(input_keywords)
        
        for element in keyword_data:
            keyword = element.get('keyword')
            monthly_search_volume = element.get('monthly_search_volume')
            importance = 1 # later, in recursive cases, importances of 2,3 etc get added
            self.add_keyword(keyword, importance, monthly_search_volume)
        parsed_keywords.extend(all_words_in_title)
        
        # all other rounds recursively add keywords
        while recursion_round < max_recursion_depth:
            keywords_to_parse = self._get_all_keywords().copy()
            keywords_to_parse = [keyword.strip() for keyword in keywords_to_parse]
            # remove all keywords that have already been parsed
            keywords_to_parse = [keyword for keyword in keywords_to_parse if keyword not in parsed_keywords]

            if not keywords_to_parse:
                break
            
            keyword_data = get_keyword_volumes(keywords_to_parse)
            
            for element in keyword_data:
                keyword = element.get('keyword')
                if keyword not in parsed_keywords:
                    monthly_search_volume = element.get('monthly_search_volume')
                    importance = recursion_round + 1
                    self.add_keyword(keyword, importance, monthly_search_volume)
                    parsed_keywords.append(keyword)
            
            recursion_round += 1
    
    # def get_volume(self, keyword):
    #     """
        
    #     Documentation sources:
    #     1. Search terms usage - https://api.bol.com/retailer/public/Retailer-API/v9/functional/retailer-api/search-terms.html
    #     """
    #     base_url = 's https://api.bol.com/retailer' # TODO: set to self.base_url
        
        
        
    #     raise NotImplementedError("This function is not yet implemented.")
            
    # def get_trending_volumes(self):
    #     # Step 1: Get input keywords from the bol.com page (categories etc)
    #     input_keywords_trending = []
        
    #     # Step 2: get volumes for these keywords
    #     self.get_volumes(input_keywords=input_keywords_trending)
        
            
    def _create_filename(self):
        return f"resources/{self.product_title.split('-')[0].strip()}.json"
            
    def save_to_file(self):
        """
        Save as JSON-file, in such a manner that it can easily be loaded again later using load_from_file
        """
        with open(self._create_filename(), 'w') as file:
            json.dump(self.keywords_data, file)
    
    def load_from_file(self, filename=None):
        """
        Load from a JSON-file that was saved using save_to_file
        
        filename : Normally not recommended, but this parameter can be used to overrule the standard filename!
        """
        if not filename:
            # only use filename to overwrite
            filename = self._create_filename()
        with open(filename, 'r') as file:
            keywords_data = json.load(file)
        self.keywords_data.extend(keywords_data)