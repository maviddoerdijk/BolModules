import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))) # only needed for local testing
from sales.init_db import Seller
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


db_url = 'sqlite:///bol_verkopers.db'
engine = create_engine(db_url)
Session = sessionmaker(bind=engine)
session = Session()

# Query the database for all sellers
sellers = session.query(Seller).all()
count = 0 
already_sent = []

handelsnamen = []
for seller in sellers:  
    if seller.handelsnaam:
        handelsnaam_20p = '%20'.join(seller.handelsnaam.split(" "))
        search_link = f"https://www.linkedin.com/search/results/all/?keywords={handelsnaam_20p}"
        handelsnamen.append(seller.handelsnaam)
        
import csv
# save to csv
with open('handelsnamen.csv', mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Handelsnaam'])  # Write header
    for handelsnaam in handelsnamen:
        writer.writerow([handelsnaam])