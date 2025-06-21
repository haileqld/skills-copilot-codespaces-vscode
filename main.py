# main.py
# Main application file for the ESP32 translation bot

import time
import settings
import wifi_manager
import openai_client
import ollama_client
import audio_input
import audio_output

# Global state for service selection
current_service = "openai" # Default service

def select_service():
    """
    Allows user to select a service (simulated).
    In a real app, this could be a button press or voice command.
    For now, it will just toggle or be fixed.
    """
    global current_service
    # This is a placeholder for a more interactive selection.
    # For testing, we can alternate or fix it.
    # if current_service == "openai":
    #     current_service = "ollama"
    # else:
    #     current_service = "openai"
    # print(f"Service selected: {current_service}")
    # audio_output.speak_text(f"Using {current_service} service.")
    return current_service

def parse_translation_command(command):
    """
    Rudimentary parsing of a translation command.
    Expected format: "translate 'text to translate' to language"
    Returns: (text_to_translate, target_language, source_language) or (None, None, None)
    """
    command_lower = command.lower()
    try:
        if "translate " not in command_lower:
            return None, None, None

        parts = command_lower.split("translate ", 1)[1].split(" to ", 1)
        text_to_translate_section = parts[0].strip()

        # Remove potential quotes around the text to translate
        if text_to_translate_section.startswith("'") and text_to_translate_section.endswith("'"):
            text_to_translate = text_to_translate_section[1:-1]
        elif text_to_translate_section.startswith('"') and text_to_translate_section.endswith('"'):
            text_to_translate = text_to_translate_section[1:-1]
        else:
            text_to_translate = text_to_translate_section

        target_language = "Spanish" # Default if not specified or parsing fails
        if len(parts) > 1:
            target_language_full = parts[1].strip()
            # Further parsing could extract "from X to Y"
            # For now, assume "to Y" is the target language
            # And source is implicitly English or auto-detected by the service
            # A more robust parser would identify "from" language as well.
            target_language = target_language_full.split(" ")[0].capitalize()


        # Source language is assumed English for now by clients, can be enhanced
        source_language = "English"

        if not text_to_translate:
            return None, None, None

        print(f"Parsed command: Text='{text_to_translate}', TargetLang='{target_language}', SourceLang='{source_language}'")
        return text_to_translate, target_language, source_language
    except Exception as e:
        print(f"Error parsing command '{command}': {e}")
        return None, None, None


def main_loop():
    """Main loop of the application."""
    audio_output.speak_text("Hello! I am your translation assistant.")
    time.sleep(0.5) # Give time for speech to finish if simulated quickly

    # How many interactions before stopping? (For testing)
    interactions = 2
    count = 0

    while count < interactions:
        count += 1
        print(f"\n--- Interaction {count}/{interactions} ---")
        audio_output.speak_text("Please tell me what you want to translate.")

        # 1. Listen to user (simulated STT)
        # The simulated audio_input.record_and_transcribe_audio() returns "translate 'hello world' to Spanish"
        user_query = audio_input.record_and_transcribe_audio(duration_ms=5000)

        if not user_query:
            audio_output.speak_text("I didn't catch that. Please try again.")
            time.sleep(0.5)
            if count < interactions: # Don't repeat last time if it fails
                continue
            else:
                break

        audio_output.speak_text(f"You said: {user_query}") # Echo back
        time.sleep(1) # Allow user to hear the echo

        # 2. Parse command
        text_to_translate, target_language, source_language = parse_translation_command(user_query)

        if not text_to_translate:
            audio_output.speak_text("I couldn't understand the translation request. Please say something like: translate 'text' to language.")
            time.sleep(0.5)
            continue

        # 3. Select service (for this example, we'll try OpenAI first, then Ollama if OpenAI fails or as a demo)
        # In a real app, user might choose, or it could be based on config.

        # --- Try OpenAI ---
        if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY != "YOUR_OPENAI_API_KEY":
            audio_output.speak_text(f"Translating using OpenAI to {target_language}.")
            print(f"Attempting OpenAI translation for: '{text_to_translate}' to {target_language} from {source_language}")

            translated_text_openai = openai_client.translate_text(
                text_to_translate,
                target_language=target_language,
                source_language=source_language
            )

            if translated_text_openai and not translated_text_openai.startswith("Error:"):
                print(f"OpenAI Translation: {translated_text_openai}")
                audio_output.speak_text(translated_text_openai)
                time.sleep(1) # Allow speech to be heard
                # For this demo, we'll still try Ollama if available
            else:
                print(f"OpenAI translation failed: {translated_text_openai}")
                audio_output.speak_text("OpenAI translation failed.")
                if translated_text_openai: # Speak the error if available
                    # audio_output.speak_text(translated_text_openai[:100]) # Speak part of the error
                    pass # Avoid speaking long technical errors
                time.sleep(0.5)
        else:
            print("OpenAI API key not configured. Skipping OpenAI.")
            audio_output.speak_text("OpenAI not configured.")
            time.sleep(0.5)

        # --- Try Ollama (either as fallback or alternative) ---
        # Check if Ollama server seems configured (basic check)
        if settings.OLLAMA_SERVER_URL and "YOUR_OLLAMA_SERVER_IP" not in settings.OLLAMA_SERVER_URL:
            audio_output.speak_text(f"Now, trying with Ollama to {target_language}.")
            print(f"Attempting Ollama translation for: '{text_to_translate}' to {target_language} from {source_language}")

            translated_text_ollama = ollama_client.translate_text(
                text_to_translate,
                target_language=target_language,
                source_language=source_language
            )

            if translated_text_ollama and not translated_text_ollama.startswith("Error:"):
                print(f"Ollama Translation: {translated_text_ollama}")
                audio_output.speak_text(translated_text_ollama)
                time.sleep(1)
            else:
                print(f"Ollama translation failed: {translated_text_ollama}")
                audio_output.speak_text("Ollama translation failed.")
                if translated_text_ollama:
                    # audio_output.speak_text(translated_text_ollama[:100])
                    pass
                time.sleep(0.5)
        else:
            print("Ollama server not configured or using placeholder. Skipping Ollama.")
            audio_output.speak_text("Ollama not configured.")
            time.sleep(0.5)

        if count < interactions: # Don't say "next request" on the last one
            audio_output.speak_text("Ready for the next request.")
            time.sleep(1)


