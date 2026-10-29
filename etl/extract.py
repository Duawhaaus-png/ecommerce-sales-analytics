import json
from pathlib import Path
import requests

BASE_URL = "https://dummyjson.com"

ENDPOINTS = {
    "products": f"{BASE_URL}/products",
    "cart" : f"{BASE_URL}/cart",
    "users": f"{BASE_URL}/users",
}

def extract_data(name,url):
    print(f"Extracting {name}...")
    response = requests.get(
        url,
        params = {"limit":0},
        timeout = 30,
    )
    response.raise_for_status()
    data = response.json()

    output_dir = Path("data/raw")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / f"{name}.json"
    with output_file.open("w",encoding="utf-8") as file:
        json.dump(
            data,
            file,
            ensure_ascii=False,
            indent=2,
        )
    print(f"Saved to {output_file}")
    return data
def main():
    for name,url in ENDPOINTS.items():
        try:
            data = extract_data(name,url)
            print(f"Successfully extracted {name}\n")
        except requests.exceptions.RequestException as e:
            print(f"API request failed for {name}: {e}")
        except (ValueError, OSError) as e:
            print(f"Data processing failed for {name}: {e}")
if __name__ == "__main__":
    main()
