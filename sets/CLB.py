# baludrs gate analysis

import numpy as np
import ijson
import sealed
import pandas as pd
import matplotlib.pyplot as plt
from tqdm import tqdm
import datetime

def get_card_list(Json_Data):
# Sheet method
    Cards = {}

    with open("json/AllSetFiles/CLB.json", 'rb') as f:
        data = ijson.items(f, 'data.cards.item')
        dq = tqdm(data)
        dq.set_description("Reading set cards")
        for card in dq:
            try:
                i = int(card['number'])
            except:
                print(card['name'], card['numbers'])
                continue
            name = card['name']
            #print(name)
            if name not in Cards:
                Cards.update({name: sealed.card(card)})
            if i < 362:
                Cards[name].add_style(card, "all")
                if "Legendary" in card['supertypes']:
                    if "Background" in card['subtypes']:
                        Cards[name].add_style(card, "background")
                    else:
                        Cards[name].add_style(card, "commander")
                    if card['rarity'] in ['common', 'uncommon']:
                        Cards[name].add_style(card, 'baseline')
                else:
                    Cards[name].add_style(card, "baseline")
            elif i >= 362 and i < 375:
                Cards[name].add_style(card, 'borderless')
            elif i >= 375 and i < 451:
                Cards[name].add_style(card, 'showcase')
            elif i >= 451 and i < 471:
                Cards[name].add_style(card, 'basic_land', unique=True)
            elif i >= 471 and i < 553:
                Cards[name].add_style(card, 'etched')
            elif i >= 553 and i < 607:
                Cards[name].add_style(card, 'coreextended')
            elif i >= 607 and i < 646:
                Cards[name].add_style(card, 'deckextended')
            elif i >= 646 and i < 686:
                Cards[name].add_style(card, 'newCommander')
            elif i >= 686 and i < 931:
                Cards[name].add_style(card, 'reprintCommander')
            elif i >= 931 and i < 935:
                Cards[name].add_style(card, 'thickcards')
            else:
                Cards[name].add_style(card, 'promo')
        dq.close()
        del(dq)

    TheList = pd.read_csv("json/TheList.csv")

    with open("json/AllSetFiles/PLIST.json", 'rb') as f3:
        data = ijson.items(f3, 'data.cards.item')
        validNames = TheList[TheList['CLB List']==1.0]["Name"].values
        dq = tqdm(data)
        dq.set_description("Reading the list")
        for card in dq:
            name = card['name']
            if name in validNames:
                if name not in Cards:
                    Cards.update({name: sealed.card(card)})
                Cards[name].add_style(card, "theList")
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
    Slots['common'] = sealed.kit()
    Slots['uncommon'] = sealed.kit()
    Slots['background'] = sealed.kit()
    Slots['commander'] = sealed.kit()
    Slots['rareMythic'] = sealed.kit()
    Slots['showcaseCU'] = sealed.kit()
    Slots['anyLegendary'] = sealed.kit()
    Slots['etched'] = sealed.kit()
    Slots['art'] = sealed.kit()
    Slots['basicLand'] = sealed.kit()
    Slots['setLand'] = sealed.kit()
    Slots['foilLand'] = sealed.kit()
    Slots['foilCommon'] = sealed.kit()
    Slots['foilUncommon'] = sealed.kit()
    Slots['foilShowcaseCU'] = sealed.kit()
    Slots['foilLegendaryCU'] = sealed.kit()
    Slots['foilRM'] = sealed.kit()
    Slots['coreExtended'] = sealed.kit()
    Slots['deckExtended'] = sealed.kit()
    Slots['showcaseRM'] = sealed.kit()
    Slots['etchedRM'] = sealed.kit()
    Slots['etchedCU'] = sealed.kit()
    Slots['rawList'] = sealed.kit()
    Slots['allShowcase'] = sealed.kit()

    Slots['art'].add_card(0.05, 0.95)
    Slots['art'].add_card(0.5, 0.05)

    cq = tqdm(Cards.values())
    cq.set_description("Assigning slots")
    for c in cq:
        if "baseline" in c.styles:
            if c.rarity == 'common':
                if "showase" in c.styles:
                    Slots['common'].add_card(c.prices['baseline']['normal'], 0.67)
                    Slots['common'].add_card(c.prices['showcase']['normal'], 0.33)
                    Slots['foilCommon'].add_card(c.prices['baseline']['foil'], 0.67)
                    Slots['foilCommon'].add_card(c.prices['showcase']['foil'], 0.33)
                else:
                    Slots['common'].add_card(c.prices['baseline']['normal'])
                    Slots['foilCommon'].add_card(c.prices['baseline']['foil'])
            elif c.rarity == 'uncommon':
                if "showcase" in c.styles:
                    Slots['uncommon'].add_card(c.prices['baseline']['normal'], 0.67)
                    Slots['uncommon'].add_card(c.prices['showcase']['normal'], 0.33)
                    Slots['foilUncommon'].add_card(c.prices['baseline']['foil'], 0.67)
                    Slots['foilUncommon'].add_card(c.prices['showcase']['foil'], 0.33)
                else:
                    Slots['uncommon'].add_card(c.prices['baseline']['normal'])
                    Slots['foilUncommon'].add_card(c.prices['baseline']['foil'])
            elif c.rarity == 'rare':
                if "showcase" in c.styles:
                    Slots['rareMythic'].add_card(c.prices['baseline']['normal'], 1.33)
                    Slots['rareMythic'].add_card(c.prices['showcase']['normal'], 0.67)
                    Slots['foilRM'].add_card(c.prices['baseline']['foil'], 1.33)
                    Slots['foilRM'].add_card(c.prices['showcase']['foil'], 0.67)
                else:
                    Slots['rareMythic'].add_card(c.prices['baseline']['normal'], 2)
                    Slots['foilRM'].add_card(c.prices['baseline']['foil'], 2)
            elif c.rarity == 'mythic':
                if "showcase" in c.styles and "borderless" in c.styles:
                    Slots['rareMythic'].add_card(c.prices['baseline']['normal'], 0.66)
                    Slots['rareMythic'].add_card(c.prices['showcase']['normal'], 0.17)
                    Slots['rareMythic'].add_card(c.prices['borderless']['normal'], 0.17)
                    Slots['foilRM'].add_card(c.prices['baseline']['foil'], 0.66)
                    Slots['foilRM'].add_card(c.prices['showcase']['foil'], 0.17)
                    Slots['foilRM'].add_card(c.prices['borderless']['foil'], 0.17)
                elif "showcase" in c.styles:
                    Slots['rareMythic'].add_card(c.prices['baseline']['normal'], 0.67)
                    Slots['rareMythic'].add_card(c.prices['showcase']['normal'], 0.33)
                    Slots['foilRM'].add_card(c.prices['baseline']['foil'], 0.67)
                    Slots['foilRM'].add_card(c.prices['showcase']['foil'], 0.33)
                elif "borderless" in c.styles:
                    Slots['rareMythic'].add_card(c.prices['baseline']['normal'], 0.67)
                    Slots['rareMythic'].add_card(c.prices['borderless']['normal'], 0.33)
                    Slots['foilRM'].add_card(c.prices['baseline']['foil'], 0.67)
                    Slots['foilRM'].add_card(c.prices['borderless']['foil'], 0.33)
                else:
                    Slots['rareMythic'].add_card(c.prices['baseline']['normal'])
                    Slots['foilRM'].add_card(c.prices['baseline']['foil'])
        if "background" in c.styles:
            if c.rarity == 'common':
                Slots['background'].add_card(c.prices['background']['normal'], 4)
                Slots['foilLegendaryCU'].add_card(c.prices['background']['foil'], 2)
            elif c.rarity == 'uncommon':
                Slots['background'].add_card(c.prices['background']['normal'], 2)
                Slots['anyLegendary'].add_card(c.prices['background']['normal'], 4)
                Slots['foilLegendaryCU'].add_card(c.prices['background']['foil'])
            elif c.rarity == 'rare':
                Slots['background'].add_card(c.prices['background']['normal'])
                Slots['anyLegendary'].add_card(c.prices['background']['normal'], 2)
        if "commander" in c.styles:
            if c.rarity == 'uncommon':
                Slots['commander'].add_card(c.prices['commander']['normal'], 4)
                Slots['anyLegendary'].add_card(c.prices['commander']['normal'], 4)
            elif c.rarity == 'rare':
                Slots['commander'].add_card(c.prices['commander']['normal'], 2)
                Slots['anyLegendary'].add_card(c.prices['commander']['normal'], 2)
            elif c.rarity == 'mythic':
                Slots['commander'].add_card(c.prices['commander']['normal'])
                Slots['anyLegendary'].add_card(c.prices['commander']['normal'])
        if "showcase" in c.styles:
            if c.rarity == 'common':
                Slots['showcaseCU'].add_card(c.prices['showcase']['normal'], 2)
                Slots['foilShowcaseCU'].add_card(c.prices['showcase']['foil'], 2)
            elif c.rarity == 'uncommon':
                Slots['showcaseCU'].add_card(c.prices['showcase']['normal'])
                Slots['foilShowcaseCU'].add_card(c.prices['showcase']['foil'])
            elif c.rarity == 'rare':
                Slots['showcaseRM'].add_card(c.prices['showcase']['normal'], 2)
            elif c.rarity == 'mythic':
                if "borderless" in c.styles:
                    Slots['showcaseRM'].add_card(c.prices['showcase']['normal'], 0.5)
                    Slots['showcaseRM'].add_card(c.prices['borderless']['normal'], 0.5)
                else:
                    Slots['showcaseRM'].add_card(c.prices['showcase']['normal'])
        if "etched" in c.styles:
            if c.rarity == 'common':
                Slots['etchedCU'].add_card(c.prices['etched']['foil'], 2)
                Slots['etched'].add_card(c.prices['etched']['foil'], 8)
            elif c.rarity == 'uncommon':
                Slots['etchedCU'].add_card(c.prices['etched']['foil'])
                Slots['etched'].add_card(c.prices['etched']['foil'], 4)
            elif c.rarity == 'rare':
                Slots['etchedRM'].add_card(c.prices['etched']['foil'], 2)
                Slots['etched'].add_card(c.prices['etched']['foil'], 2)
            elif c.rarity == 'mythic':
                Slots['etchedRM'].add_card(c.prices['etched']['foil'])
                Slots['etched'].add_card(c.prices['etched']['foil'])
        if "basic_land0" in c.styles:
            for s in c.styles:
                Slots['basicLand'].add_card(c.prices[s]['normal'])
                Slots['foilLand'].add_card(c.prices[s]['foil'])
        if "coreextended" in c.styles:
            if c.rarity == 'rare':
                Slots['coreExtended'].add_card(c.prices['coreextended']['normal'], 2)
            elif c.rarity == 'mythic':
                Slots['coreExtended'].add_card(c.prices['coreextended']['normal'])
        if "deckextended" in c.styles:
            if c.rarity == "rare":
                Slots['deckExtended'].add_card(c.prices['deckextended']['normal'], 2)
            elif c.rarity == 'mythic':
                Slots['deckExtended'].add_card(c.prices['deckextended']['normal'])
        if "theList" in c.styles:
            Slots['rawList'].add_card(c.prices['theList']['normal'])
    cq.close()
    del(cq)

    Slots['allShowcase'].add_set(Slots['showcaseCU'], 0.75, norm=True)
    Slots['allShowcase'].add_set(Slots['showcaseRM'], 0.25, norm=True)
    
    Slots['foil'] = sealed.kit()

    with open("json/AllSetFiles/CLB.json", 'r') as f:
        data = ijson.kvitems(f, 'data.booster.default.sheets.dedicatedFoil.cards')
        dq = tqdm(data)
        dq.set_description("Loading foil rates")
        for uuid, weight in dq:
            for c in Cards.values():
                for s, u in c.styles.items():
                    if u == uuid:
                        if "showcase" in c.styles and "borderless" in c.styles:
                            Slots['foil'].add_card(c.prices['all']['foil'], weight*0.66)
                            Slots['foil'].add_card(c.prices['showcase']['foil'], weight*0.17)
                            Slots['foil'].add_card(c.prices['borderless']['foil'], weight*0.17)
                        elif "showcase" in c.styles:
                            Slots['foil'].add_card(c.prices['all']['foil'], weight*0.67)
                            Slots['foil'].add_card(c.prices['showcase']['foil'], weight*0.33)
                        elif "borderless" in c.styles:
                            Slots['foil'].add_card(c.prices['all']['foil'], weight*0.67)
                            Slots['foil'].add_card(c.prices['borderless']['foil'], weight*0.33)
                        else:
                            Slots['foil'].add_card(c.prices['all']['normal'], weight)
        dq.close()
        del(dq)

    Slots['theList'] = sealed.kit()
    Slots['theList'].add_card(0, 0.75)
    Slots['theList'].add_set(Slots['rawList'], weight=0.25, norm=True)

    Slots["wildcard"] = sealed.kit()
    Slots["wildcard"].add_set(Slots['common'], weight=0.7, norm=True)
    Slots["wildcard"].add_set(Slots['uncommon'], weight=0.175, norm=True)
    Slots["wildcard"].add_set(Slots['rareMythic'], weight=0.125, norm=True)

    Slots["setLand"].add_set(Slots['basicLand'], 0.8)
    Slots['setLand'].add_set(Slots['foilLand'], 0.2)

    for slot, data in Slots.items():
        data.normalize()
    return Slots

