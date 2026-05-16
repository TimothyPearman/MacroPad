#include <TFT_eSPI.h>
#include <SPI.h>
#include "WiFi.h"
#include <Wire.h>
//#include "Button2.h"
#include <esp_adc_cal.h>
//#include "bmp.h"
#include <esp_sleep.h>

// define TFT display pins
#define TFT_MOSI   19
#define TFT_SCLK   18
#define TFT_CS     5
#define TFT_DC     16
#define TFT_RST    23
#define TFT_BL     4   // Display backlight control pin

// define the switch matrix identifiers
#define COLUMN_1   33
#define COLUMN_2   25
#define COLUMN_3   26
#define COLUMN_4   27
#define ROW_1      38
#define ROW_2      37
#define ROW_3      36

// define system constants
#define BAUD_RATE 115200
#define SCREEN_WIDTH 135
#define SCREEN_HEIGHT 240
#define COLUMNS 4
#define ROWS 3
#define DEBOUNCE_DELAY 50

// define logic constants
#define COLUMN_SCAN_DELAY 5
#define DISPLAY_REFRESH_INTERVAL 100

// Global state
volatile boolean stateChanged = false;
volatile boolean connected = false;
int iteration = 0;
portMUX_TYPE keyMux = portMUX_INITIALIZER_UNLOCKED; // mutex for synchronizing access to key state variables

const char *HANDSHAKE_REQUEST = "HELLO ARDUINO";
const char *HANDSHAKE_RESPONSE = "HELLO PYTHON";

//arrays of column and row pins for easy iteration
int columns[COLUMNS] = {COLUMN_1, COLUMN_2, COLUMN_3, COLUMN_4};
int rows[ROWS] = {ROW_1, ROW_2, ROW_3};

//array of the current stable state of each key (0 or 1)
int keyStates[ROWS][COLUMNS] = {
  {0, 0, 0, 0}, // Row 0
  {0, 0, 0, 0}, // Row 1
  {0, 0, 0, 0}  // Row 2
};

//array of the last time each key changed state for debounce calculations
unsigned long keyTimes[ROWS][COLUMNS] = {
  {0, 0, 0, 0},
  {0, 0, 0, 0},
  {0, 0, 0, 0}
};


// Initialize TFT display
TFT_eSPI tft = TFT_eSPI(SCREEN_WIDTH, SCREEN_HEIGHT); // Invoke custom library

// Function prototypes
void scanTask(void *parameter);
void displayTask(void *parameter);
void serialTask(void *parameter);
void updateScreen();
void handleSerialInput();

void setup() {
  Serial.begin(BAUD_RATE);
  delay(1000);

  tft.init();
  tft.setSwapBytes(true);
  tft.setRotation(3);
  tft.fillScreen(TFT_BLACK);
  tft.setTextSize(2);
  tft.setTextColor(TFT_MAGENTA);
  tft.setCursor(0, 0);
  tft.setTextDatum(TC_DATUM);
  tft.drawString("Timmy's MacroPad", tft.width()/2, 0);
  tft.drawString("UwU", tft.width()/2, 0 + 30);
  tft.drawString("version 4", tft.width()/2, 0 + 60);

  // Set pin modes
  for (int i = 0; i < COLUMNS; i++) {
    pinMode(columns[i], OUTPUT);
    digitalWrite(columns[i], LOW); // default low
  }
  for (int j = 0; j < ROWS; j++) {
    pinMode(rows[j], INPUT);
  }

  xTaskCreatePinnedToCore(scanTask, "ScanTask", 4096, NULL, 2, NULL, 0);
  xTaskCreatePinnedToCore(displayTask, "DisplayTask", 4096, NULL, 1, NULL, 1);
  xTaskCreatePinnedToCore(serialTask, "SerialTask", 2048, NULL, 1, NULL, 1);
}

void loop() {
  vTaskDelay(portMAX_DELAY);
}

