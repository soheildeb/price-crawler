from base.Model import Product

prod = {
    "base":{
        "sample_id":{2222},
        "material":{1093},
        "delivery_id":{1213},
        "print_kind":{1047},
        "size":{
            74: "9*5",
            75: "8.5*5.5",
            76: "9*6",
            77: "5*5",
        },
        "side":{1, 2},  
        "tirazh": [1, 50, 100, 200, 300, 500, 1000],

    }
}

p1 = Product(name="business-card", config=prod)
p1.calculate_prices()