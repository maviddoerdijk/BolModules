"""
Module for keywords; analyzing, extracting, and manipulating data from the bol website.
"""
from models import TopKeywords
from plotting import plot_top_keywords


def main():
    #TODO: implement that it automatically gets title from bol.com instead of manually having to add it
    topkeywords = TopKeywords("Markttrendanalyse")
    # save to file in /resources
    topkeywords.save_to_file()

    for keyword_data in topkeywords.keywords_data:
        print(keyword_data['keyword'] + " " + str(keyword_data['monthly_search_volume']))
    
if __name__ == "__main__":
    #TODO: reformat code into actual function
    main()