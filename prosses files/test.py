import pandas as pd
from tqdm import tqdm
from base.base import *
# Constants
sample_id = 2222
print_id = 1047
material_id = 1093
delivery_id = 1213

sizes = {
    74: "9*5",
    75: "8.5*5.5",
    76: "9*6",
    77: "5*5",
}

tirazh_list = [1, 50, 100, 200, 300, 500, 1000]

sides = {
    1: "One Side",
    2: "Two Side",
}

prod = {
    "base":{
        "sample_id":2222,
        "material":1093,
        "delivery_id":1213,
        "print_kind":1047,
        "size":{
            74: "9*5",
            75: "8.5*5.5",
            76: "9*6",
            77: "5*5",
        },
        "tirazh": [1, 50, 100, 200, 300, 500, 1000],
        "side":{1, 2}
        } 
}


def main():
    sess = build_session()
    results = []

    total_iterations = len(sizes) * len(sides) * len(tirazh_list)

    try:
        with tqdm(total=total_iterations, desc="Calculating prices", ncols=100) as pbar:
            for size_id, size_name in sizes.items():
                for side_id, side_name in sides.items():
                    for tirazh in tirazh_list:
                        price = calculate(
                            sess,
                            sample_id=sample_id,
                            print_kind=print_id,
                            material=material_id,
                            size=size_id,
                            delivery_id=delivery_id,
                            tirazh=tirazh,
                            side=side_id,
                        )
                        results.append({
                            "Size": size_name,
                            "Side": side_name,
                            "Tirazh": tirazh,
                            "Price": price,
                        })
                        pbar.update(1)

        # Save results to Excel only if all calculations succeeded
        df = pd.DataFrame(results)
        df.to_excel("prices.xlsx", index=False)
        print("\n✅ Operation completed successfully. Results saved to prices.xlsx.")

    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
        print("Execution stopped. No output file was created.")


if __name__ == "__main__":
    main()
