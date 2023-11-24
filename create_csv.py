import json
import requests
import pandas as pd
import re

def main():
    sealed_url = "https://raw.githubusercontent.com/taw/magic-sealed-data/master/sealed_extended_data.json"
    booster_req = requests.get(sealed_url)
    booster_data = json.loads(booster_req.content)
    
    analyze_code = 'lci-set'
    
    all_cards = pd.read_csv(r"/Users/samzimmerman/Downloads/AllPrintingsCSVFiles/cards.csv")
    all_cards['card_id'] = all_cards["setCode"].str.lower() + ":" + all_cards["number"].str.lower()
    all_cards.set_index("card_id", inplace=True)
    all_cards = all_cards[~all_cards.index.duplicated()]
    print(all_cards)
    
    master = list()
    
    for booster in booster_data:
        if booster['code'] != analyze_code:
            continue
        for s_name, sheet in booster['sheets'].items():
            print(s_name)
            cards = pd.DataFrame.from_records(sheet["cards"])
            cards["card_id"] = cards["set"] + ":" + cards["number"]
            cards["probability"] = cards["weight"] / sheet["total_weight"]
            master.extend(cards["card_id"])
            cards.to_csv("build/"+s_name+".csv")
            #print(cards)
    master = list(set(master))
    master = sorted(master, key=lambda x: (x.split(":")[0], int(re.sub(r'[a-z]', '', x.split(":")[1]))))
    for m in master:
        st, nm = m.split(":")
        cnm = re.sub(r'[a-z]', '', nm)
        clean = st+":"+cnm
        print(f"{m};{all_cards.loc[clean, 'name']}")
            
if __name__ == "__main__":
    main()
