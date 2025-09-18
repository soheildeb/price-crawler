class Product:
    def __init__(self, name, types, output_folder):
        self.name = name
        self.types = types  # list of dicts: {"name": "Glossy", "params": {...}}
        self.output_folder = output_folder

    def calculate_prices(self, session):
        """
        حلقه روی انواع محصول و محاسبه قیمت پایه + adt
        خروجی: dict{name of type: DataFrame}
        """
        import pandas as pd
        import os

        os.makedirs(self.output_folder, exist_ok=True)
        sheets = {}

        for t in self.types:
            type_name = t["name"]
            params = t["params"]
            rows = []
            for size in params["sizes"]:
                for side in params["sides"]:
                    for tirazh in params["tirazh_list"]:
                        base_price = calculate(
                            session,
                            sample_id=params["sample_id"],
                            print_kind=params["print_id"],
                            material=params["material_id"],
                            size=size,
                            delivery_id=params["delivery_id"],
                            tirazh=tirazh,
                            side=side,
                        )
                        adt_price = None
                        if "adt_id" in params:
                            adt_price = calculate_adt(
                                session,
                                sample_id=params["sample_id"],
                                sample_print_kind=params["print_id"],
                                sample_material_kind=params["material_id"],
                                adt_id=params["adt_id"],
                                size=size,
                                tirazh=tirazh,
                                delivery_id=params["delivery_id"],
                                side=side,
                            )
                        rows.append({
                            "Size": size,
                            "Side": side,
                            "Tirazh": tirazh,
                            "BasePrice": base_price,
                            "AdtPrice": adt_price
                        })
            sheets[type_name] = pd.DataFrame(rows)
        return sheets