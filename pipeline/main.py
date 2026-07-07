from pipeline.extract import extract
from pipeline.transform import transform
from pipeline.load import load

def main(assets):
    failed = []
    for asset in assets:
        try:
            print(f"Processing {asset}...")
            raw_data = extract(asset)
            transformed_data = transform(raw_data, asset)
            load(transformed_data)
        except RuntimeError as e:
            print(f"❌ {asset} — failed after retries: {e}")
            failed.append(asset)
        except ValueError as e:
            print(f"❌ {asset} — unrecoverable error (skipping): {e}")
            failed.append(asset)
        
    if failed:
        print(f"List of failed stock: {failed}")
    else:
        print(f"All asset has been loaded successfully.")

if __name__ == "__main__":
    assets = ["AMD", "NVDA", "BTC-USD"]
    main(assets)