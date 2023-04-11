import matplotlib.pyplot as plt
import sealed as s_func
import time
import tracemalloc
import booster_factory as b_f
from glob import glob
from tqdm import tqdm
import ijson

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

priceJson = s_func.get_price_data("json/AllPrices.json")

boosters = []

files_glob = tqdm(glob("json/AllSetFiles/*.json"))
for file_name in files_glob:
	with open(file_name, "rb") as f:
		all_boosters = dict(ijson.kvitems(f, "data.booster"))
		for type_code, config in all_boosters.items():
			if "arena" in type_code:
				continue
			booster = b_f.build_booster(config, priceJson)
			set_code = file_name.split("/")[-1][:-5]
			variant = type_code
			if variant in ["vip", "premium"]:
				variant = "collector"
			boosters.append({"set": set_code, "type": variant, "booster": booster})
files_glob.close()
del(files_glob)

for b in boosters:
	print(b["set"], b["type"], b["booster"].summary())

if performance_meter:
    print("memory:", tracemalloc.get_traced_memory())
    print("duration:", time.time() - start_time)

plt.show()