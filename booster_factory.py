
import sealed
import warnings

def build_sheet(cards, prices, logger=False, foil=False, fixed=False, bulkThreshold=0):
    sheet = sealed.kit()
    foiling = "foil" if foil else "normal"
    if fixed:
        sum_ = 0
        for uuid, weight in cards.items():
            if prices[uuid][foiling] < bulkThreshold:
                continue
            try:
                sum_ += prices[uuid][foiling] * weight
            except:
                if logger:
                    logger.warning("Missing price for card {0}/{1}\n".format(uuid, foiling))
        sheet.add_card(sum_)
    for uuid, weight in cards.items():
        try:
            if prices[uuid][foiling] < bulkThreshold:
                sheet.add_card(0, weight)
            else:
                sheet.add_card(prices[uuid][foiling], weight)
        except:
            if logger:
                logger.warning("Missing price for card {0}/{1}\n".format(uuid, foiling))
            sheet.add_card(0, weight)
    sheet.normalize()
    return sheet


def build_variant(sheets, contents):
    variant = sealed.kit()
    for sheet_name, sheet_count in contents.items():
        for i in range(sheet_count):
            variant.merge_kit(sheets[sheet_name])
    return variant

def build_booster(config, prices, logger=False, verbose=False, bulkThreshold=0):
    booster = sealed.kit()
    sheets = {}
    for name, data in config["sheets"].items():
        sheets[name] = build_sheet(data["cards"], prices, logger, data["foil"], data.get("fixed", False), bulkThreshold)
    for version in config["boosters"]:
        try:
            version_kit = build_variant(sheets, version["contents"])
        except KeyError:
            version_kit = build_variant(sheets, version["sheets"])
        booster.add_set(version_kit, weight=version["weight"])
    booster.normalize()
    if verbose:
        return sheets, booster
    return booster
    