void scanKeyMatrix() {
  //iterate through each column
  for (int i = 0; i < COLUMNS; i++) {
    //scan columns in order and delay between column scans to prevent ghosting
    digitalWrite(columns[i], HIGH); // pull column high
    delay(COLUMN_SCAN_DELAY);

    //iterate through each row
    for (int j = 0; j < ROWS; j++) {
      //read the current stable state and new scanned state of the key
      int currentState = keyStates[j][i]; // last known stable state
      int newState = digitalRead(rows[j]); // new scanned state


      if (newState != currentState && (millis() - keyTimes[j][i]) > DEBOUNCE_DELAY) {
        portENTER_CRITICAL(&keyMux); // ensure atomic access to state variables
        keyTimes[j][i] = millis(); // reset debounce timer on state change
        keyStates[j][i] = newState; // update stable state to new state
        stateChanged = true;
        portEXIT_CRITICAL(&keyMux); // release access to state variables
      }
    }

    digitalWrite(columns[i], LOW); // drop column low
  }
}

void sendButtonState() {
  // Take a snapshot of the current key states for consistent serial output
  int snapshot[ROWS][COLUMNS];

  portENTER_CRITICAL(&keyMux); // ensure atomic access to stateChanged variable
  // Copy current key states to snapshot
  for (int i = 0; i < ROWS; i++) {
    for (int j = 0; j < COLUMNS; j++) {
      snapshot[i][j] = keyStates[i][j];
    }
  }
  portEXIT_CRITICAL(&keyMux); // release access

  // print the snapshot to serial for debugging
  for (int i = 0; i < ROWS; i++) {
    for (int j = 0; j < COLUMNS; j++) {
      Serial.print(snapshot[i][j]);
    }
  }

  Serial.println("");
}

void scanTask(void *parameter) {
  while (true) {
    if (!connected) {
      vTaskDelay(pdMS_TO_TICKS(50));
      continue;
    }

    // Scan the key matrix and update state variables
    scanKeyMatrix();
    bool shouldSend = false;

    portENTER_CRITICAL(&keyMux); // ensure atomic access to stateChanged variable
    // Check if state has changed and set flag to send button state if so
    if (stateChanged) {
      stateChanged = false;
      shouldSend = true;
    }
    portEXIT_CRITICAL(&keyMux); // release access

    // Only send button state if it has changed to reduce unnecessary serial communication
    if (shouldSend) {
      sendButtonState();
    }

    // Short delay to yield to other tasks and prevent watchdog resets
    vTaskDelay(pdMS_TO_TICKS(1));
  }
}

void displayTask(void *parameter) {
  bool wasConnected = false;

  while (true) {
    if (!connected) {
      if (wasConnected) {
        wasConnected = false;
      }

      tft.fillScreen(TFT_BLACK);
      tft.setTextSize(2);
      tft.setTextColor(TFT_RED);
      tft.setCursor(0, 40);
      tft.print("Not connected");
      vTaskDelay(pdMS_TO_TICKS(250));
      continue;
    }

    if (!wasConnected) {
      tft.fillScreen(TFT_BLACK);
      wasConnected = true;
    }

    updateScreen();

    // Delay to control display refresh rate and yield to other tasks
    vTaskDelay(pdMS_TO_TICKS(DISPLAY_REFRESH_INTERVAL));
  }
}

void serialTask(void *parameter) {
  while (true) {
    handleSerialInput();
    vTaskDelay(pdMS_TO_TICKS(5));
  }
}

void handleSerialInput() {
  static String incoming = "";

  while (Serial.available() > 0) {
    char incomingChar = (char)Serial.read();

    if (incomingChar == '\n') {
      incoming.trim();

      if (incoming == HANDSHAKE_REQUEST) {
        Serial.println(HANDSHAKE_RESPONSE);
        connected = true;
      }

      incoming = "";
    } else if (incomingChar != '\r') {
      incoming += incomingChar;
    }
  }
}

void updateScreen() {
  int snapshot[ROWS][COLUMNS];

  portENTER_CRITICAL(&keyMux);
  for (int i = 0; i < ROWS; i++) {
    for (int j = 0; j < COLUMNS; j++) {
      snapshot[i][j] = keyStates[i][j];
    }
  }
  portEXIT_CRITICAL(&keyMux);

  tft.fillRect(0, 90, tft.width(), 140, TFT_BLACK);
  tft.setCursor(0, 90);
  tft.setTextColor(TFT_MAGENTA);
  tft.print("Keys: ");

  for (int i = 0; i < ROWS; i++) {
    for (int j = 0; j < COLUMNS; j++) {
      tft.print(snapshot[i][j]);
    }
  }

  tft.setCursor(0, 120);
  tft.print("Millis: ");
  tft.print(millis());
}
