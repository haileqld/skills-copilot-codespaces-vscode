# ESP32 Voice Translation Bot

This project is a MicroPython application for ESP32 that acts as a voice-controlled translation bot. It can:
- Listen to user's voice input (simulated in the current version).
- Convert speech to text (simulated, with placeholders for cloud STT services).
- Connect to OpenAI API or a local Ollama server to perform text translation.
- Convert the translated text back to speech and play it to the user (simulated, with placeholders for cloud TTS services).

The primary use case is to get translations of spoken phrases.

## Features

- **Dual AI Service Support:**
    - OpenAI: Utilizes OpenAI's models (e.g., GPT series for chat-based translation).
    - Ollama: Connects to a self-hosted Ollama instance running LLMs locally.
- **Wi-Fi Connectivity:** Connects to your local Wi-Fi network for internet access.
- **Modular Design:** Code is organized into modules for settings, Wi-Fi, API clients, and audio handling.
- **Configurable:** API keys, Wi-Fi credentials, and server details are managed in `settings.py`.
- **Placeholder Audio:** Current audio input (STT) and output (TTS) are simulated. Hooks are in place for integration with actual microphone/speaker hardware and cloud-based STT/TTS services.

## Project Structure

```
.
├── main.py               # Main application script
├── settings.py           # Configuration (API keys, Wi-Fi creds - MUST BE EDITED)
├── wifi_manager.py       # Handles Wi-Fi connection
├── openai_client.py      # Client for OpenAI API
├── ollama_client.py      # Client for Ollama server API
├── audio_input.py        # Handles audio recording and STT (currently simulated)
├── audio_output.py       # Handles TTS and audio playback (currently simulated)
├── requirements.txt      # Lists MicroPython libraries needed
└── README.md             # This file
```

## Hardware Requirements (for full functionality)

- ESP32 development board.
- Microphone (e.g., I2S microphone like INMP441 or an analog microphone).
- Speaker and amplifier (e.g., I2S amplifier like MAX98357A or a DAC output with an amplifier).
- Internet access via Wi-Fi.

**Note:** The current code primarily uses placeholders for audio hardware interaction. Actual hardware integration would require uncommenting and completing the I2S/ADC/DAC sections in `audio_input.py` and `audio_output.py` and matching them to your specific hardware.

## Software Requirements

- MicroPython firmware flashed onto the ESP32.
- Required MicroPython libraries (see `requirements.txt`):
    - `urequests`: For HTTP API calls.
    - `ujson`: For JSON processing.
    (These may need to be manually uploaded to the ESP32 if not built into your firmware.)

## Setup Instructions

1.  **Clone the Repository (or download the files):**
    Get all the project files onto your computer.

2.  **Install MicroPython Firmware:**
    If you haven't already, flash your ESP32 with the latest version of MicroPython.

3.  **Configure Settings (`settings.py`):**
    Open `settings.py` and update the following values:
    - `WIFI_SSID`: Your Wi-Fi network name.
    - `WIFI_PASSWORD`: Your Wi-Fi network password.
    - `OPENAI_API_KEY`: Your OpenAI API key (if you plan to use OpenAI).
        - Ensure `OPENAI_API_URL` and `OPENAI_TRANSLATE_MODEL` are appropriate for your needs. The default is set for chat completions.
    - `OLLAMA_SERVER_URL`: The full URL to your Ollama server's `/api/generate` endpoint (e.g., `http://your_ollama_server_ip:11434/api/generate`).
        - Set `OLLAMA_MODEL` to the name of the model you want to use with Ollama (e.g., `mistral`, `llama2`). Ensure this model is available on your Ollama server.
    - **(Optional) STT/TTS Service Configuration:** If/when you integrate real STT/TTS services, update their respective API key and URL placeholders in `settings.py`.
    - **(Optional) Audio Hardware Pins:** If/when integrating real audio hardware, update the I2S/ADC pin configurations in `settings.py` (currently commented out) and ensure `audio_input.py` and `audio_output.py` use them.

