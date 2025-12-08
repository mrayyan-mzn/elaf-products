import google.generativeai as genai
import typing_extensions as typing
import json
import time
import sys
import threading
import itertools

# --- CONFIGURATION ---
# 1. PASTE YOUR NEW API KEY HERE
MY_KEY = "AIzaSyAOEJj8fmKtAz3L8YYb1WiT1Vm9zwCEmJM"  # <--- REPLACE THIS!


# 2. Define Schema
class LocalizedName(typing.TypedDict):
    ar: str
    en: str


class OutputItem(typing.TypedDict):
    id: str
    name: LocalizedName
    original_value: str
    parentId: str | None


# --- HELPER: LIVE SPINNER ---
def live_spinner(stop_event):
    """Shows a rotating spinner and live timer in the console."""
    start_time = time.time()
    spinner_chars = itertools.cycle(["|", "/", "-", "\\"])

    while not stop_event.is_set():
        elapsed = time.time() - start_time
        # \r goes back to the start of the line, end='' prevents new line
        sys.stdout.write(
            f"\r--- [WAITING] Gemini is thinking... {next(spinner_chars)}  ({elapsed:.1f}s)"
        )
        sys.stdout.flush()
        time.sleep(0.1)

    # Clean up the line when done
    sys.stdout.write(
        f"\r--- [DONE] Response received in {time.time() - start_time:.2f}s        \n"
    )


def transform_to_structure(api_key: str, input_json: dict | list) -> list[OutputItem]:
    print(f"--- [LOG] Configuring API... ---")
    genai.configure(api_key=api_key)

    # for m in genai.list_models():
    #     print(f"{m.name}")

    model_name = "models/gemini-2.5-flash"

    try:
        model = genai.GenerativeModel(model_name)
    except Exception as e:
        print(f"--- [ERROR] Failed to load model: {e}")
        return []

    prompt = f"""
    Analyze the provided Input JSON and transform it into a structured list.
    
    Requirements:
    1. **Correction & Cleanup**: Detect and fix any typos or spelling mistakes in the 'name' field.
    2. 'id': Generate a unique, short English String ID (slug).
    3. 'name': Object containing 'ar' (Arabic translation) and 'en' (Corrected English name).
    4. **'original_value'**: Store the EXACT text from the input JSON here (including typos) to use as a search reference.
    5. 'parentId': The 'id' of the parent category. Use null for top-level.
    
    Input JSON:
    {json.dumps(input_json)}
    """

    # --- START LIVE TIMER ---
    stop_spinner = threading.Event()
    spinner_thread = threading.Thread(target=live_spinner, args=(stop_spinner,))
    spinner_thread.start()

    response = None
    try:
        # The actual API call
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
                response_schema=list[OutputItem],
            ),
        )
    except Exception as e:
        stop_spinner.set()
        spinner_thread.join()
        print(f"\n--- [ERROR] API Call Failed: {e}")
        return []

    # --- STOP LIVE TIMER ---
    stop_spinner.set()
    spinner_thread.join()

    # Parse Result
    try:
        return json.loads(response.text)
    except Exception as e:
        print(f"--- [ERROR] JSON Parsing Failed: {e}")
        return []


# --- MAIN EXECUTION ---
if __name__ == "__main__":
    # Load Data
    try:
        with open("elaf_categories.json", "r", encoding="utf-8") as f:
            raw_data = json.load(f)
            print(
                f"--- [LOG] Loaded {len(raw_data) if isinstance(raw_data, list) else 'input'} items from file ---"
            )
    except FileNotFoundError:
        print("--- [WARN] File not found. Using dummy data. ---")
        raw_data = [{"title": "Fruits", "children": ["Apple", "Orange"]}]

    # Run
    structured_data = transform_to_structure(MY_KEY, raw_data)

    if structured_data:
        # Save
        filename = "elaf_structured_categories.json"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(json.dumps(structured_data, indent=2, ensure_ascii=False))

        print(f"--- [SUCCESS] Processed {len(structured_data)} items.")
        print(f"--- [LOG] Saved to '{filename}'")
