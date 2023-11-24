import matplotlib.pyplot as plt
import sealed as s_func
import time
import tracemalloc
import booster_factory as b_f
import deck_factory as d_f
#from glob import glob
from pathlib import Path
from tqdm import tqdm
import ijson
import json
import yaml
import os
import pickle
import logging
import logging.handlers as handlers

performance_meter = False
compile_ = False

logfile_name = "log.log"
logger = logging.getLogger()
logger.setLevel(logging.INFO)
rollCheck = os.path.isfile(logfile_name)
handler = handlers.RotatingFileHandler(logfile_name, backupCount=5, encoding="utf-8")
formatter = logging.Formatter("%(levelname)s - %(message)s")

handler.setFormatter(formatter)
handler.setLevel(logging.INFO)
logger.addHandler(handler)

if rollCheck:
    logger.handlers[0].doRollover()

logger.info("Starting Run")

if performance_meter:
    tracemalloc.start()
    start_time = time.time()

def getVal(dictionary, all_keys):
    v = dictionary[all_keys[0]]
    if isinstance(v, dict):
        return getVal(v, all_keys[1:])
    else:
        return v

def checkVal(dictionary, all_keys):
    if len(all_keys) == 1:
        return True
    v = dictionary[all_keys[0]]
    if isinstance(v, dict) and (all_keys[1] in v):
        return checkVal(v, all_keys[1:])
    return False

def create_boxplots(seal, typ, filt=False, sort=False, norm=True, yscale="log"):
    u = [(scode, sval) for scode, sval in seal.items() if checkVal(sval, typ)]
    if filt:
        u = filter(lambda x: x[1][filt[0]] == filt[1], u)
    if sort:
        u = sorted(u, key=lambda x: x[1][sort])
    if norm:
        w = [getVal(val[1], ["prices"] + typ[1:]) for val in u]
    else:
        w = [1 for _ in u]
    boxes = [
        {
            'label': " ".join([scode] + typ),
            'whislo': getVal(sval, typ)[1] / weight,
            'q1': getVal(sval, typ)[2] / weight,
            'med': getVal(sval, typ)[3] / weight,
            'q3': getVal(sval, typ)[4] / weight,
            'whishi': getVal(sval, typ)[5] / weight,
            'fliers': [getVal(sval, typ)[0] / weight]
        } for (scode, sval), weight in zip(u, w)]

    fig, ax = plt.subplots()
    ax.bxp(boxes, showfliers=True)
    plt.xticks(rotation=45)
    plt.yscale(yscale)
    plt.xlabel('Set')
    if norm:
        plt.ylabel('Relative Value [roi]')
    else:
        plt.ylabel('Value [$]')
    plt.grid()
    plt.tight_layout()

def build_product(contents, boosters, decks, sealed, cards, logger):
    ready = True
    pack = s_func.kit()
    if isinstance(contents, list):
      return pack
    for k in contents.keys():
        if k not in ["deck", "pack", "sealed", "variable", "other", "card", "card_count"]:
            logger.error("Invalid product definition: {0}\n".format(k))
            return pack
    for d in contents.get("deck", []):
        for i in range(d.get("count", 1)):
            try:
                pack.merge_kit(decks[d["set"].upper()][d["name"]])
            except KeyError:
                logger.warning("Invalid deck identifier {0}/{1}\n".format(d["set"], d["name"]))
    for p in contents.get("pack", []):
        for i in range(p.get("count", 1)):
            try:
                pack.merge_kit(boosters[p["set"].upper()][p["code"]])
            except KeyError:
                logger.warning("Invalid pack identifier {0}/{1}\n".format(p["set"], p["code"]))
    for s in contents.get("sealed", []):
        if 'uuid' not in s:
            logger.warning("Invalid sealed object identifier {0}/{1}\n".format(s["set"], s["name"]))
            continue
        if s["uuid"] not in sealed:
            ready = False
            break
        for i in range(s.get("count", 1)):
            pack.merge_kit(sealed[s["uuid"]])
    for c in contents.get("card", []):
        cpack = s_func.kit()
        foiling = "foil" if c.get("foil", False) else "normal"
        try:
            cpack.add_card(cards.get(c["uuid"], {}).get(foiling, 0))
        except KeyError:
            logger.warning("Card {0}/{1} missing uuid\n".format(c["set"], c["name"]))
        pack.merge_kit(cpack)
    p2 = s_func.kit()
    for version in contents.get("variable", []):
        pack = build_product(version, boosters, decks, sealed, cards, logger)
        if pack:
            p2.add_set(pack, version.get("count", 1))
        else:
            ready = False
            break
    p2.normalize()
    pack.merge_kit(p2)
    pack.normalize()
    if ready:
        return pack
    else:
        return False

