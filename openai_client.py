# openai_client.py
# Handles communication with the OpenAI API for translation tasks.

import urequests # Standard MicroPython library for HTTP requests
import ujson   # Standard MicroPython library for JSON parsing
import settings # To get API key and URL

def translate_text(text_to_translate, target_language="Spanish", source_language="English"):
    """
    Sends text to OpenAI API for translation.
    Note: OpenAI's general models (like GPTs) are used here via chat completions.
          For dedicated translation, you might explore specific translation APIs if available
          or structure the prompt more carefully.

    Args:
        text_to_translate (str): The text string to be translated.
        target_language (str): The language to translate the text into.
        source_language (str): The language of the input text.

    Returns:
        str: The translated text, or an error message if translation fails.
    """
    if settings.OPENAI_API_KEY == "YOUR_OPENAI_API_KEY" or not settings.OPENAI_API_KEY:
        return "Error: OpenAI API Key not configured in settings.py"

    headers = {
        "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    # Constructing a prompt for translation using a chat model
    # This can be adjusted based on the model's capabilities and preferred prompting style.
    prompt = f"Translate the following text from {source_language} to {target_language}: \"{text_to_translate}\""

    # Payload for the Chat Completions API
    # For older models like 'text-davinci-003' via the completions endpoint (not chat),
    # the payload structure would be different:
    # data = {
    #     "model": settings.OPENAI_TRANSLATE_MODEL,
    #     "prompt": prompt,
    #     "max_tokens": 60 + len(text_to_translate) // 2, # Estimate tokens for translation
    #     "temperature": 0.3 # Lower temperature for more deterministic output
    # }
    # url = "https://api.openai.com/v1/completions" # if using the older completions endpoint

    # Using Chat Completions API (e.g., for gpt-3.5-turbo, gpt-4)
    data = {
        "model": settings.OPENAI_TRANSLATE_MODEL, # Ensure this model is a chat model
        "messages": [
            {"role": "system", "content": f"You are a helpful assistant that translates text from {source_language} to {target_language}."},
            {"role": "user", "content": text_to_translate}
        ],
        "max_tokens": 150, # Adjust as needed
        "temperature": 0.5 # Adjust for creativity vs. precision
    }
    url = settings.OPENAI_API_URL # Should be the chat completions endpoint

    print(f"Sending request to OpenAI: {ujson.dumps(data)}")

    try:
        response = urequests.post(url, headers=headers, json=data)

        if response.status_code == 200:
            response_json = response.json()
            print(f"OpenAI Raw Response: {response_json}")

            # For Chat Completions API:
            if 'choices' in response_json and len(response_json['choices']) > 0:
                # The translation is in the message content of the first choice
                translated_text = response_json['choices'][0]['message']['content'].strip()
                return translated_text
            # For older Completions API (e.g. text-davinci-003):
            # elif 'choices' in response_json and len(response_json['choices']) > 0:
            #    translated_text = response_json['choices'][0]['text'].strip()
            #    return translated_text
            else:
                return "Error: Unexpected response structure from OpenAI."
        else:
            error_message = f"Error: OpenAI API request failed with status code {response.status_code}"
            if response.text:
                error_message += f" - {response.text}"
            print(error_message)
            return error_message

    except Exception as e:
        print(f"Error during OpenAI API request: {e}")
        return f"Error: Exception during API request - {e}"
    finally:
        if 'response' in locals() and response:
            response.close()


# Example usage (for testing this module directly if possible in MicroPython env)
if __name__ == "__main__":
    print("Testing OpenAI Client...")

    # Configure settings for a direct test (normally done by importing settings)
    # This requires settings.py to be in the same directory and configured
    # settings.OPENAI_API_KEY = "YOUR_ACTUAL_KEY_FOR_TESTING_HERE" # Temporary for local test

    if settings.OPENAI_API_KEY == "YOUR_OPENAI_API_KEY":
        print("Please set your OpenAI API key in settings.py to run this test.")
    else:
        print(f"Using model: {settings.OPENAI_TRANSLATE_MODEL} via {settings.OPENAI_API_URL}")
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

        # Example of a non-English source
        text3 = "Wie geht es Ihnen?"
        target_lang3 = "English"
        source_lang3 = "German"
        print(f"\nTranslating '{text3}' from {source_lang3} to {target_lang3}:")
        translation3 = translate_text(text3, target_language=target_lang3, source_language=source_lang3)
        print(f"Translation: {translation3}")

    print("\nOpenAI Client test finished.")
