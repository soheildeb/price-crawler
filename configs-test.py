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
        },
        'side': {1: 'یکرو',2: 'دورو'},
        "tirazh": [1, 50],
    },
    "cover":{
        'workTypeID': {3},
        'deliveryID': {1518},
        'sampleSizeID': {288},
        'sampleID': {2399},
        'multiCopyCount': {1},
        'sampleMaterialID': {1299}, 
        'samplePrintKindID': {1122},
        'id': {15889: 'سلفون مخمل', 15890: 'سلفون مات'},
        'side': {1: 'یکرو',2: 'دورو'},
        'tirazhCount': [1, 50],
    }
}

p1 = Product(name="کارت ویزیت گلاسه", config=prod)
p1.calculate_prices()

