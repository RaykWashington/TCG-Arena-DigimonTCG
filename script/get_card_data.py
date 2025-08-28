import requests
import jmespath
from pathlib import Path
import json

url = "https://apitcg.com/api/digimon/cards"
script_path = Path(__file__).parent
card_data_name = 'card_data_raw.json'
card_list_name = "DigimonTCG_card_ist"


header = {
"x-api-key" : "b378d1090d0db9127887ef7d43392dec74f236cf4de0ddf16d01e1bbe1b53633"
}

param ={
"limit" : "100",
}


#formato para o TCG-Arena
search_string = """
    data[].{id : id,
    face:{
        front:{
            name: join('-', [name, code]),
            type: cardType, 
            cost: playCost, 
            image: images.small
            }
        }, 
    name: join('-', [name, code]),
    type: cardType,
    level: level,
    color: colors[0]
    cost: playCost, 
    set: set.name}"""

session = requests.Session() #aparentemente reduz o peso da coisa de lidar com varias paginas, chamo o request pela session

def get_card_dataset(): #iterar nas paginas


    first_page = session.get(url, params=param, headers=header).json() #pega os dados da primera pagina
    yield first_page #faz da funcao um generator
    num_pages = first_page['totalPages'] #pegando da info de paginação da propria api

    for param["page"] in range(2, num_pages + 1):
        next_page = session.get(url, headers = header, params = param).json()
        yield next_page
    
#gera o arquivo database

for page in get_card_dataset():
    with open(script_path / card_data_name, '+a', encoding='utf-8') as file:
        json.dump(page, file, ensure_ascii=False, indent= 4)
        print("Database criada...")

#indexando as cartas

with open(script_path / card_data_name, '+r') as file:
    card_data = json.load(file)
    mapped = jmespath.search(search_string, card_data)
    indexed = {str(item['id']): item for item in card_data} #dict comprehension pra indexar pelo id
    print("Cartas indexadas...")

#gera o card list

with open(script_path / card_list_name, 'w', encoding='utf-8') as file:
    json.dump(indexed, file, ensure_ascii= False, indent= 4)
    print("Card List salvo.")

