```cpp
#include <WiFi.h>
#include <WebServer.h>
#include <BleKeyboard.h>

const char* WIFI_SSID = "1416";
const char* WIFI_PASSWORD = "xingsang";

BleKeyboard bleKeyboard(
  "ESP32 Typewriter",
  "ESP32",
  100
);

WebServer server(80);

volatile bool stopRequested = false;
bool currentlyTyping = false;

int charDelay = 60;

const char MAIN_PAGE[] PROGMEM = R"rawliteral(

<!DOCTYPE html>

<html>

<head>

<meta name="viewport"
content="width=device-width, initial-scale=1">

<title>ESP32 Typewriter</title>

<style>

* {
    box-sizing: border-box;
}

body {
    margin: 0;
    background: #101010;
    color: #eeeeee;
    font-family: Arial, sans-serif;
}

.container {
    max-width: 850px;
    margin: auto;
    padding: 24px;
}

h1 {
    margin-bottom: 5px;
}

.subtitle {
    color: #888;
    margin-bottom: 20px;
}

.status {
    padding: 14px;
    border: 1px solid #444;
    margin-bottom: 15px;
    background: #181818;
    line-height: 1.8;
}

textarea {
    width: 100%;
    min-height: 350px;
    resize: vertical;

    background: #080808;
    color: #ffffff;

    border: 1px solid #555;

    padding: 16px;

    font-family: monospace;
    font-size: 16px;

    outline: none;
}

textarea:focus {
    border-color: #aaa;
}

button {
    width: 100%;
    margin-top: 12px;
    padding: 15px;

    border: none;

    font-size: 17px;
    font-weight: bold;

    cursor: pointer;

    background: #eeeeee;
    color: #111111;
}

button:active {
    transform: scale(0.99);
}

.stop {
    background: #772222;
    color: white;
}

.clear {
    background: #333333;
    color: white;
}

.row {
    display: flex;
    gap: 10px;
}

.row button {
    flex: 1;
}

.speed {
    margin-top: 18px;

    padding: 15px;

    border: 1px solid #444;
    background: #181818;
}

.speed input {
    width: 100%;
}

.speedValue {
    margin-top: 8px;
    color: #aaa;
    font-family: monospace;
}

.message {
    margin-top: 15px;

    padding: 12px;

    border: 1px solid #333;

    background: #181818;

    color: #aaa;
}

</style>

</head>

<body>

<div class="container">

<h1>ESP32 Typewriter</h1>

<div class="subtitle">
Bluetooth HID multiline keyboard
</div>

<div class="status">

Wi-Fi:
<strong id="wifiStatus">
checking...
</strong>

<br>

ESP32 IP:
<strong id="ipAddress">
-
</strong>

<br>

Bluetooth:
<strong id="bleStatus">
checking...
</strong>

<br>

Typing:
<strong id="typingStatus">
NO
</strong>

<br>

Progress:
<strong id="progress">
0 / 0
</strong>

</div>

<textarea
id="text"
placeholder="Type or paste your text here..."></textarea>

<div class="speed">

Typing delay:

<input
type="range"
id="speed"
min="40"
max="150"
value="60"
oninput="updateSpeed()">

<div class="speedValue">

<strong id="speedValue">
60 ms
</strong>
per character

</div>

</div>

<div class="row">

<button onclick="typeText()">
TYPE
</button>

<button
class="stop"
onclick="stopTyping()">
STOP
</button>

<button
class="clear"
onclick="clearText()">
CLEAR
</button>

</div>

<div class="message" id="message">
Ready.
</div>

</div>

<script>

function updateSpeed()
{
    const value =
        document.getElementById("speed").value;

    document.getElementById(
        "speedValue"
    ).innerText =
        value + " ms";
}


function clearText()
{
    document.getElementById(
        "text"
    ).value = "";

    document.getElementById(
        "message"
    ).innerText = "Text cleared.";
}


async function typeText()
{
    const text =
        document.getElementById("text").value;

    if (!text)
    {
        document.getElementById(
            "message"
        ).innerText =
            "Enter some text first.";

        return;
    }

    const speed =
        document.getElementById(
            "speed"
        ).value;

    document.getElementById(
        "message"
    ).innerText =
        "Starting...";

    try
    {
        const response =
            await fetch(
                "/type",
                {
                    method: "POST",

                    headers:
                    {
                        "Content-Type":
                        "application/x-www-form-urlencoded"
                    },

                    body:
                        "speed=" +
                        encodeURIComponent(speed) +
                        "&text=" +
                        encodeURIComponent(text)
                }
            );

        const result =
            await response.text();

        document.getElementById(
            "message"
        ).innerText =
            result;
    }

    catch(error)
    {
        document.getElementById(
            "message"
        ).innerText =
            "Connection error.";
    }
}


async function stopTyping()
{
    try
    {
        const response =
            await fetch(
                "/stop",
                {
                    method: "POST"
                }
            );

        const result =
            await response.text();

        document.getElementById(
            "message"
        ).innerText =
            result;
    }

    catch(error)
    {
        document.getElementById(
            "message"
        ).innerText =
            "Connection error.";
    }
}


async function updateStatus()
{
    try
    {
        const response =
            await fetch("/status");

        const data =
            await response.json();

        document.getElementById(
            "bleStatus"
        ).innerText =
            data.connected
            ? "CONNECTED"
            : "NOT CONNECTED";

        document.getElementById(
            "typingStatus"
        ).innerText =
            data.typing
            ? "YES"
            : "NO";

        document.getElementById(
            "wifiStatus"
        ).innerText =
            data.wifi
            ? "CONNECTED"
            : "DISCONNECTED";

        document.getElementById(
            "ipAddress"
        ).innerText =
            data.ip;

        document.getElementById(
            "progress"
        ).innerText =
            data.progress +
            " / " +
            data.total;
    }

    catch(error)
    {
        document.getElementById(
            "wifiStatus"
        ).innerText =
            "DISCONNECTED";
    }
}


setInterval(
    updateStatus,
    1000
);

updateStatus();

</script>

</body>

</html>

)rawliteral";


String currentText = "";
size_t currentPosition = 0;


void typeCharacter(char c)
{
    if (stopRequested)
        return;

    if (!bleKeyboard.isConnected())
        return;

    if (c == '\n')
    {
        bleKeyboard.write(KEY_RETURN);

        delay(100);

        return;
    }

    if (c == '\r')
    {
        return;
    }

    if (c == '\t')
    {
        bleKeyboard.write(KEY_TAB);

        delay(100);

        return;
    }

    bleKeyboard.write(
        (uint8_t)c
    );

    delay(charDelay);

    if (c == ' ')
    {
        delay(25);
    }

    if (
        c == '.' ||
        c == ',' ||
        c == '!' ||
        c == '?' ||
        c == ':' ||
        c == ';'
    )
    {
        delay(80);
    }
}


void typeText(String text)
{
    if (!bleKeyboard.isConnected())
    {
        Serial.println(
            "BLE keyboard is not connected."
        );

        return;
    }

    currentlyTyping = true;

    stopRequested = false;

    currentText = text;
    currentPosition = 0;

    Serial.println();
    Serial.println(
        "================================"
    );

    Serial.println(
        "STARTING TYPE"
    );

    Serial.println(
        "================================"
    );

    Serial.print(
        "Characters: "
    );

    Serial.println(
        text.length()
    );

    for (
        size_t i = 0;
        i < text.length();
        i++
    )
    {
        currentPosition = i;

        if (stopRequested)
        {
            Serial.println(
                "Typing stopped."
            );

            break;
        }

        if (!bleKeyboard.isConnected())
        {
            Serial.println(
                "BLE disconnected."
            );

            break;
        }

        typeCharacter(
            text[i]
        );

        /*
           Periodic longer pause.

           This reduces sustained BLE traffic
           and makes long text transmission more
           reliable on weaker connections.
        */

        if (
            i > 0 &&
            i % 30 == 0
        )
        {
            delay(180);
        }
    }

    currentPosition = text.length();

    currentlyTyping = false;

    Serial.println(
        "Typing finished."
    );
}


void handleRoot()
{
    server.send(
        200,
        "text/html",
        MAIN_PAGE
    );
}


void handleType()
{
    if (!server.hasArg("text"))
    {
        server.send(
            400,
            "text/plain",
            "No text received."
        );

        return;
    }

    if (!bleKeyboard.isConnected())
    {
        server.send(
            409,
            "text/plain",
            "Bluetooth keyboard is not connected."
        );

        return;
    }

    if (currentlyTyping)
    {
        server.send(
            409,
            "text/plain",
            "Already typing."
        );

        return;
    }

    if (server.hasArg("speed"))
    {
        charDelay =
            server.arg("speed").toInt();

        if (charDelay < 40)
            charDelay = 40;

        if (charDelay > 150)
            charDelay = 150;
    }

    String text =
        server.arg("text");

    server.send(
        200,
        "text/plain",
        "Typing started."
    );

    typeText(text);
}


void handleStop()
{
    stopRequested = true;

    server.send(
        200,
        "text/plain",
        "Stop requested."
    );

    Serial.println(
        "STOP requested."
    );
}


void handleStatus()
{
    String json = "{";

    json += "\"connected\":";
    json +=
        bleKeyboard.isConnected()
        ? "true"
        : "false";

    json += ",";

    json += "\"typing\":";
    json +=
        currentlyTyping
        ? "true"
        : "false";

    json += ",";

    json += "\"wifi\":";
    json +=
        WiFi.status() == WL_CONNECTED
        ? "true"
        : "false";

    json += ",";

    json += "\"ip\":\"";
    json +=
        WiFi.localIP().toString();
    json += "\"";

    json += ",";

    json += "\"progress\":";
    json += currentPosition;

    json += ",";

    json += "\"total\":";
    json += currentText.length();

    json += "}";

    server.send(
        200,
        "application/json",
        json
    );
}


void setup()
{
    Serial.begin(115200);

    delay(1000);

    Serial.println();
    Serial.println(
        "================================"
    );

    Serial.println(
        "ESP32 BLUETOOTH TYPEWRITER"
    );

    Serial.println(
        "================================"
    );

    WiFi.mode(WIFI_STA);

    WiFi.begin(
        WIFI_SSID,
        WIFI_PASSWORD
    );

    Serial.println();
    Serial.print(
        "Connecting to phone hotspot"
    );

    int attempts = 0;

    while (
        WiFi.status() != WL_CONNECTED &&
        attempts < 40
    )
    {
        delay(500);

        Serial.print(".");

        attempts++;
    }

    Serial.println();

    if (
        WiFi.status() == WL_CONNECTED
    )
    {
        Serial.println(
            "Wi-Fi connected!"
        );

        Serial.print(
            "Network: "
        );

        Serial.println(
            WIFI_SSID
        );

        Serial.print(
            "ESP32 IP: "
        );

        Serial.println(
            WiFi.localIP()
        );

        Serial.print(
            "Gateway: "
        );

        Serial.println(
            WiFi.gatewayIP()
        );

        Serial.print(
            "RSSI: "
        );

        Serial.println(
            WiFi.RSSI()
        );
    }
    else
    {
        Serial.println(
            "Wi-Fi connection failed."
        );
    }

    bleKeyboard.begin();

    Serial.println();

    Serial.println(
        "Bluetooth keyboard started."
    );

    Serial.println(
        "Pair with: ESP32 Typewriter"
    );

    server.on(
        "/",
        HTTP_GET,
        handleRoot
    );

    server.on(
        "/type",
        HTTP_POST,
        handleType
    );

    server.on(
        "/stop",
        HTTP_POST,
        handleStop
    );

    server.on(
        "/status",
        HTTP_GET,
        handleStatus
    );

    server.begin();

    Serial.println();

    Serial.println(
        "HTTP server started."
    );

    if (
        WiFi.status() == WL_CONNECTED
    )
    {
        Serial.print(
            "Open: http://"
        );

        Serial.println(
            WiFi.localIP()
        );
    }

    Serial.println(
        "================================"
    );
}


void loop()
{
    server.handleClient();

    static unsigned long lastWiFiCheck = 0;

    if (
        millis() - lastWiFiCheck > 5000
    )
    {
        lastWiFiCheck = millis();

        if (
            WiFi.status() != WL_CONNECTED
        )
        {
            Serial.println(
                "Wi-Fi disconnected. Reconnecting..."
            );

            WiFi.disconnect();

            WiFi.begin(
                WIFI_SSID,
                WIFI_PASSWORD
            );
        }
    }

    delay(2);
}
```
