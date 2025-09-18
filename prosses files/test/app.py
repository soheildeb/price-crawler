from itertools import product

product_a = {
    "base": {
        "id":12,
        "material":{"glossy":1, "cotton":2},
        "size": {"a4":1, "a3":2},
        "side": [1,2],
        "tirazh":[1,2,3,4,5],
        "dimensions": ["material","size", "side", "tirazh"]
    },
    "adt":None,
}

product_b = {
    "base": {
        "id":12,
        "side": [1,2],
        "size": {"a4":1, "a3":2},
        "tirazh":[1,2,3,4,5],
        "dimensions": ["side", "size", "tirazh"]
    },
    "adt":None,
}

def generate_combinations(type_obj):
    dims = type_obj["dimensions"]
    loop_lists = []

    for dim in dims:
        if dim == "size":
            loop_lists.append(type_obj["size"])
        elif dim == "side":
            loop_lists.append(type_obj["side"])
        elif dim == "tirazh":
            loop_lists.append(type_obj["tirazh"])
        elif dim == "material":
            loop_lists.append(type_obj.get("material", [None]))

    for combo in product(*loop_lists):
        yield dict(zip(dims, combo))

# چاپ خوانا
products = [product_a, product_b]
for prod in products:
    print(f"\nCombinations for product:")
    for combo in generate_combinations(prod["base"]):
        print(combo)
