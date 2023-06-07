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

performance_meter = False

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

def build_product(contents, boosters, decks, sealed, cards):
    ready = True
    pack = s_func.kit()
    if isinstance(contents, list):
      return pack
    for k in contents.keys():
        if k not in ["deck", "pack", "sealed", "variable", "other", "card"]:
            with open("log.log", 'a') as f:
                f.write("Invalid product definition: {0}\n".format(k))
                return pack
    for d in contents.get("deck", []):
        for i in range(d.get("count", 1)):
            try:
                pack.merge_kit(decks[d["set"]][d["name"]])
            except KeyError:
                with open("log.log", 'a') as f:
                    f.write("Invalid deck identifier {0}/{1}\n".format(d["set"], d["name"]))
    for p in contents.get("pack", []):
        for i in range(p.get("count", 1)):
            try:
                pack.merge_kit(boosters[p["set"]][p["code"]])
            except KeyError:
                with open("log.log", "a") as f:
                    f.write("Invalid pack identifier {0}/{1}\n".format(p["set"], p["code"]))
    for s in contents.get("sealed", []):
        if s["uuid"] not in sealed:
            ready = False
            break
        for i in range(s.get("count", 1)):
            pack.merge_kit(sealed[s["uuid"]])
    for c in contents.get("card", []):
        cpack = s_func.kit()
        foiling = "foil" if c["foil"] else "normal"
        try:
            cpack.add_card(cards.get(c["uuid"], {}).get(foiling, 0))
        except KeyError:
            with open("log.log", "a") as f:
                f.write("Card {0}/{1} missing uuid\n".format(c["set"], c["name"]))
        pack.merge_kit(cpack)
    p2 = s_func.kit()
    for version in contents.get("variable", []):
        pack = build_product(version, boosters, decks, sealed, cards)
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
    

priceJson = s_func.get_price_data("mtgJson/AllPrices.json")

setFolder = Path("mtgJson/AllSetFiles")
nSets = len(os.listdir(setFolder))
deckFolder = Path("mtgJson/AllDeckFiles")
nDecks = len(os.listdir(deckFolder))

boosters = {}
decks = {}
sealed = {}
products = []

# Build packs
for setFile in tqdm(setFolder.glob("*.json"), desc="Boosters", position=0, total=nSets):
    setCode = setFile.stem.lower()
    if setCode == "con_":
        setCode = "con"
    with open(setFile, 'rb') as f:
        allBoosters = dict(ijson.kvitems(f, "data.booster"))
    if allBoosters:
        boosters[setCode] = {}
        for typeCode, boosterPack in tqdm(allBoosters.items(), desc=" "+setCode, position=1, leave=False):
            if "arena" in typeCode:
                continue
            boosters[setCode][typeCode] = b_f.build_booster(boosterPack, priceJson)

# Build decks
for deckFile in tqdm(deckFolder.glob("*.json"), desc="Decks", position=0, total=nDecks):
    with open(deckFile, 'rb') as f:
        deckData = json.load(f)
    setCode = deckData["data"]["code"].lower()
    if setCode not in decks:
        decks[setCode] = {}
    name = deckData["data"]["name"]
    decks[setCode][name] = d_f.build_deck(deckData["data"], priceJson)

# Load products
for setFile in tqdm(setFolder.glob("*.json"), desc="Load Products", position=0, total=nSets):
    setCode = setFile.stem.lower()
    if setCode == "con_":
        setCode = "con"
    with open(setFile, 'rb') as f:
        cleanedProducts = [{**d, "set": setCode} for d in ijson.items(f, "data.sealedProduct.item")]
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
        pack = build_product(obj["contents"], boosters, decks, sealed, priceJson)
        if pack:
            sealed[obj["uuid"]] = pack
    t.close()
    del(t)

if len(products) > len(sealed):
    print("Missing products:")
    for p in products:
        if p["uuid"] not in sealed:
            print(p["name"])


print("products")
for p in products:
    if sealed[p["uuid"]].mean > 0:
        print(p["name"], sealed[p["uuid"]].summary())


if performance_meter:
    print("memory:", tracemalloc.get_traced_memory())
    print("duration:", time.time() - start_time)

plt.show()