from pipeline.extract import extract
from pipeline.transform import transform
from pipeline.load import load

def main(assets):
    for asset in assets:
        try:
            print(f"Processing {asset}...")
            raw_data = extract(asset)
            transformed_data = transform(raw_data, asset)
            load(transformed_data)
            print(f"Finished processing {asset}.\n")
        except Exception as e:
            print(f"Error processing {asset}: {e}\n")
            continue

if __name__ == "__main__":
    assets = ["AMD", "NVDA", "BTC-USD"]
    main(assets)