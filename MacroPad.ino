#include <TFT_eSPI.h>
#include <SPI.h>
#include "WiFi.h"
#include <Wire.h>
#include "Button2.h"
#include <esp_adc_cal.h>
#include "bmp.h"
#include <esp_sleep.h>

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

int columns[4] = {COLUMN_1, COLUMN_2, COLUMN_3, COLUMN_4};
int rows[3] = {ROW_1, ROW_2, ROW_3};

//array of each keys state and the time that it was pressed (for debounce calculations)
int keyStates[3][4][2] = {
  { {0, 0}, {0, 0}, {0, 0}, {0, 0} }, // Row 0
  { {0, 0}, {0, 0}, {0, 0}, {0, 0} }, // Row 1
  { {0, 0}, {0, 0}, {0, 0}, {0, 0} }  // Row 2
};

int Columns = 4;
int Rows = 3;
int iteration = 0;
int debounceDelay = 50;

TFT_eSPI tft = TFT_eSPI(135, 240); // Invoke custom library

void setup() {
  Serial.begin(115200);
  Serial.println("Start");
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

  // Set pin modes
  for (int i = 0; i < Columns; i++) {
    pinMode(columns[i], OUTPUT);
    digitalWrite(columns[i], LOW); // default low
  }
  for (int j = 0; j < Rows; j++) {
    pinMode(rows[j], INPUT);
  }

  //checkKey();
  //printState();
}

void loop() {
  checkKey();
  printState();
  //delay(100); // reduce flickering
}

void checkKey() {
  //iterate through each column
  for (int i = 0; i < Columns; i++) {
    digitalWrite(columns[3-i], HIGH); // pull column high
    delay(75);

    //iterate through each row
    for (int j = 0; j < Rows; j++) {
      //check each row and debounce logic
      int currentState = keyStates[j][3-i][0]; // last known stable state
      int newState = digitalRead(rows[j]); // New state
      //Serial.println(currentState); // debug
      //Serial.println(newState); // debug

      if (newState != currentState && (millis() - keyStates[j][3-i][1]) > debounceDelay) {
        keyStates[j][3-i][1] = millis(); // reset debounce timer on state change
        keyStates[j][3-i][0] = newState;
        //Serial.println("pressed"); // debug
      }
    }

    digitalWrite(columns[3-i], LOW); // pull column low
  }
}

void printState() {
  for (int i = 0; i < Rows; i++) {
    //Serial.print("column: "); // debug
    //Serial.println(i); // debug

    for (int j = 0; j < Columns; j++) {
      //Serial.print("row: "); // debug
      //Serial.println(j); // debug

      //Serial.print("[");
      Serial.print(keyStates[i][j][0]);
      //Serial.print(",");
      //Serial.print(keyStates[i][j][1]);
      //Serial.print("]");
    }
    Serial.println();
  }
  Serial.println("");
  delay(1000);

   // debug
  Serial.print("iteration");
  Serial.println(iteration);
  iteration++;
}