def collect_ids(items):
    pairs = []
    for i, item in enumerate(items):
        for j, value in enumerate(item["values"]):
            pairs.append({"id": item["id"], "index": (i, j), "value": value})
    return pairs