def main(priceJson = None):
    if priceJson is None:
        priceJson = sealed.get_price_data("json/AllPrices.json")
    Cards = get_card_list(priceJson)
    Slots = build_slots(Cards)
    draft_booster_contents = ((["common"] * 13) + (["uncommon"] * 3) + 
        ["background", "commander", "rareMythic", "foil"]
    )
    set_booster_contents = ((["common"] * 3) + (["uncommon"] * 3) + (["wildcard"] * 2) +
        ['art', 'setLand', 'showcaseCU', 'background', 'anyLegendary', 
         'rareMythic', 'foil', 'etched', 'theList']
    )
    collector_booster_contents = ((['foilCommon'] * 3) + (['foilUncommon'] * 2) + 
        ['foilLand', 'foilShowcaseCU', 'foilLegendaryCU', 'foilRM', 'coreExtended',
         'deckExtended', 'showcaseRM', 'etchedCU', 'etchedRM']
    )
    draft_booster, draft_booster_box = sealed.build_booster(Slots, draft_booster_contents, 24, "draft")
    set_booster, set_booster_box = sealed.build_booster(Slots, set_booster_contents, 18, "set")
    collector_booster, collector_booster_box = sealed.build_booster(Slots, collector_booster_contents, 12, "col")
    summary = {}
    summary['category'] = 'supplement'
    summary['release'] = datetime.date(2022, 6, 10)
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
    summary['set']['showcase'] = Slots['allShowcase'].summary()
    return summary
