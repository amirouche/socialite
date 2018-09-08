from time import time


FILTERS = dict()


def maybe(v):
    return '' if v is None else v


FILTERS['maybe'] = maybe


def epoch2human(epoch):
    return int(time() - epoch)  # TODO: humanize for the real


FILTERS["epoch2human"] = epoch2human
