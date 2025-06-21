# ollama_client.py
# Handles communication with a local Ollama server for translation tasks.

import urequests # Standard MicroPython library for HTTP requests
import ujson   # Standard MicroPython library for JSON parsing
import settings # To get Ollama server URL and model name

def translate_text(text_to_translate, target_language="Spanish", source_language="English"):
    """
    Sends text to Ollama server for translation using its /api/generate endpoint.

    Args:
        text_to_translate (str): The text string to be translated.
        target_language (str): The language to translate the text into.
        source_language (str): The language of the input text.

    Returns:
        str: The translated text, or an error message if translation fails.
    """
    if settings.OLLAMA_SERVER_URL == "http://YOUR_OLLAMA_SERVER_IP:11434/api/generate" or \
       not settings.OLLAMA_SERVER_URL or \
       "YOUR_OLLAMA_SERVER_IP" in settings.OLLAMA_SERVER_URL:
        return "Error: Ollama Server URL not configured properly in settings.py"

    headers = {
        "Content-Type": "application/json"
    }

    # Constructing a prompt for translation.
    # The effectiveness of this prompt will depend on the Ollama model being used.
    prompt = f"Translate the following text from {source_language} to {target_language}. Output only the translated text and nothing else: \"{text_to_translate}\""

    # For some models, a more structured or conversational approach might be needed.
    # Example system prompt (if model supports it well in this API structure):
    # system_prompt = f"You are a translation assistant. Translate the user's text from {source_language} to {target_language}. Output only the translated text."

    data = {
        "model": settings.OLLAMA_MODEL,
        "prompt": prompt,
        # "system": system_prompt, # Optional: include if your model and Ollama version handle it this way
        "stream": False,  # Request a non-streaming response
        # "max_tokens": 150, # Optional: if supported and needed to control output length
        # "temperature": 0.3 # Optional: for more deterministic output
    }

    url = settings.OLLAMA_SERVER_URL # This should be the /api/generate endpoint typically

    print(f"Sending request to Ollama: {ujson.dumps(data)}")

    try:
        response = urequests.post(url, headers=headers, json=data)

        if response.status_code == 200:
            response_json = response.json() # Assuming non-streaming gives a single JSON object
            print(f"Ollama Raw Response: {response_json}")

            # The response structure for "stream": false for /api/generate is typically:
            # {
            #   "model": "model_name",
            #   "created_at": "timestamp",
            #   "response": "the_full_response_text",
            #   "done": true,
            #   ... (other stats)
            # }
            if 'response' in response_json and response_json.get('done', False):
                translated_text = response_json['response'].strip()
                # Sometimes models might add quotes around the translation, try to remove them
                if translated_text.startswith('"') and translated_text.endswith('"'):
                    translated_text = translated_text[1:-1]
                if translated_text.startswith("'") and translated_text.endswith("'"):
                    translated_text = translated_text[1:-1]
                return translated_text
            else:
                # If the response is streamed line-by-line (even with stream:false, some setups might do this)
                # This basic client is not set up to parse a stream of JSON objects.
                # For simplicity, we expect a single JSON object when stream:false.
                # A more robust client might need to handle concatenated JSON objects if stream:false isn't fully respected
                # or if the server sends data in chunks.
                full_response_text = ""
                try:
                    # Attempt to parse as if it's line-delimited JSON (common for streaming)
                    # This is a fallback, ideally stream:false gives one object.
                    response_content = response.text
                    for line in response_content.splitlines():
                        if line.strip():
                            json_line = ujson.loads(line)
                            if 'response' in json_line:
                                full_response_text += json_line['response']
                            if json_line.get('done'):
                                break
                    if full_response_text:
                        return full_response_text.strip()
                    else:
                         return "Error: Unexpected response structure from Ollama or empty response."

                except Exception as e_parse:
                    print(f"Error parsing Ollama streamed response: {e_parse}")
                    return f"Error: Could not parse Ollama response. Content: {response.text[:200]}"


        else:
            error_message = f"Error: Ollama API request failed with status code {response.status_code}"
            if response.text:
                error_message += f" - {response.text[:200]}" # Limit error text length
            print(error_message)
            return error_message

    except Exception as e:
        print(f"Error during Ollama API request: {e}")
        return f"Error: Exception during API request - {e}"
    finally:
        if 'response' in locals() and response:
            response.close()

# Example usage (for testing this module directly if possible in MicroPython env)
if __name__ == "__main__":
    print("Testing Ollama Client...")

    # Ensure settings.py is configured, especially OLLAMA_SERVER_URL and OLLAMA_MODEL
    # settings.OLLAMA_SERVER_URL = "http://localhost:11434/api/generate" # Example for local test
    # settings.OLLAMA_MODEL = "mistral"

    if "YOUR_OLLAMA_SERVER_IP" in settings.OLLAMA_SERVER_URL:
        print("Please configure your Ollama server URL in settings.py to run this test.")
    else:
        print(f"Using Ollama model: {settings.OLLAMA_MODEL} via {settings.OLLAMA_SERVER_URL}")

        text1 = "Hello, world!"
        target_lang1 = "Spanish"
        print(f"\nTranslating '{text1}' to {target_lang1}:")
        translation1 = translate_text(text1, target_language=target_lang1)
        print(f"Translation: {translation1}")

        text2 = "How are you?"
        target_lang2 = "French"
        print(f"\nTranslating '{text2}' to {target_lang2}:")
        translation2 = translate_text(text2, target_language=target_lang2)
        print(f"Translation: {translation2}")

        text3 = "Das ist ein Test."
        target_lang3 = "English"
        source_lang3 = "German"
        print(f"\nTranslating '{text3}' from {source_lang3} to {target_lang3}:")
        translation3 = translate_text(text3, target_language=target_lang3, source_language=source_lang3)
        print(f"Translation: {translation3}")

    print("\nOllama Client test finished.")
