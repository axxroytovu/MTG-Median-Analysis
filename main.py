import matplotlib.pyplot as plt
import sets.STX
import sets.SNC
import sets.CLB
import sets._2X2
import sealed as s_func
import time
import tracemalloc

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

sealed = {}

print("SNC")
sealed["SNC"] = sets.SNC.main(priceJson)
sealed['SNC']['prices'] = {
    'draft': {'booster': 2.60, 'box': 69.01},
    'set': {'booster': 3.94, 'box': 87.84},
    'collector': {'booster': 15.46, 'box': 128.87}
}
print("2X2")
sealed['2X2'] = sets._2X2.main(priceJson)
sealed['2X2']['prices'] = {
    'draft': {'booster': 13.75, 'box': 262.0},
    'collector': {'booster': 39.99, 'box': 228.0}
}
print("STX")
sealed['STX'] = sets.STX.main(priceJson)
sealed['STX']['prices'] = {
    'draft': {'booster': 3.37, 'box': 102.9},
    'set': {'booster': 4.25, 'box': 99.65},
    'collector': {'booster': 22.44, 'box': 220.0}
}
print("CLB")
sealed['CLB'] = sets.CLB.main(priceJson)
sealed['CLB']['prices'] = {
    'draft': {'booster': 3.98, 'box': 92.73},
    'set': {'booster': 5.9, 'box': 80.59},
    'collector': {'booster': 15.94, 'box': 156.89}
}

# Set Boosters
settings = {"sort": "release", "norm": True, "yscale": "linear"}
create_boxplots(sealed, ["sealed", "draft", "booster"], **settings)
plt.savefig("draft_booster.png")
create_boxplots(sealed, ["sealed", "set", "booster"], **settings)
plt.savefig("set_booster.png")
create_boxplots(sealed, ["sealed", "collector", "booster"], **settings)
plt.savefig("collector_booster.png")
create_boxplots(sealed, ["sealed", "draft", "box"], **settings)
plt.savefig("draft_box.png")
create_boxplots(sealed, ["sealed", "set", "box"], **settings)
plt.savefig("set_box.png")
create_boxplots(sealed, ["sealed", "collector", "box"], **settings)
plt.savefig("collector_box.png")
settings.update({"norm": False})
create_boxplots(sealed, ['set', 'common'], **settings)
plt.savefig("all_commons.png")
create_boxplots(sealed, ['set', 'uncommon'], **settings)
plt.savefig("all_uncommons.png")
create_boxplots(sealed, ['set', 'rareMythic'], **settings)
plt.savefig("all_rm.png")
create_boxplots(sealed, ['set', 'showcase'], **settings)
plt.savefig("all_showcase.png")

if performance_meter:
    print("memory:", tracemalloc.get_traced_memory())
    print("duration:", time.time() - start_time)

plt.show()