if __name__ == "__main__":
    print("ESP32 Translation Bot Initializing...")

    # 1. Validate settings
    # settings.validate_settings() # This function in settings.py just prints warnings
    if settings.WIFI_SSID == "YOUR_WIFI_SSID" or \
       (settings.OPENAI_API_KEY == "YOUR_OPENAI_API_KEY" and \
        "YOUR_OLLAMA_SERVER_IP" in settings.OLLAMA_SERVER_URL) :
        print("CRITICAL: Wi-Fi SSID or any translation service (OpenAI/Ollama) is not configured in settings.py.")
        print("Please configure settings.py before running.")
        audio_output.speak_text("Error. System not configured.") # Use audio_output for consistency if it's already imported
        # In a real ESP32 app, might flash an LED or enter a config mode.
        # For this simulation, we'll exit.
    else:
        print("Settings appear to be present (though not fully validated for correctness here).")


    # 2. Initialize Audio I/O (Placeholders for now)
    if not audio_input.init_microphone():
        print("Failed to initialize microphone. Functionality will be limited.")
        # audio_output.speak_text("Microphone error.") # Might not have speaker yet
    if not audio_output.init_speaker():
        print("Failed to initialize speaker. Functionality will be limited.")
        # No speak_text possible here if speaker init failed

    # 3. Connect to Wi-Fi
    wifi_connected = False
    if settings.WIFI_SSID != "YOUR_WIFI_SSID":
        print("Attempting Wi-Fi connection...")
        # audio_output.speak_text("Connecting to Wi-Fi.") # Speaker might not be ready
        if wifi_manager.connect_wifi():
            print(f"Wi-Fi connected. IP: {wifi_manager.get_ip_address()}")
            # audio_output.speak_text("Wi-Fi connected.") # Too early for complex speech
            wifi_connected = True
        else:
            print("Failed to connect to Wi-Fi. Translation services will not work.")
            audio_output.speak_text("Wi-Fi connection failed.")
            # Depending on the app, might halt or offer limited functionality
    else:
        print("Wi-Fi SSID not configured. Skipping Wi-Fi connection.")
        audio_output.speak_text("Wi-Fi not configured.")

    if not wifi_connected:
        print("Proceeding without Wi-Fi. Cloud services will fail.")
        audio_output.speak_text("Continuing without internet. Cloud features disabled.")


    print("\nInitialization complete. Starting main loop.")
    # audio_output.speak_text("System ready.") # Moved greeting into main_loop

    try:
        main_loop()
    except KeyboardInterrupt:
        print("Program stopped by user.")
        audio_output.speak_text("Shutting down now.")
    except Exception as e:
        print(f"An unhandled error occurred in main_loop: {e}")
        # Attempt to speak the error if possible, but keep it simple
        # In MicroPython, full error objects might be complex to serialize to speech
        audio_output.speak_text("An application error occurred.")
    finally:
        print("\nShutting down...")
        audio_input.deinit_microphone()
        audio_output.deinit_speaker()
        if wifi_manager.is_wifi_connected():
            wifi_manager.disconnect_wifi()
        print("Cleanup complete.")

    print("ESP32 Translation Bot Finished.")
