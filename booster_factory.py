
import sealed
import warnings

def build_sheet(cards, prices, foil=False):
    foiling = "foil" if foil else "normal"
    sheet = sealed.kit()
    for uuid, rate in cards.items():
        try:
            sheet.add_card(prices[uuid][foiling], rate)
        except:
            warnings.warn("Missing price for card {0}/{1}".format(uuid, foiling))
    sheet.normalize()
    return sheet


def build_variant(sheets, contents):
    variant = sealed.kit()
    for sheet_name, sheet_count in contents.items():
        for i in range(sheet_count):
            variant.merge_kit(sheets[sheet_name])
    return variant

def build_booster(config, prices):
    booster = sealed.kit()
    sheets = {}
    for name, data in config["sheets"].items():
        sheets[name] = build_sheet(data["cards"], prices, data["foil"])
    for version in config["boosters"]:
        version_kit = build_variant(sheets, version["contents"])
        booster.add_set(version_kit, weight=version["weight"])
    booster.normalize()
    return booster
    