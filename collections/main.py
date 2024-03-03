from petpy import Petfinder
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('PETFINDER_API_KEY')
secret_key = os.getenv('PETFINDER_SECRET_KEY')

pf = Petfinder(key=api_key, secret=secret_key)
animals = pf.animals()

animal_ids = []
for i in animals['animals'][0:3]:
    animal_ids.append(i['id'])
    
animal_data = pf.animals(animal_id=animal_ids)
print(animal_data)

# Returning a pandas DataFrame of the first 150 animal results
#animals = pf.animals(results_per_page=50, pages=3, return_df=True)
