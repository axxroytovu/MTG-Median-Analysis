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

    with open("json/2x2.json", 'rb') as f:
        data = ijson.items(f, 'data.cards.item')
        dq = tqdm(data)
        dq.set_description("Reading set cards")
        for card in dq:
            try:
                i = int(card['number'])
            except:
                print(card['name'], card['number'])
                continue
            name = card['name']
            if name not in Cards:
                Cards.update({name: sealed.card(card)})
            if i == 332:
                Cards[name].add_style(card, "spires")
            elif i >= 333 and i < 413:
                Cards[name].add_style(card, "borderless")
            elif i >= 413 and i < 563:
                Cards[name].add_style(card, "etchedFoil")
            elif i >= 563 and i < 578:
                Cards[name].add_style(card, "texturedFoil")
            elif i >= 578:
                Cards[name].add_style(card, "promo")
            else:
                Cards[name].add_style(card, "baseline")
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
    Slots['rareMythic'] = sealed.kit()
    Slots['foil'] = sealed.kit()
    Slots['foilCommon'] = sealed.kit()
    Slots['foilUncommon'] = sealed.kit()
    Slots['borderlessCU'] = sealed.kit()
    Slots['foilBorderlessCU'] = sealed.kit()
    Slots['foilRareMythic'] = sealed.kit()
    Slots['borderlessRM'] = sealed.kit()
    Slots['etchedRM'] = sealed.kit()
    Slots['foilBorderlessRM'] = sealed.kit()
    Slots['allBorderless'] = sealed.kit()
    Slots['crypticSpires'] = sealed.kit()

    cq = tqdm(Cards.values())
    cq.set_description("Assigning slots")
    for c in cq:
        if 'spires' in c.styles:
            Slots['crypticSpires'].add_card(c.prices['spires']['normal'])
        if 'baseline' in c.styles:
            if c.rarity == 'common':
                if 'borderless' in c.styles:
                    Slots['common'].add_card(c.prices['baseline']['normal'], 0.67)
                    Slots['common'].add_card(c.prices['borderless']['normal'], 0.33)
                else:
                    Slots['common'].add_card(c.prices['baseline']['normal'])
                Slots['foilCommon'].add_card(c.prices['baseline']['foil'])
            elif c.rarity == 'uncommon':
                if 'borderless' in c.styles:
                    Slots['uncommon'].add_card(c.prices['baseline']['normal'], 0.67)
                    Slots['uncommon'].add_card(c.prices['borderless']['normal'], 0.33)
                else:
                    Slots['uncommon'].add_card(c.prices['baseline']['normal'])
                Slots['foilUncommon'].add_card(c.prices['baseline']['foil'])
            elif c.rarity == 'rare':
                if 'borderless' in c.styles:
                    Slots['rareMythic'].add_card(c.prices['baseline']['normal'], 1.33)
                    Slots['rareMythic'].add_card(c.prices['borderless']['normal'], 0.67)
                else:
                    Slots['rareMythic'].add_card(c.prices['baseline']['normal'], 2)
                Slots['foilRareMythic'].add_card(c.prices['baseline']['foil'], 2)
            elif c.rarity == 'mythic':
                if 'borderless' in c.styles:
                    Slots['rareMythic'].add_card(c.prices['baseline']['normal'], 0.67)
                    Slots['rareMythic'].add_card(c.prices['borderless']['normal'], 0.33)
                else:
                    Slots['rareMythic'].add_card(c.prices['baseline']['normal'])
                Slots['foilRareMythic'].add_card(c.prices['baseline']['foil'])
        if 'borderless' in c.styles:
            if c.rarity == 'common':
                Slots['borderlessCU'].add_card(c.prices['borderless']['normal'])
                Slots['foilBorderlessCU'].add_card(c.prices['borderless']['foil'])
                Slots['allBorderless'].add_card(c.prices['borderless']['normal'], 8)
            elif c.rarity == 'uncommon':
                Slots['borderlessCU'].add_card(c.prices['borderless']['normal'])
                Slots['foilBorderlessCU'].add_card(c.prices['borderless']['foil'])
                Slots['allBorderless'].add_card(c.prices['borderless']['normal'], 4)
            elif c.rarity == 'rare':
                Slots['borderlessRM'].add_card(c.prices['borderless']['normal'], 2)
                Slots['foilBorderlessRM'].add_card(c.prices['borderless']['foil'], 2)
                Slots['allBorderless'].add_card(c.prices['borderless']['normal'], 2)
            elif c.rarity == 'mythic':
                Slots['borderlessRM'].add_card(c.prices['borderless']['normal'])
                Slots['foilBorderlessRM'].add_card(c.prices['borderless']['foil'])
                Slots['allBorderless'].add_card(c.prices['borderless']['normal'])
                if 'texturedFoil' in c.styles:
                    Slots['foilBorderlessRM'].add_card(c.prices['texturedFoil']['foil'], 0.5)
        if 'etchedFoil' in c.styles:
            if c.rarity == 'rare':
                Slots['etchedRM'].add_card(c.prices['etchedFoil']['foil'], 2)
            else:
                Slots['etchedRM'].add_card(c.prices['etchedFoil']['foil'])
    cq.close()
    del(cq)

    with open("json/2x2.json", 'r') as f:
        data = ijson.kvitems(f, 'data.booster.default.sheets.dedicatedFoilDoubleMasters.cards')
        dq = tqdm(data)
        dq.set_description("Loading foil weights")
        for uuid, weight in dq:
            for c in Cards.values():
                for s, u in c.styles.items():
                    if u == uuid:
                        if "borderless" in c.styles:
                            Slots["foil"].add_card(c.prices["borderless"]['foil'], weight/3.0)
                            Slots["foil"].add_card(c.prices["baseline"]['foil'], weight * 2.0/3)
                        else:
                            Slots["foil"].add_card(c.prices["baseline"]['foil'], weight)
        dq.close()
        del(dq)

    for k, s in Slots.items():
        s.normalize()

    return Slots


def main(priceJson = None):
    if priceJson is None:
        priceJson = sealed.get_price_data("json/AllPrices.json")
    Cards = get_card_list(priceJson)
    Slots = build_slots(Cards)
    draft_booster_contents = (["common"] * 8 + ["uncommon"] * 3 + 
        ["rareMythic", "foil"] * 2 + ['crypticSpires']
    )
    collector_booster_contents = (['foilCommon'] * 5 + 
        ['foilUncommon', 'borderlessCU', 'foilBorderlessCU'] * 2 +
        ['foilRareMythic', 'borderlessRM', 'etchedRM', 'foilBorderlessRM']
    )
    draft_booster, draft_booster_box = sealed.build_booster(Slots, draft_booster_contents, 24, "draft")
    collector_booster, collector_booster_box = sealed.build_booster(Slots, collector_booster_contents, 4, "col")
    summary = {}
    summary['category'] = 'reprint'
    summary['release'] = datetime.date(2022, 7, 8)
    summary["sealed"] = {"draft": {}, "collector": {}}
    summary["sealed"]["draft"]["booster"] = draft_booster.summary()
    summary["sealed"]['draft']['box'] = draft_booster_box.summary()
    summary["sealed"]['collector']['booster'] = collector_booster.summary()
    summary["sealed"]['collector']['box'] = collector_booster_box.summary()
    summary['set'] = {}
    summary['set']['common'] = Slots['common'].summary()
    summary['set']['uncommon'] = Slots['uncommon'].summary()
    summary['set']['rareMythic'] = Slots['rareMythic'].summary()
    summary['set']['showcase'] = Slots['allBorderless'].summary()
    return summary