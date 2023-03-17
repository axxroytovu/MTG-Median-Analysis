# strixhaven analysis

import numpy as np
import ijson
import sealed
import pandas as pd
import matplotlib.pyplot as plt
from tqdm import tqdm
import datetime
import itertools as itr

def get_card_list(Json_Data):
    Cards = {}

    with open("json/AllSetFiles/SNC.json", "rb") as f2:
        data = ijson.items(f2, 'data.cards.item')
        dq = tqdm(data)
        dq.set_description("Reading core set cards")
        for card in dq:
            try:
                i = int(card['number'])
            except:
                #print(card['name'], card['number'])
                continue
            name = card['name']
            if name not in Cards:
                Cards.update({name: sealed.card(card)})
            if i < 262:
                Cards[name].add_style(card, "baseline")
            elif i >= 262 and i < 272:
                Cards[name].add_style(card, "basicLand", unique=True)
            elif i >= 272 and i < 282:
                Cards[name].add_style(card, "showcaseLand", unique=True)
            elif i >= 282 and i < 296:
                Cards[name].add_style(card, "borderless")
            elif i >= 296 and i < 341:
                Cards[name].add_style(card, "gilded")
            elif i >= 341 and i < 350:
                Cards[name].add_style(card, "skyscraper")
            elif i >= 350 and i < 361:
                Cards[name].add_style(card, "otherShowcase")
            elif i >= 361 and i < 406:
                Cards[name].add_style(card, "gildedFoil")
            elif i >= 406 and i < 441:
                Cards[name].add_style(card, "coreExtended")
            elif i >= 441 and i < 450:
                Cards[name].add_style(card, "foilEtched")
            elif i == 450:
                Cards[name].add_style(card, "boxTopper")
            else:
                Cards[name].add_style(card, "promo")
        dq.close()
        del(dq)
        
    TheList = pd.read_csv("json/TheList.csv")

    with open("json/AllSetFiles/PLIST.json", 'rb') as f3:
        with open("json/AllSetFiles/SLX.json", 'rb') as f4:
            data = ijson.items(f3, 'data.cards.item')
            data2 = ijson.items(f4, 'data.cards.item')
            dq = tqdm(itr.chain(data, data2))
            dq.set_description("Reading the list")
            validNames = TheList[TheList['SNC List']==1.0]["Name"].values
            for card in dq:
                name = card['name']
                if name in validNames:
                    if name not in Cards:
                        Cards.update({name: sealed.card(card)})
                    Cards[name].add_style(card, "theList")
            dq.close()
            del(dq)

    with open("json/AllSetFiles/NCC.json", 'rb') as f4:
        data = ijson.items(f4, 'data.cards.item')
        dq = tqdm(data)
        dq.set_description("Reading commander cards")
        for card in dq:
            if int(card['number']) < 11:
                if card['name'] not in Cards:
                    Cards.update({card['name']: sealed.card(card)})
                Cards[card['name']].add_style(card, 'commander')
            elif int(card['number']) >= 86 and int(card['number']) < 94:
                if card['name'] not in Cards:
                    Cards.update({card['name']: sealed.card(card)})
                Cards[card['name']].add_style(card, 'commander')
            elif int(card['number']) >= 94 and int(card['number']) <= 185:
                if card['name'] not in Cards:
                    Cards.update({card['name']: sealed.card(card)})
                Cards[card['name']].add_style(card, 'commanderExtended')
        dq.close()
        del(dq)

    cq = tqdm(Cards.items())
    cq.set_description("Assigning card prices")
    for k,v in cq:
        v.add_prices(Json_Data)
    cq.close()
    del(cq)
    
    return Cards

