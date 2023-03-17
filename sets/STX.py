# strixhaven analysis

import numpy as np
import ijson
import sealed
import pandas as pd
import matplotlib.pyplot as plt
from tqdm import tqdm
import datetime

def get_card_list(Json_Data):
    Cards = {}

    with open("json/AllSetFiles/STX.json", "rb") as f2:
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
            if i in [1, 2, 3, 4, 5, 7, 25, 47, 57, 67, 78, 108, 114, 120, 125, 183, 187, 195, 211, 236]:
                Cards[name].add_style(card, "lesson")
            elif i >= 276 and i < 285:
                Cards[name].add_style(card, "borderless")
            elif i >= 285 and i < 366:
                Cards[name].add_style(card, "extended")
            elif i >= 366 and i < 376:
                if i%2:
                    Cards[name].add_style(card, "basicLand") 
                else:
                    Cards[name].add_style(card, "basicLand2") 
            elif i >= 376:
                Cards[name].add_style(card, "promo")
            else:
                Cards[name].add_style(card, "baseline")
        dq.close()
        del(dq)

    with open("json/AllSetFiles/STA.json", "rb") as f2:
        data = ijson.items(f2, 'data.cards.item')
        dq = tqdm(data)
        dq.set_description("Reading MA cards")
        for card in dq:
            try:
                i = int(card['number'])
            except:
                continue
            name = card['name']
            if name not in Cards:
                Cards.update({name: sealed.card(card)})
            if i < 64:
                Cards[name].add_style(card, "archive")
            else:
                Cards[name].add_style(card, "jpArchive")
        dq.close()
        del(dq)
        
    TheList = pd.read_csv("json/TheList.csv")

    with open("json/AllSetFiles/PLIST.json", 'rb') as f3:
        data = ijson.items(f3, 'data.cards.item')
        dq = tqdm(data)
        dq.set_description("Reading the list")
        validNames = TheList[TheList['STX List']==1.0]["Name"].values
        for card in dq:
            name = card['name']
            if name in validNames:
                if name not in Cards:
                    Cards.update({name: sealed.card(card)})
                Cards[name].add_style(card, "theList")
        dq.close()
        del(dq)

    with open("json/AllSetFiles/C21.json", 'rb') as f4:
        data = ijson.items(f4, 'data.cards.item')
        dq = tqdm(data)
        dq.set_description("Reading commander cards")
        for card in dq:
            if int(card['number']) >= 328 and int(card['number']) <= 407:
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
    Slots["common"] = sealed.kit()
    Slots["foilCommon"] = sealed.kit()
    Slots["uncommon"] = sealed.kit()
    Slots["foilUncommon"] = sealed.kit()
    Slots["rareMythic"] = sealed.kit()
    Slots["foilRareMythic"] = sealed.kit()
    Slots["archive"] = sealed.kit()
    Slots["foilArchiveU"] = sealed.kit()
    Slots['etchedArchiveU'] = sealed.kit()
    Slots['etchedArchiveRM'] = sealed.kit()
    Slots['collectorWildcard'] = sealed.kit()
    Slots["lesson"] = sealed.kit()
    Slots["foilLesson"] = sealed.kit()
    Slots["rawFoil"] = sealed.kit()
    Slots["foil"] = sealed.kit()
    Slots['art'] = sealed.kit()
    Slots['art'].add_card(0.05, 0.95)
    Slots['art'].add_card(0.5, 0.05)
    Slots['foilLand'] = sealed.kit()
    Slots['fLand'] = sealed.kit()
    Slots['theListRaw'] = sealed.kit()
    Slots['theList'] = sealed.kit()
    Slots['commanderExtended'] = sealed.kit()
    Slots['extendedBorderless'] = sealed.kit()

    cq = tqdm(Cards.values())
    cq.set_description("Assigning slots")
    for c in cq:
        if "baseline" in c.styles:
            if c.rarity == "common":
                Slots["foilCommon"].add_card(c.prices["baseline"]['foil'])
                if "borderless" in c.styles:
                    Slots["common"].add_card(c.prices["baseline"]['normal'], 0.67)
                    Slots["common"].add_card(c.prices["borderless"]['normal'], 0.33)
                else:
                    Slots["common"].add_card(c.prices["baseline"]['normal'])
            elif c.rarity == "uncommon":
                Slots['foilUncommon'].add_card(c.prices['baseline']['foil'])
                if "borderless" in c.styles:
                    Slots["uncommon"].add_card(c.prices["baseline"]['normal'], 0.67)
                    Slots["uncommon"].add_card(c.prices["borderless"]['normal'], 0.33)
                else:
                    Slots["uncommon"].add_card(c.prices["baseline"]['normal'])
            elif c.rarity == "rare":
                Slots['foilRareMythic'].add_card(c.prices["baseline"]['foil'], 2)
                if "borderless" in c.styles:
                    Slots["rareMythic"].add_card(c.prices["baseline"]['normal'], 1.33)
                    Slots["rareMythic"].add_card(c.prices["borderless"]['normal'], 0.67)
                else:
                    Slots["rareMythic"].add_card(c.prices["baseline"]['normal'], 2)
            elif c.rarity == "mythic":
                Slots['foilRareMythic'].add_card(c.prices["baseline"]['foil'])
                if "borderless" in c.styles:
                    Slots["rareMythic"].add_card(c.prices["baseline"]['normal'], 0.67)
                    Slots["rareMythic"].add_card(c.prices["borderless"]['normal'], 0.33)
                else:
                    Slots["rareMythic"].add_card(c.prices["baseline"]['normal'])
        if "archive" in c.styles:
            if c.rarity == "uncommon":
                Slots['foilArchiveU'].add_card(c.prices['archive']['foil'], 0.5)
                Slots['foilArchiveU'].add_card(c.prices['jpArchive']['foil'], 0.5)
                Slots['etchedArchiveU'].add_card(c.prices['archive']['foil'], 0.5)
                Slots['etchedArchiveU'].add_card(c.prices['jpArchive']['foil'], 0.5)
                weight = 25
            elif c.rarity == "rare":
                Slots['collectorWildcard'].add_card(c.prices['archive']['foil'])
                Slots['collectorWildcard'].add_card(c.prices['jpArchive']['foil'])
                Slots['etchedArchiveRM'].add_card(c.prices['archive']['foil'])
                Slots['etchedArchiveRM'].add_card(c.prices['jpArchive']['foil'])
                weight = 6
            elif c.rarity == "mythic":
                Slots['collectorWildcard'].add_card(c.prices['archive']['foil'], 0.5)
                Slots['collectorWildcard'].add_card(c.prices['jpArchive']['foil'], 0.5)
                Slots['etchedArchiveRM'].add_card(c.prices['archive']['foil'], 0.5)
                Slots['etchedArchiveRM'].add_card(c.prices['jpArchive']['foil'], 0.5)
                weight = 3
            Slots["archive"].add_card(c.prices["archive"]['normal'], weight)
        if "lesson" in c.styles:
            if c.rarity == "common":
                Slots["lesson"].add_card(c.prices["lesson"]['normal'], 11)
                Slots['foilLesson'].add_card(c.prices['lesson']['foil'], 11)
            elif c.rarity == "uncommon":
                Slots["uncommon"].add_card(c.prices["lesson"]['normal'])
                Slots['foilLesson'].add_card(c.prices['lesson']['foil'], 6)
            elif c.rarity == "rare":
                Slots["lesson"].add_card(c.prices["lesson"]['normal'], 2)
                Slots['foilLesson'].add_card(c.prices['lesson']['foil'], 2)
            elif c.rarity == "mythic":
                Slots["lesson"].add_card(c.prices["lesson"]['normal'], 1)
                Slots['foilLesson'].add_card(c.prices['lesson']['foil'], 1)
        if "basicLand" in c.styles:
            Slots["land"].add_card(c.prices["basicLand"]['normal'])
            Slots["foilLand"].add_card(c.prices["basicLand"]['foil'])
        if "basicLand2" in c.styles:
            Slots["land"].add_card(c.prices["basicLand2"]['normal'])
            Slots["foilLand"].add_card(c.prices["basicLand2"]['foil'])
        if "theList" in c.styles:
            Slots['theListRaw'].add_card(c.prices["theList"]['normal'])
        if "borderless" in c.styles:
            Slots['extendedBorderless'].add_card(c.prices['borderless']['normal'], 1+(c.rarity=='rare'))
            Slots['collectorWildcard'].add_card(c.prices['borderless']['foil'], 1+(c.rarity=='rare'))
        if "extended" in c.styles:
            Slots['extendedBorderless'].add_card(c.prices['extended']['normal'], 1+(c.rarity=='rare'))
            Slots['collectorWildcard'].add_card(c.prices['extended']['foil'], 1+(c.rarity=='rare'))
        if "commanderExtended" in c.styles:
            Slots['commanderExtended'].add_card(c.prices['commanderExtended']['normal'], 1+(c.rarity=='rare'))
    cq.close()
    del(cq)

    with open("json/AllSetFiles/STX.json", "rb") as f2:
        data = ijson.kvitems(f2, 'data.booster.default.sheets.foil.cards')
        dq = tqdm(data)
        dq.set_description("Loading foil rates")
        for uuid, weight in dq:
            for c in Cards.values():
                for s, u in c.styles.items():
                    if u == uuid:
                        if "lesson" in c.styles:
                            Slots["rawFoil"].add_card(c.prices['lesson']['foil'], weight)
                        elif "borderless" in c.styles:
                            Slots["rawFoil"].add_card(c.prices['borderless']['foil'], weight/3.0)
                            Slots["rawFoil"].add_card(c.prices['baseline']['foil'], weight * 2.0/3)
                        else:
                            Slots["rawFoil"].add_card(c.prices['baseline']['foil'], weight)
        dq.close()
        del(dq)

    Slots['theList'].add_card(0, 0.75)
    Slots['theList'].add_set(Slots['theListRaw'], weight=0.25, norm=True)

    Slots["foil"].add_set(Slots["common"], weight=0.67, norm=True)
    Slots["foil"].add_set(Slots["rawFoil"], weight=0.33, norm=True)

    Slots['fLand'].add_set(Slots['land'], weight=0.85, norm=True)
    Slots['fLand'].add_set(Slots['foilLand'], weight=0.15, norm=True)

    # Connected
    probs = [0, .35, .4, .125, .07, .035]
    cpr = np.cumsum(probs)
    for idx, p in enumerate(cpr):
        temp = sealed.kit()
        temp.add_set(Slots['common'], weight=p, norm=True)
        temp.add_set(Slots['uncommon'], weight=1-p, norm=True)
        Slots["setCommonUncommon"+str(idx)] = temp

    strixprob = [0.7  , 0.175, 0.125]
    Slots["wildcard"] = sealed.kit()
    Slots["wildcard"].add_set(Slots['common'], weight=strixprob[0], norm=True)
    Slots["wildcard"].add_set(Slots['uncommon'], weight=strixprob[1], norm=True)
    Slots["wildcard"].add_set(Slots['rareMythic'], weight=strixprob[2], norm=True)

    for slot, data in Slots.items():
        data.normalize()
    
    return Slots


