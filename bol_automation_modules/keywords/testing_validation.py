from models import TopKeywords
import random

def create_mock_top_keywords():
    product_title = "Blast box - Ballonnen prik spel - Voor volwassenen en kinderen - Spannend - 2 tot 4 spelers - Vanaf 4 jaar - Familie spel"
    product_link = "https://www.bol.com/nl/nl/p/blast-box-ballonnen-prik-spel-voor-volwassenen-en-kinderen-spannend-2-tot-4-spelers-vanaf-4-jaar-familie-spel/9300000181473082/?bltgh=gNzk8qsqYAIw37maY0VPrg.2_13.14.ProductTitle"
    
    top_keywords = TopKeywords(product_title, product_link)
    
    # Hardcoded Dutch keywords
    keywords = ['ballonnen spel voor vakantie', 'ballonnen spel volwassenen', 'ballonnen spel voor groepen', 'ballonnen spel voor park', 'ballonnen spel kinderen', 'ballonnen spel spannend', 'spel voor 2 spelers', 'ballonnen spel 4 spelers', "ballonnen spel voor collega's", 'ballonnen spel voor tuin', 'ballonnen spel voor tieners', 'spannend spel', 'ballonnen spel voor vereniging', 'ballonnen spel gezelschap', 'ballonnen spel voor peuters', 'ballonnen spel familie', 'spel vanaf 4 jaar', 'spel voor 4 spelers', 'ballonnen spel vanaf 4 jaar', 'ballonnen spel voor school', 'ballonnen spel voor ouderen', 'ballonnen spel voor evenementen', 'ballonnen spel voor festivals', "ballonnen spel voor baby's", 'ballonnen spel voor koppels', 'ballonnen spel voor picknicks', 'spel voor volwassenen', 'ballonnen spel 2 spelers', 'gezelschapsspel', 'ballonnen spel voor verjaardagen', 'ballonnen spel voor teams', 'ballonnen spel voor binnen', 'ballonnen spel voor familie', 'kinderspel', 'ballonnen spel voor vrienden', 'ballonnen spel voor sportdagen', 'ballonnen spel voor camping', 'ballonnen prikken', 'prik spel', 'ballonnen spel voor klas', 'ballonnen spel voor strand', 'ballonnen spel voor kleuters', 'ballonnen spel voor buurtfeest', 'ballonnen spel voor club', 'ballonnen spel', 'ballonnen spel voor schoolreis', 'familiespel', 'spel voor kinderen', 'ballonnen spel voor buiten', 'ballonnen spel voor feestjes']
    
    # Adding 30 mock keywords with random monthly search volume and importance
    for keyword in keywords:
        importance = random.randint(1, 10)
        monthly_search_volume = random.randint(50, 500)
        top_keywords.add_keyword(keyword, importance=importance, monthly_search_volume=monthly_search_volume)
    
    return top_keywords