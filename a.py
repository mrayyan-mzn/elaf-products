import json
import os

def build_category_tree(flat_categories):
    # 1. Initialize a map to store nodes by their ID for O(1) access
    id_map = {}
    
    # 2. Create the Node objects
    for item in flat_categories:
        node = {
            "id": item["id"],
            "name": {
                "ar": item["name"]["ar"],
                # Ensure English is uppercase to match your target output
                "en": item["name"]["en"]
            },
            "subCategories": []
        }
        
        # Normalize ID (uppercase and underscores) for consistent matching
        # e.g. "fresh-food" matches "FRESH_FOOD"
        normalized_id = item["id"].upper().replace("-", "_")
        id_map[normalized_id] = node

    # 3. Build the Hierarchy
    roots = []
    
    for item in flat_categories:
        normalized_id = item["id"].upper().replace("-", "_")
        current_node = id_map[normalized_id]
        
        parent_id_raw = item.get("parentId")
        
        if parent_id_raw:
            # Normalize parent ID to match keys in id_map
            normalized_parent_id = parent_id_raw.upper().replace("-", "_")
            
            if normalized_parent_id in id_map:
                id_map[normalized_parent_id]["subCategories"].append(current_node)
            else:
                # If parent ID exists but is not found in the file, treat as root
                roots.append(current_node)
        else:
            # No parentId means this is a root category
            roots.append(current_node)

    # 4. Clean up: Remove empty 'subCategories' keys recursively
    def remove_empty_subs(nodes):
        for node in nodes:
            if len(node["subCategories"]) == 0:
                del node["subCategories"]
            else:
                remove_empty_subs(node["subCategories"])
                
    remove_empty_subs(roots)
    return roots

# --- Main Execution ---
input_filename = 'elaf_categories.json'
output_filename = 'nested_categories.json'

try:
    # Read from file
    with open(input_filename, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    # Process data
    nested_structure = build_category_tree(data)
    
    # Write to new file
    with open(output_filename, 'w', encoding='utf-8') as f:
        json.dump(nested_structure, f, indent=2, ensure_ascii=False)
        
    print(f"Successfully converted data. Output saved to '{output_filename}'")
    
    # Optional: Print the first item to verify
    # print(json.dumps(nested_structure[0], indent=2, ensure_ascii=False))

except FileNotFoundError:
    print(f"Error: The file '{input_filename}' was not found.")
except json.JSONDecodeError:
    print(f"Error: The file '{input_filename}' contains invalid JSON.")
except Exception as e:
    print(f"An error occurred: {e}")