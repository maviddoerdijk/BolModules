"""
Define all models (given as Classes) for the keywords module here.
"""


class TopKeywords:
    """
    Class that saves all top useful keywords (length undefined) including their importance for this product and monthly search volume.
    """
    # 
    def __init__(self, product_title, product_link):
        self.product_title = product_title
        self.product_link = product_link
        self.keywords_data = []

    def add_keyword(self, keyword, importance, monthly_search_volume):
        # check if importance is an int 1-10
        if not isinstance(importance, int) or importance < 1 or importance > 10:
            raise ValueError("Importance should be an integer between 1 and 10.")

        # check if monthly_search_volume is an int
        if not isinstance(monthly_search_volume, int):
            raise ValueError("Monthly search volume should be an integer.")
        
        # check if keyword in keywords_data
        if any(keyword_data['keyword'] == keyword for keyword_data in self.keywords_data):
            raise ValueError(f"Keyword '{keyword}' already exists in the keywords data.")
        
        self.keywords_data.append({
            'keyword': keyword,
            'importance': importance,
            'monthly_search_volume': monthly_search_volume
        })