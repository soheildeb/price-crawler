from .utils import *
import pandas as pd
import os
from openpyxl import load_workbook


class Product:
    def __init__(self, name, category, config, output_location=None, progress_callback=None):
        self.name = name
        self.category = category
        self.config = config
        self.progress_callback = progress_callback
        if output_location:
            self.output_location = output_location
        else:
            self.output_location = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "result"))
            os.makedirs(self.output_location, exist_ok=True)
        self.session = build_session()
    
    def get_total_combinations(self):
        """Return total number of combinations for Base + all ADTs."""
        total = 0
        for key, value in self.config.items():
            combos = list(generate_combinations(value))
            total += len(combos)
        return total
    
    def calculate_prices(self, output_filename: str = None, progress_callback=None):
        output_filename = output_filename or f"{self.category}.xlsx"
        output_dir = self.output_location or "."
        final_path = os.path.join(output_dir, output_filename)
        
        done = 0
        total = self.get_total_combinations()

        df_base = pd.DataFrame()
        df_adts = []
        # --- base ---
        base_conf = self.config.get("base")
        if base_conf:
            rows = []
            for params_api, params_display in generate_combinations(base_conf):
                price = calculate(self.session, **params_api)
                rows.append({"BasePrice": price, **params_display})
                done += 1
                if progress_callback:
                    progress_callback(done, total)  # update progress
            df_base = pd.DataFrame(rows)

        # --- adts ---
        for key, value in self.config.items():
            if key == "base":
                continue
            rows = []
            for params_api, params_display in generate_combinations(value):
                price = calculate_adt(self.session, **params_api)
                rows.append({"finishing": price, **params_display})
                done += 1
                if progress_callback:
                    progress_callback(done, total)
            df_adts.append(pd.DataFrame(rows))

        if df_adts:
            df_adt = pd.concat(df_adts, ignore_index=True)
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