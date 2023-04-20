import matplotlib.pyplot as plt
import sealed as s_func
import time
import tracemalloc
import booster_factory as b_f
import deck_factory as d_f
from glob import glob
from tqdm import tqdm
import ijson
import yaml

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

def build_product(contents, boosters, decks, sealed):
	ready = True
	pack = s_func.kit()
	if "deck" in contents:
		for d in contents["deck"]:
			for i in range(d.get("count", 1)):
				pack.merge_kit(decks[d["code"]])
	if "pack" in contents:
		for p in contents["pack"]:
			for i in range(p.get("count", 1)):
				pack.merge_kit(boosters[p["code"]])
	if "sealed" in contents:
		for s in contents["sealed"]:
			if s["code"] not in sealed:
				ready = False
				break
			for i in range(s.get("count", 1)):
				pack.merge_kit(sealed[s["code"]])
	if "variable" in contents:
		p2 = s_func.kit()
		for version in contents["variable"]:
			pack = build_product(version, boosters, decks, sealed)
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
	

priceJson = s_func.get_price_data("json/AllPrices.json")

boosters = {}
decks = {}
sealed = {}
products = []

# Build packs
with open("json/sealed_extended_data.json", "rb") as f:
    all_boosters = list(ijson.items(f, "item"))
    booster_tqdm = tqdm(all_boosters)
    booster_tqdm.set_description("Building booster packs")
    for full_config in booster_tqdm:
        type_code = full_config.get("code")
        if "arena" in type_code:
            continue
        booster = b_f.build_booster(full_config, priceJson)
        boosters[full_config["code"]] = booster
    booster_tqdm.close()
    del(booster_tqdm)

# Build decks
with open("json/decks.json", "rb") as f:
	all_decks = list(ijson.items(f, "item"))
	deck_tqdm = tqdm(all_decks)
	deck_tqdm.set_description("Building fixed decks")
	for config in deck_tqdm:
		deck = d_f.build_deck(config, priceJson)
		decks[config["code"]] = deck
	deck_tqdm.close()
	del(deck_tqdm)

# Load products
for file in glob("sets/*.yaml"):
	with open(file, 'rb') as f:
		products.extend(yaml.safe_load(f))

# Build products
for i in range(3):
	t = tqdm(products)
	t.set_description("Building sealed - pass {0}".format(i+1))
	for obj in t:
		if obj["code"] in sealed:
			continue
		pack = build_product(obj["contents"], boosters, decks, sealed)
		if pack:
			sealed[obj["code"]] = pack
	t.close()
	del(t)

if len(products) > len(sealed):
	print("Missing products:")
	for p in products:
		if p["code"] not in sealed:
			print(p["name"])


print("products")
for k, v in sealed.items():
	if v.mean > 0:
		print(k, v.summary())


if performance_meter:
    print("memory:", tracemalloc.get_traced_memory())
    print("duration:", time.time() - start_time)

plt.show()