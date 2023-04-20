
import sealed
import warnings

def build_sheet(cards, prices, foil=False):
    sheet = sealed.kit()
    for card in cards:
        foiling = "foil" if card["foil"] else "normal"
        try:
            sheet.add_card(prices[card["uuid"]][foiling], card["weight"])
        except:
            with open("log.log", 'a') as file:
                file.write("Missing price for card {0}/{1}/{2}\n".format(card["set"], card["number"], foiling))
            sheet.add_card(0, card["weight"])
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
        sheets[name] = build_sheet(data["cards"], prices)
    for version in config["boosters"]:
        version_kit = build_variant(sheets, version["sheets"])
        booster.add_set(version_kit, weight=version["weight"])
    booster.normalize()
    return booster
    