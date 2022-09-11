# Test programs to try messing with data

import ijson
from scipy.sparse import csr_array
import numpy as np

Price_Data = {}

'''
with open("/Users/samzimmerman/Downloads/AllPrices.json", "rb") as f:
    data = ijson.kvitems(f, 'data')
    for card_id, prices in data:
        #print(card_id)
        try:
            Json_Data[card_id] = list(prices['paper']['cardkingdom']['retail']['normal'].values())[0]
        except:
            pass
'''

'''
with open("/Users/samzimmerman/Downloads/AllPrintings.json", "rb") as f2:
    data = ijson.items(f2, 'data.STX.cards.item')
    for each_card in data:
        print("~".join([each_card['uuid'], each_card['number'], each_card['name'], each_card['rarity']]))

with open("/Users/samzimmerman/Downloads/AllPrintings.json", "rb") as f2:
    data = ijson.items(f2, 'data.ASTX.cards.item')
    for each_card in data:
        print("~".join([each_card['uuid'], each_card['number'], each_card['name'], each_card['rarity']]))

with open("/Users/samzimmerman/Downloads/AllPrintings.json", "rb") as f2:
    data = ijson.items(f2, 'data.STA.cards.item')
    for each_card in data:
        print("~".join([each_card['uuid'], each_card['number'], each_card['name'], each_card['rarity']]))

'''

with open("/Users/samzimmerman/Downloads/AllPrintings.json", "rb") as f2:
    data = ijson.kvitems(f2, 'data.STX.booster.default.sheets')
    for sheetname, subdata in data:
        print(sheetname)
        for uuid, weight in subdata['cards'].items():
            print(uuid, weight)