if compile_:
    priceJson = s_func.get_price_data("mtgJson/AllPrices.json")

    with open("mtgJson/AllPrintings.json", 'rb') as allPrintings:
        printData = json.load(allPrintings)

    for set_name in tqdm(list(printData["data"].keys()), desc="Updating Prices", position=0):
        for card in tqdm(printData["data"][set_name]["cards"], desc=set_name, position=1, leave=False):
            if card["uuid"] in priceJson:
                test = True
                if card["hasFoil"] and ('foil' not in priceJson[card["uuid"]]):
                    test = False
                if card["hasNonFoil"] and ('normal' not in priceJson[card["uuid"]]):
                    test = False
                if test:
                    continue
            else:
                priceJson[card["uuid"]] = {}
            if card.get("variations", False):
                try:
                    if card["hasNonFoil"] and ('normal' not in priceJson[card["uuid"]]):
                        priceJson[card["uuid"]]['normal'] = min(priceJson[v]['normal'] for v in card["variations"] if 'normal' in priceJson.get(v, {}))
                    if card["hasFoil"] and ('foil' not in priceJson[card["uuid"]]):
                        priceJson[card["uuid"]]['foil'] = min(priceJson[v]['foil'] for v in card["variations"] if 'foil' in priceJson.get(v, {}))
                    continue
                except ValueError:
                    pass
            if card["hasNonFoil"] and ('normal' not in priceJson[card["uuid"]]):
                nonfoil = []
                for set_code in card["printings"]:
                    for check_card in tqdm(printData["data"][set_code]["cards"], desc="comparing "+set_code, position=2, leave=False):
                        if check_card["name"] == card["name"]:
                            if 'normal' in priceJson.get(check_card["uuid"], {}):
                                nonfoil.append(priceJson[check_card["uuid"]]['normal'])
                priceJson[card["uuid"]]['normal'] = min(nonfoil, default=0)
            if card["hasFoil"] and ('foil' not in priceJson[card["uuid"]]):
                foil = []
                for set_code in card["printings"]:
                    for check_card in tqdm(printData["data"][set_code]["cards"], desc="comparing "+set_code, position=2, leave=False):
                        if check_card["name"] == card["name"]:
                            if 'foil' in priceJson.get(check_card["uuid"], {}):
                                foil.append(priceJson[check_card["uuid"]]['foil'])
                priceJson[card["uuid"]]['foil'] = min(foil, default=0)

    boosters = {}
    decks = {}
    sealed = {}
    products = []

    for set_name, contents in tqdm(list(printData["data"].items()), desc="Sets", position=0):
        # Build packs
        if "booster" in contents:
            boosters[set_name] = {}
            for typeCode, boosterPack in tqdm(contents["booster"].items(), desc=f"Boosters {set_name}", position=1, leave=False):
                if "arena" in typeCode:
                    continue
                boosters[set_name][typeCode] = b_f.build_booster(boosterPack, priceJson, logger)
        if "decks" in contents:
            decks[set_name] = {}
            for deck in tqdm(contents["decks"], desc=f"Decks {set_name}", position=1, leave=False):
                name = deck["name"]
                decks[set_name][name] = d_f.build_deck(deck, priceJson, logger)
        if "sealedProduct" in contents:
            cleanedProducts = [{**d, "set": set_name, "date":d.get("releaseDate", contents["releaseDate"])} for d in contents["sealedProduct"]]
            products.extend(cleanedProducts)

    # Build products
    for i in range(3):
        t = tqdm(products, desc=f"Sealed - pass {i+1}")
        for obj in t:
            if obj["uuid"] in sealed:
                continue
            if "contents" not in obj:
                sealed[obj["uuid"]] = s_func.kit()
                continue
            pack = build_product(obj["contents"], boosters, decks, sealed, priceJson, logger)
            if pack:
                sealed[obj["uuid"]] = pack
        t.close()
        del(t)

    if len(products) > len(sealed):
        print("Missing products:")
        for p in products:
            if p["uuid"] not in sealed:
                logger.info("Missing %s", p['name'])
                print(p["name"])

    conv = lambda i: i or ""
    sortfunc = lambda d: (conv(d.get("category")), conv(d.get("subtype")), conv(d["date"]))
    products.sort(key=sortfunc)

    with open("compiled_products.pkl", "wb") as ff:
        pickle.dump(products, ff)
    with open("compiled_sealed.pkl", "wb") as ff:
        pickle.dump(sealed, ff)
else:
    with open("compiled_products.pkl", "rb") as ff:
        products = pickle.load(ff)
    with open("compiled_sealed.pkl", "rb") as ff:
        sealed = pickle.load(ff)

print("products")
category = ""
subtype = ""
set_code = ""
for p in products:
    try:
        if sealed[p["uuid"]].mean == 0:
            continue
    except KeyError:
        continue
    if p.get("category") != category:
        category = p.get("category")
        subtype = ""
        set_code = ""
        print(category)
    if p.get("subtype") != subtype:
        subtype = p.get("subtype")
        set_code = ""
        print("  ", subtype)
    if p.get("set") != set_code:
        set_code = p.get("set")
        print("    ", set_code)
    print("      ", p["name"])
    print("        ", sealed[p["uuid"]].summary())

logger.info("Finished")
if performance_meter:
    print("memory:", tracemalloc.get_traced_memory())
    print("duration:", time.time() - start_time)

#plt.show()