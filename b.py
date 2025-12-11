import json

input_filename = 'elaf_brands.json'
output_filename = 'elaf_brands_cleaned.json'

try:
    # 1. Read the data
    with open(input_filename, 'r', encoding='utf-8') as f:
        brands = json.load(f)

    cleaned_brands = []

    # 2. Process the list
    for brand in brands:
        # Create a new dictionary with only the fields you want
        new_brand = {
            "id": brand.get("id"),
            "name": brand.get("name")
        }
        cleaned_brands.append(new_brand)

    # 3. Save the data
    with open(output_filename, 'w', encoding='utf-8') as f:
        json.dump(cleaned_brands, f, indent=2, ensure_ascii=False)

    print(f"Success! Processed {len(cleaned_brands)} brands.")
    print(f"Saved to: {output_filename}")

except FileNotFoundError:
    print(f"Error: Could not find '{input_filename}'.")
except json.JSONDecodeError:
    print(f"Error: '{input_filename}' is not valid JSON.")