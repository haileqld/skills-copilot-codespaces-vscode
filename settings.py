# settings.py
# Configuration settings for the ESP32 Translation Bot

# Wi-Fi Credentials
WIFI_SSID = "YOUR_WIFI_SSID"
WIFI_PASSWORD = "YOUR_WIFI_PASSWORD"

# OpenAI API Configuration
OPENAI_API_KEY = "YOUR_OPENAI_API_KEY"
OPENAI_API_URL = "https://api.openai.com/v1/chat/completions" # Example for chat models, adjust if using other endpoints
# OPENAI_TRANSLATE_MODEL = "gpt-3.5-turbo" # Or any other model suitable for translation
OPENAI_TRANSLATE_MODEL = "text-davinci-003" # Or another suitable model if not using chat completions for direct translation
                                        # For actual translation tasks, you might use a specific translation API if available
                                        # or structure prompts carefully for chat models.

# Ollama Server Configuration
OLLAMA_SERVER_URL = "http://YOUR_OLLAMA_SERVER_IP:11434/api/generate" # Default Ollama API endpoint for generation
OLLAMA_MODEL = "mistral" # Or your preferred model configured in Ollama, e.g., "llama2", "codellama"
                         # Ensure this model is suitable for or can be prompted for translation.

# Audio Configuration (Placeholders - depends on specific hardware and libraries)
# Example: If using a specific I2S microphone and speaker setup
# I2S_MIC_SD_PIN = 32
# I2S_MIC_WS_PIN = 25
# I2S_MIC_SCK_PIN = 33
#
# I2S_SPEAKER_SD_PIN = 26
# I2S_SPEAKER_WS_PIN = 22
# I2S_SPEAKER_SCK_PIN = 21

# STT (Speech-to-Text) Service Configuration (Example: if using a cloud service)
# STT_API_KEY = "YOUR_STT_SERVICE_API_KEY"
# STT_API_URL = "URL_OF_YOUR_STT_SERVICE"

# TTS (Text-to-Speech) Service Configuration (Example: if using a cloud service)
# TTS_API_KEY = "YOUR_TTS_SERVICE_API_KEY"
# TTS_API_URL = "URL_OF_YOUR_TTS_SERVICE"


# --- Helper function to check if essential settings are configured ---
def validate_settings():
    """
    Validates that essential settings are not still using placeholder values.
    In a real application, you might raise an error or prompt the user.
    """
    essential_settings = {
        "WIFI_SSID": WIFI_SSID,
        "WIFI_PASSWORD": WIFI_PASSWORD,
        "OPENAI_API_KEY": OPENAI_API_KEY,
        # Ollama is optional, so we might not make its URL essential for basic startup
        # "OLLAMA_SERVER_URL": OLLAMA_SERVER_URL
    }

    missing_configs = []
    for key, value in essential_settings.items():
        if value.startswith("YOUR_") or value == "":
            missing_configs.append(key)

    if "OPENAI_API_KEY" in missing_configs and not (OLLAMA_SERVER_URL and not OLLAMA_SERVER_URL.startswith("YOUR_")):
        # If no OpenAI key AND no valid Ollama URL, then it's an issue.
        # Or if only OpenAI is intended to be used. For now, let's assume OpenAI is a primary target.
        pass # Decided to just print warnings for now from main.py

    if missing_configs:
        print("WARNING: The following settings in 'settings.py' need to be configured:")
        for item in missing_configs:
            print(f" - {item}")
        return False
    return True

# Example of how to load/notify about settings - could be called from main.py
if __name__ == "__main__":
    print("Loading settings...")
    if validate_settings():
        print("Settings appear to be configured.")
    else:
        print("Please update 'settings.py' with your actual credentials and configurations.")

    print(f"Wi-Fi SSID: {WIFI_SSID}")
    print(f"OpenAI Key (Partial): {OPENAI_API_KEY[:5]}..." if OPENAI_API_KEY != "YOUR_OPENAI_API_KEY" else "Not set")
    print(f"Ollama URL: {OLLAMA_SERVER_URL}")
    print(f"Ollama Model: {OLLAMA_MODEL}")
