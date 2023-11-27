import json
import requests
import pandas as pd
import re

def main():
    sealed_url = "https://raw.githubusercontent.com/taw/magic-sealed-data/master/sealed_extended_data.json"
    booster_req = requests.get(sealed_url)
    booster_data = json.loads(booster_req.content)
    
    analyze_code = 'unf'
    
    all_cards = pd.read_csv(r"C:\Users\axxro\Downloads\cards (3).csv")
    all_cards['card_id'] = all_cards["setCode"].str.lower() + ":" + all_cards["number"].str.lower()
    all_cards.set_index("card_id", inplace=True)
    all_cards = all_cards[~all_cards.index.duplicated()]
    # print(all_cards)
    
    master = pd.DataFrame(columns=["card_id", 'link_id', "name", "foil", "category", 'rarity'])
    
    sheets = {}
    
    
    for booster in booster_data:
        if booster['code'] != analyze_code:
            continue
        for s_name, sheet in booster['sheets'].items():
            print(s_name)
            cards = pd.DataFrame.from_records(sheet["cards"])
            cards["card_id"] = cards["set"] + ":" + cards["number"]
            cards["link_id"] = cards["set"] + ":" + cards["number"].str.replace(r'[a-z]', '', regex=True)
            cards["probability"] = cards["weight"] / sheet["total_weight"]
            mult_cards = cards.join(all_cards, "link_id", "inner", rsuffix="2")
            pt2 = cards.join(all_cards, "card_id", "inner", rsuffix="2")
            mult_cards = pd.concat([mult_cards, pt2[~pt2["card_id"].isin(mult_cards["card_id"])]], ignore_index=True)
            mult_cards.loc[mult_cards['frameEffects'].str.contains("showcase", na=False), "category"] = "showcase"
            mult_cards.loc[(mult_cards['frameEffects'].str.contains("extendedart", na=False)) & (mult_cards['category'] == ""), "category"] = "extended"
            mult_cards.loc[(mult_cards['borderColor'].str.contains("borderless", na=False)), "category"] = "borderless"
            mult_cards.loc[mult_cards['setCode'] == "REX", "category"] = "jurassic world"
            mult_cards.loc[mult_cards['setCode'] == "SPG", "category"] = "special guest"
            mult_cards.loc[mult_cards['setCode'] == "PLIST", "category"] = "the list"
            mult_cards.loc[mult_cards['promoTypes'].str.contains("galaxyfoil", na=False), "category"] = "galaxy"
            #print(mult_cards['category'].tolist())
            mult_cards['category'] = mult_cards['category'].fillna('none')
            mult_cards['rarity'] = mult_cards['rarity'].fillna('none')
            #master.extend(cards["card_id"])
            pivot_rarity = pd.pivot_table(mult_cards, values="probability", index="rarity", aggfunc="sum")
            pivot_cat = pd.pivot_table(mult_cards, values="probability", index="category", aggfunc="sum")
            mult_cards = mult_cards[['card_id', 'link_id', 'name', 'foil', 'category', 'rarity', 'probability']]
            master = master.merge(mult_cards, on=["card_id", 'link_id', "name", "foil", "category", 'rarity'], how="outer", suffixes=("", s_name))
            if "probability" in master.columns:
                master["probability"+s_name] = master["probability"]
                master.drop("probability", axis=1, inplace=True)
            mult_cards['price'] = ""
            mult_cards['impact'] = ""
            
            
            mult_cards.to_csv("build/"+s_name+".csv")
            pivot_rarity.to_csv("build/"+s_name+"_rarity.csv")
            pivot_cat.to_csv("build/"+s_name+"_cat.csv")
            
            #print(cards)
        full_weight = 0
        for b in booster['boosters']:
            full_weight += b['weight']
            for s, c in b['sheets'].items():
                if s not in sheets:
                    sheets[s] = 0
                sheets[s] += c * b['weight']
        for n in sheets.keys():
            sheets[n] /= full_weight
    
    master["probability"] = 0
    for n in sheets.keys():
        master["probability"] += master["probability"+n].fillna(0) * sheets[n]
    pivot_rarity = pd.pivot_table(master, values="probability", index="rarity", aggfunc="sum")
    pivot_cat = pd.pivot_table(master, values="probability", index="category", aggfunc="sum")
    master = master[['card_id', 'link_id', 'name', 'foil', 'category', 'rarity', 'probability']]
    master.to_csv("build/master.csv")
    pivot_rarity.to_csv("build/master_rarity.csv")
    pivot_cat.to_csv("build/master_cat.csv")
    print(master)
            
if __name__ == "__main__":
    main()
