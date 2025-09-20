from .base import *
import pandas as pd
import os
import sys


class Product:
    def __init__(self, name, config, output_location=None):
        self.name = name
        self.config = config
        self.output_location = output_location
        self.session = build_session()
        
    def calculate_prices(self, output_filename: str = None):
        output_filename = output_filename or f"{self.name}.xlsx"
        output_dir = self.output_location or "."
        final_path = os.path.join(output_dir, output_filename)

        df_base = pd.DataFrame()
        df_adts = []
    
        # --- base ---
        base_conf = self.config.get("base")
        if base_conf:
            rows = []
            for params in generate_combinations(base_conf):
                price = calculate(self.session, **params)
                rows.append({"BasePrice": price, **params})
            df_base = pd.DataFrame(rows)

    
        # --- adts ---
        for key, value in self.config.items():
            if key == "base":
                continue
            rows = []
            for params in generate_combinations(value):
                price = calculate_adt(self.session, **params)
                rows.append({"AdtPrice": price, **params})
            df_adts.append(pd.DataFrame(rows))
        
        if df_adts:
            df_adt = pd.concat(df_adts, ignore_index=True)

                        # اگه بخوای ستون‌ها کنار هم باشن:
            df_final = pd.concat([df_base.reset_index(drop=True),
                                df_adt.reset_index(drop=True)], axis=1)
            # اگه بخوای ردیف‌ها پشت هم باشن:
            # df_final = pd.concat([df_base, df_adt], ignore_index=True)
        else:
            df_final = df_base
        
        df_final.to_excel(final_path, index=False)
        print(f"Saved results to {final_path}")