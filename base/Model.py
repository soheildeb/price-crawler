from .base import *
import pandas as pd
import os
from openpyxl import load_workbook


class Product:
    def __init__(self, name, config, output_location=None):
        self.name = name
        self.config = config
        self.output_location = output_location
        self.session = build_session()
        
    def calculate_prices(self, output_filename: str = None):
        output_filename = output_filename or f"Prices.xlsx"
        output_dir = self.output_location or "."
        final_path = os.path.join(output_dir, output_filename)

        df_base = pd.DataFrame()
        df_adts = []

        # --- base ---
        base_conf = self.config.get("base")
        if base_conf:
            rows = []
            for params_api, params_display in generate_combinations(base_conf):
                price = calculate(self.session, **params_api)
                rows.append({"BasePrice": price, **params_display})
            df_base = pd.DataFrame(rows)

        # --- adts ---
        for key, value in self.config.items():
            if key == "base":
                continue
            rows = []
            for params_api, params_display in generate_combinations(value):
                price = calculate_adt(self.session, **params_api)
                rows.append({"finishing": price, **params_display})
            df_adts.append(pd.DataFrame(rows))

        if df_adts:
            df_adt = pd.concat(df_adts, ignore_index=True)
            # Place ADT columns next to Base
            df_final = pd.concat([df_base.reset_index(drop=True),
                                df_adt.reset_index(drop=True)], axis=1)
        else:
            df_final = df_base

        # --- write to Excel preserving other sheets ---
        if os.path.exists(final_path):
            with pd.ExcelWriter(final_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
                df_final.to_excel(writer, sheet_name=self.name, index=False)
        else:
            with pd.ExcelWriter(final_path, engine='openpyxl') as writer:
                df_final.to_excel(writer, sheet_name=self.name, index=False)

        print(f"Saved results to {final_path} (sheet: {self.name})")