def build_slots(Cards):
    Slots = {}
    Slots["land"] = sealed.kit()
    Slots["foilLand"] = sealed.kit()
    Slots["common"] = sealed.kit()
    Slots["uncommon"] = sealed.kit()
    Slots["rareMythic"] = sealed.kit()
    Slots["rareMythicWC"] = sealed.kit()
    Slots['rawFoil'] = sealed.kit()
    Slots["art"] = sealed.kit()
    Slots["setFoil"] = sealed.kit()
    Slots["showcaseCU"] = sealed.kit()
    Slots["theList"] = sealed.kit()
    Slots['theListRaw'] = sealed.kit()
    Slots["collectorFoilRM"] = sealed.kit()
    Slots["collectorFoilSCU"] = sealed.kit()
    Slots["showcaseRM"] = sealed.kit()
    Slots["extendedCommander"] = sealed.kit()
    Slots["extendedCore"] = sealed.kit()
    Slots["foilRareMythic"] = sealed.kit()
    Slots["showcaseCU"] = sealed.kit()
    Slots["foilUncommon"] = sealed.kit()
    Slots["foilCommon"] = sealed.kit()
    Slots["foilMetroLand"] = sealed.kit()
    Slots["gildedFoils"] = sealed.kit()
    Slots['boxTopper'] = sealed.kit()
    Slots['showcase'] = sealed.kit()
    
    showcaseStyles = set(["borderless", "gilded", "skyscraper", "otherShowcase"])
    rareWeight = {"common": 8, "uncommon": 4, "rare": 2, "mythic": 1}

    cq = tqdm(Cards.values())
    cq.set_description("Assigning slots")
    for c in cq:
        if "baseline" in c.styles:
            if c.rarity == "common":
                Slots["foilCommon"].add_card(c.prices["baseline"]['foil'])
                cstyles = set(c.styles) & showcaseStyles
                for s in cstyles:
                    Slots['common'].add_card(c.prices[s]['normal'], 0.33/len(s))
                Slots["common"].add_card(c.prices["baseline"]['normal'], 1 if len(cstyles) == 0 else 0.67)
            elif c.rarity == "uncommon":
                Slots['foilUncommon'].add_card(c.prices['baseline']['foil'])
                cstyles = set(c.styles) & showcaseStyles
                for s in cstyles:
                    Slots['uncommon'].add_card(c.prices[s]['normal'], 0.33/len(s))
                Slots["uncommon"].add_card(c.prices["baseline"]['normal'], 1 if len(cstyles) == 0 else 0.67)
            elif c.rarity == "rare":
                Slots['foilRareMythic'].add_card(c.prices["baseline"]['foil'], 2)
                cstyles = set(c.styles) & showcaseStyles
                for s in cstyles:
                    Slots['rareMythic'].add_card(c.prices[s]['normal'], 0.67/len(s))
                    Slots['rareMythicWC'].add_card(c.prices[s]['normal'], 0.67/len(s))
                Slots["rareMythic"].add_card(c.prices["baseline"]['normal'], 2 if len(cstyles) == 0 else 1.33)
                Slots["rareMythicWC"].add_card(c.prices["baseline"]['normal'], 2 if len(cstyles) == 0 else 1.33)
            elif c.rarity == "mythic":
                Slots['foilRareMythic'].add_card(c.prices["baseline"]['foil'])
                cstyles = set(c.styles) & showcaseStyles
                for s in cstyles:
                    Slots['rareMythic'].add_card(c.prices[s]['normal'], 0.33/len(s))
                    Slots['rareMythicWC'].add_card(c.prices[s]['normal'], 0.33/len(s))
                Slots["rareMythic"].add_card(c.prices["baseline"]['normal'], 1 if len(cstyles) == 0 else 0.67)
                Slots["rareMythicWC"].add_card(c.prices["baseline"]['normal'], 1 if len(cstyles) == 0 else 0.67)
        if "commander" in c.styles:
            Slots["rareMythicWC"].add_card(c.prices['commander']['normal'], rareWeight[c.rarity])
        if "gildedFoil" in c.styles:
            Slots['gildedFoils'].add_card(c.prices['gildedFoil']['foil'], rareWeight[c.rarity])
            if c.rarity in ["common", "uncommon"]:
                Slots["collectorFoilSCU"].add_card(c.prices['gildedFoil']['foil'], rareWeight[c.rarity])
            else:
                Slots["collectorFoilRM"].add_card(c.prices['gildedFoil']['foil'], rareWeight[c.rarity])
        for s in showcaseStyles & set(c.styles):
            Slots['showcase'].add_card(c.prices[s]['normal'], rareWeight[c.rarity])
            if c.rarity in ["common", "uncommon"]:
                Slots["showcaseCU"].add_card(c.prices[s]['normal'], rareWeight[c.rarity])
                Slots["collectorFoilSCU"].add_card(c.prices[s]['foil'], rareWeight[c.rarity])
                Slots['showcase'].add_card(c.prices[s]['normal'], rareWeight[c.rarity])
            else:
                Slots["showcaseRM"].add_card(c.prices[s]['normal'], rareWeight[c.rarity])
                Slots["collectorFoilRM"].add_card(c.prices[s]['normal'], rareWeight[c.rarity])
        if "foilEtched" in c.styles:
            Slots["collectorFoilRM"].add_card(c.prices['foilEtched']['foil'], rareWeight[c.rarity])
        if "basicLand0" in c.styles:
            Slots["land"].add_card(c.prices["basicLand0"]['normal'], 2)
            Slots["foilLand"].add_card(c.prices["basicLand0"]['foil'], 2)
            Slots["land"].add_card(c.prices["basicLand1"]['normal'], 2)
            Slots["foilLand"].add_card(c.prices["basicLand1"]['foil'], 2)
            Slots["land"].add_card(c.prices["showcaseLand2"]['normal'])
            Slots["foilLand"].add_card(c.prices["showcaseLand2"]['foil'])
            Slots["land"].add_card(c.prices["showcaseLand3"]['normal'])
            Slots["foilLand"].add_card(c.prices["showcaseLand3"]['foil'])
            Slots["foilMetroLand"].add_card(c.prices["showcaseLand2"]['foil'])
            Slots["foilMetroLand"].add_card(c.prices["showcaseLand3"]['foil'])
        if "theList" in c.styles:
            Slots['theListRaw'].add_card(c.prices["theList"]['normal'])
        if "coreExtended" in c.styles:
            Slots['extendedCore'].add_card(c.prices['coreExtended']['normal'], rareWeight[c.rarity])
            Slots['collectorFoilRM'].add_card(c.prices['coreExtended']['foil'], rareWeight[c.rarity])
        if "commanderExtended" in c.styles:
            Slots['extendedCommander'].add_card(c.prices['commanderExtended']['normal'], rareWeight[c.rarity])
            Slots['collectorFoilRM'].add_card(c.prices['commanderExtended']['foil'], rareWeight[c.rarity])
        if "boxTopper" in c.styles:
            Slots['boxTopper'].add_card(c.prices['boxTopper']['foil'])
    cq.close()
    del(cq)

    with open("json/AllSetFiles/SNC.json", "rb") as f2:
        data = ijson.kvitems(f2, 'data.booster.default.sheets.foil.cards')
        dq = tqdm(data)
        dq.set_description("Loading foil rates")
        for uuid, weight in dq:
            for c in Cards.values():
                for s, u in c.styles.items():
                    if u == uuid:
                        cstyles = set(c.styles) & showcaseStyles
                        for s in cstyles:
                            Slots['rawFoil'].add_card(c.prices[s]['foil'], weight * 0.33/len(s))
                        try:
                            Slots["rawFoil"].add_card(c.prices["baseline"]['foil'], weight * (1 if len(cstyles) == 0 else 0.67))
                        except:
                            Slots["rawFoil"].add_card(c.prices[s]['foil'], weight * (1 if len(cstyles) == 0 else 0.67))
        dq.close()
        del(dq)

    Slots['art'].add_card(0.05, 0.95)
    Slots['art'].add_card(0.5, 0.05)

    Slots['theList'].add_card(0, 0.75)
    Slots['theList'].add_set(Slots['theListRaw'], weight=0.25, norm=True)

    Slots["foil"] = sealed.kit()
    Slots["foil"].add_set(Slots["common"], weight=0.67, norm=True)
    Slots["foil"].add_set(Slots["rawFoil"], weight=0.33, norm=True)
    
    Slots['fLand'] = sealed.kit()
    Slots['fLand'].add_set(Slots['land'], weight=0.79, norm=True)
    Slots['fLand'].add_set(Slots['foilLand'], weight=0.21, norm=True)
    
    Slots['setFoil'].add_set(Slots['rawFoil'], weight=0.96, norm=True)
    Slots['setFoil'].add_set(Slots['gildedFoils'], weight=0.04, norm=True)

    strixprob = [0.7  , 0.175, 0.125]
    Slots["wildcard"] = sealed.kit()
    Slots["wildcard"].add_set(Slots['common'], weight=strixprob[0], norm=True)
    Slots["wildcard"].add_set(Slots['uncommon'], weight=strixprob[1], norm=True)
    Slots["wildcard"].add_set(Slots['rareMythicWC'], weight=strixprob[2], norm=True)

    for slot, data in Slots.items():
        data.normalize()
        #print(slot, data.summary())
    
    return Slots


