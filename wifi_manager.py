# wifi_manager.py
# Handles Wi-Fi connectivity for the ESP32.

import network
import time
import settings # To get Wi-Fi credentials

# Global variable to hold the station interface
sta_if = None

def connect_wifi(ssid=None, password=None, retries=5, retry_delay_s=5):
    """
    Connects the ESP32 to a Wi-Fi network.

    Args:
        ssid (str, optional): Wi-Fi SSID. Defaults to settings.WIFI_SSID.
        password (str, optional): Wi-Fi Password. Defaults to settings.WIFI_PASSWORD.
        retries (int): Number of times to attempt connection.
        retry_delay_s (int): Delay in seconds between retries.

    Returns:
        bool: True if connected, False otherwise.
    """
    global sta_if

    _ssid = ssid if ssid is not None else settings.WIFI_SSID
    _password = password if password is not None else settings.WIFI_PASSWORD

    if not _ssid or _ssid == "YOUR_WIFI_SSID":
        print("Error: Wi-Fi SSID not configured in settings.py.")
        return False

    # Initialize the station interface if not already done
    if sta_if is None:
        sta_if = network.WLAN(network.STA_IF)

    if not sta_if.active():
        print("Activating Wi-Fi station interface...")
        sta_if.active(True)
        time.sleep(1) # Give it a moment to activate

    if sta_if.isconnected():
        print(f"Already connected to Wi-Fi: {sta_if.ifconfig()[0]}")
        return True

    print(f"Attempting to connect to Wi-Fi SSID: '{_ssid}'...")

    for attempt in range(retries):
        try:
            sta_if.connect(_ssid, _password)

            # Wait for connection
            connect_timeout_s = 15
            start_time = time.time()
            while not sta_if.isconnected() and (time.time() - start_time) < connect_timeout_s:
                print(f"Connection attempt {attempt + 1}/{retries}: Checking status... (Remaining: {connect_timeout_s - (time.time() - start_time):.0f}s)")
                time.sleep(1)

            if sta_if.isconnected():
                print("\nWi-Fi Connected!")
                print(f"IP Address: {sta_if.ifconfig()[0]}")
                return True
            else:
                print(f"Connection attempt {attempt + 1} failed. Timeout or incorrect credentials.")
                sta_if.disconnect() # Explicitly disconnect before retrying
                time.sleep(0.5) # Short delay after disconnect
                if sta_if.active(): # Ensure it's active for next attempt
                    pass
                else: # Reactivate if it became inactive
                    sta_if.active(True)
                    time.sleep(0.5)


        except OSError as e:
            print(f"Error during Wi-Fi connection (attempt {attempt + 1}): {e}")
            # Common errors:
            #  - OSError: 2 (No such file or directory) - can happen if WiFi drivers fail
            #  - OSError: 12 (Out of memory) - if network stack uses too much memory
            #  - Other network related OS errors
            # Consider deactivating and reactivating the interface on certain errors
            sta_if.active(False)
            time.sleep(0.5)
            sta_if.active(True)
            time.sleep(0.5)


        if attempt < retries - 1:
            print(f"Retrying in {retry_delay_s} seconds...")
            time.sleep(retry_delay_s)
        else: # Last attempt failed
            if not sta_if.isconnected(): # Double check status after loop
                 print("Failed to connect to Wi-Fi after all retries.")
                 sta_if.active(False) # Deactivate to save power potentially
                 return False
            else: # Connected in the very last moment (unlikely given the loop structure, but good to check)
                print("\nWi-Fi Connected! (on very last check)")
                print(f"IP Address: {sta_if.ifconfig()[0]}")
                return True

    return False # Should be covered by the loop logic

def is_wifi_connected():
    """Checks if Wi-Fi is currently connected."""
    global sta_if
    if sta_if and sta_if.isconnected():
        return True
    return False

def get_ip_address():
    """Returns the current IP address if connected, otherwise None."""
    if is_wifi_connected():
        return sta_if.ifconfig()[0]
    return None

def disconnect_wifi():
    """Disconnects from Wi-Fi and deactivates the interface."""
    global sta_if
    if sta_if and sta_if.active():
        if sta_if.isconnected():
            print("Disconnecting from Wi-Fi...")
            sta_if.disconnect()
        # Wait for disconnection
        disconnect_wait_s = 5
        start_time = time.time()
        while sta_if.isconnected() and (time.time() - start_time) < disconnect_wait_s:
            time.sleep(0.1)

        if not sta_if.isconnected():
            print("Wi-Fi disconnected.")
        else:
            print("Wi-Fi still shows as connected after disconnect attempt.")

        print("Deactivating Wi-Fi station interface.")
        sta_if.active(False)
        # sta_if = None # Optionally reset the global if you want to re-init completely next time
        return True
    print("Wi-Fi interface not active or not initialized.")
    return False

# Example usage:
if __name__ == "__main__":
    print("Testing Wi-Fi Manager...")

    if settings.WIFI_SSID == "YOUR_WIFI_SSID" or settings.WIFI_PASSWORD == "YOUR_WIFI_PASSWORD":
        print("\nPlease configure your Wi-Fi SSID and Password in settings.py to run this test.")
    else:
        print(f"Attempting to connect to SSID: {settings.WIFI_SSID}")
        if connect_wifi():
            print(f"\nSuccessfully connected. IP: {get_ip_address()}")

            print("\nWaiting for 10 seconds before disconnecting...")
            time.sleep(10)

            disconnect_wifi()
            print(f"Is connected now? {is_wifi_connected()}")
        else:
            print("\nFailed to connect to Wi-Fi.")

    print("\nWi-Fi Manager test finished.")