def main(priceJson = None):
    if priceJson is None:
        priceJson = sealed.get_price_data("json/AllPrices.json")
    Cards = get_card_list(priceJson)
    Slots = build_slots(Cards)
    draft_booster_contents = ((["common"] * 8) + (["uncommon"] * 3) + 
        ["lesson", "land", "archive", "rareMythic", "foil"]
    )
    set_booster_contents = (["setCommonUncommon"+str(idx) for idx in range(6)] +
        ['art', 'fLand', 'wildcard', 'rawFoil', 'rareMythic', 
         'archive', 'lesson', 'theList']
    )
    collector_booster_contents = ((['foilCommon'] * 5) + (['foilUncommon'] * 2) + 
        ['foilLand', 'foilRareMythic', 'foilLesson', 'commanderExtended',
         'extendedBorderless', 'foilArchiveU', 'collectorWildcard', 'etchedArchiveU',
         'etchedArchiveRM']
    )
    draft_booster, draft_booster_box = sealed.build_booster(Slots, draft_booster_contents, 36, "draft")
    set_booster, set_booster_box = sealed.build_booster(Slots, set_booster_contents, 30, "set")
    collector_booster, collector_booster_box = sealed.build_booster(Slots, collector_booster_contents, 12, "col")
    summary = {}
    summary['category'] = 'expansion'
    summary['release'] = datetime.date(2021, 4, 23)
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
    summary['set']['showcase'] = Slots['archive'].summary()
    return summary