def main(priceJson = None):
    if priceJson is None:
        priceJson = sealed.get_price_data("json/AllPrices.json")
    Cards = get_card_list(priceJson)
    Slots = build_slots(Cards)
    draft_booster_contents = ((["common"] * 9) + (["uncommon"] * 3) + 
        ["land", "rareMythic", "foil"]
    )
    set_booster_contents = (['common', 'uncommon'] * 3 +
        ['showcaseCU', 'fLand', 'wildcard', 'wildcard', 'rareMythic', 'setFoil']
    )
    collector_booster_contents = (['foilCommon'] * 4 + ['foilUncommon', 'showcaseCU'] * 2 + 
        ['foilMetroLand', 'foilRareMythic', 'extendedCore', 'extendedCommander',
         'showcaseRM', 'collectorFoilSCU', 'collectorFoilRM']
    )
    draft_booster, draft_booster_box = sealed.build_booster(Slots, draft_booster_contents, 36, "draft", topper=Slots['boxTopper'])
    set_booster, set_booster_box = sealed.build_booster(Slots, set_booster_contents, 30, "set", topper=Slots['boxTopper'])
    collector_booster, collector_booster_box = sealed.build_booster(Slots, collector_booster_contents, 12, "col", topper=Slots['boxTopper'])
    summary = {}
    summary['category'] = 'expansion'
    summary['release'] = datetime.date(2022, 4, 29)
    summary["sealed"] = {"draft": {}, "set": {}, "collector": {}}
    summary["sealed"]["draft"]["booster"] = draft_booster.summary()
    summary["sealed"]['draft']['box'] = draft_booster_box.summary()
    summary["sealed"]['set']['booster'] = set_booster.summary()
    summary["sealed"]['set']['box'] = set_booster_box.summary()
    summary["sealed"]['collector']['booster'] = collector_booster.summary()
    summary["sealed"]['collector']['box'] = collector_booster_box.summary()
    summary['set'] = {}
    summary['set']['common'] = Slots['common'].summary()
    summary['set']['uncommon'] = Slots['uncommon'].summary()
    summary['set']['rareMythic'] = Slots['rareMythic'].summary()
    summary['set']['showcase'] = Slots['showcase'].summary()
    return summary

