from .base import *
import pandas as pd
import os


class Product:
    def __init__(self, name, config, output_location=None):
        self.name = name
        self.config = config
        self.output_location = output_location
    session = build_session()
    def calculate_prices(self, sess=session):
        rows = []
        for params in generate_combinations(self.config["base"]):
            price = calculate(sess,
                **params
            )
            rows.append({
                "BasePrice": price,
                **params
           })
            
        df = pd.DataFrame(rows)
        df.to_excel(f"{self.name}.xlsx", index=False)