4.  **Upload Files to ESP32:**
    Use a tool like `ampy`, `rshell`, or Thonny IDE to upload all the Python files (`.py`) and the `requirements.txt` (for reference) to the root directory of your ESP32's filesystem.
    - **Libraries:** If `urequests` or `ujson` are not built into your firmware, download their `.py` files (e.g., from [micropython-lib](https://github.com/micropython/micropython-lib)) and upload them to the `/lib` directory on your ESP32 (create `/lib` if it doesn't exist) or to the root.

5.  **Install Dependencies (if needed using `mip`):**
    If your MicroPython firmware supports `mip` (MicroPython Package Manager), you can install dependencies directly on the device via the REPL:
    ```python
    import mip
    mip.install("urequests")
    # mip.install("ujson") # ujson is often built-in
    ```

## Running the Application

1.  **Connect to ESP32:**
    Connect to your ESP32's REPL (e.g., via Thonny, `rshell`, or `screen`/`picocom`).

2.  **Run `main.py`:**
    In the REPL, import and run the main script:
    ```python
    import main
    ```
    Alternatively, if `main.py` is present, many ESP32 boards will run it automatically on boot/reset.

3.  **Interact with the Bot:**
    - The application will initialize, connect to Wi-Fi, and then start its main loop.
    - It will (currently, through simulation in `audio_input.py`) "listen" for a command. The default simulated command is "translate 'hello world' to Spanish".
    - It will then attempt to translate this using OpenAI (if configured) and then Ollama (if configured).
    - The translated text will be "spoken" (simulated by printing to console and simulated audio delay in `audio_output.py`).
    - The main loop currently runs for a fixed number of interactions (2 by default).

## How it Works (Current Simulated Flow)

1.  `main.py` starts, initializes modules.
2.  `wifi_manager.py` connects to the configured Wi-Fi.
3.  `audio_input.init_microphone()` and `audio_output.init_speaker()` are called (placeholders).
4.  The main loop begins:
    a.  `audio_input.record_and_transcribe_audio()` is called. This function currently:
        i.  Simulates recording audio for a few seconds.
        ii. Simulates sending this (non-existent) audio to an STT service.
        iii.Returns a hardcoded text string (e.g., "translate 'hello world' to Spanish").
    b.  The received text is parsed by `main.py` to extract the text to translate and target language.
    c.  The application tries the OpenAI service:
        i.  `openai_client.translate_text()` sends the prompt to the OpenAI API.
        ii. The API response (translation) is received.
    d.  The application then tries the Ollama service:
        i.  `ollama_client.translate_text()` sends the prompt to your Ollama server.
        ii. The API response (translation) is received.
    e.  `audio_output.speak_text()` is called for each translation. This function currently:
        i.  Simulates calling a TTS service to get audio data.
        ii. Simulates playing this (non-existent) audio data with appropriate delays.
5.  After a couple of interactions, the loop ends, and cleanup functions are called.

## Future Enhancements / To-Do

- **Real Audio Input (STT):**
    - Implement actual I2S/ADC microphone reading in `audio_input.py`.
    - Integrate with a cloud STT service (e.g., OpenAI Whisper API, Google Cloud STT). This will involve handling audio formats and multipart POST requests for audio data.
- **Real Audio Output (TTS):**
    - Implement actual I2S/DAC speaker output in `audio_output.py`.
    - Integrate with a cloud TTS service (e.g., OpenAI TTS API, Google Cloud TTS, Piper). This involves fetching audio data (PCM/MP3) and playing it, possibly streaming for longer audio.
- **User Choice of Service:** Allow the user to select OpenAI or Ollama via a button or voice command.
- **More Robust Command Parsing:** Improve the parsing of voice commands to handle more variations and languages.
- **Error Indication:** Use onboard LEDs for status and error indication.
- **Configuration Mode:** Implement a way to configure Wi-Fi credentials if the initial connection fails (e.g., by starting an Access Point).
- **On-Device Models (Advanced):** Explore lightweight, on-device STT/TTS solutions if feasible for simple commands, reducing cloud dependency (challenging on ESP32).

## Troubleshooting

- **Wi-Fi Connection Issues:**
    - Double-check `WIFI_SSID` and `WIFI_PASSWORD` in `settings.py`.
    - Ensure your ESP32 has good Wi-Fi signal.
    - Check the serial output for error messages from `wifi_manager.py`.
- **API Errors (OpenAI/Ollama):**
    - Verify your `OPENAI_API_KEY` is correct and has credits/access.
    - Ensure your `OLLAMA_SERVER_URL` is correct, the server is running, and the specified model is available on the Ollama server.
    - Check the console output for specific error messages from the API clients.
- **"ModuleNotFoundError":** If you see errors like `ModuleNotFoundError: no module named 'urequests'`, you need to upload the missing library to your ESP32 (see Setup section).
- **Audio Issues (with real hardware):** This will require careful debugging of I2S/ADC/DAC connections, driver code, and audio data formats.

Contributions and suggestions are welcome!
```
