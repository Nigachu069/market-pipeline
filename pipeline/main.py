from extract import extract
from transform import transform
from load import load

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

assets = ["AMD", "NVDA", "BTC-USD"]

if __name__ == "__main__":
    main(assets)