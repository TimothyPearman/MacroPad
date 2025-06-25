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

TFT_eSPI tft = TFT_eSPI(135, 240); // Invoke custom library

void setup() {
  Serial.begin(115200);
  Serial.println("Start");

  tft.init();
  tft.setSwapBytes(true);
  tft.setRotation(2);
  tft.fillScreen(TFT_BLACK);
  tft.setTextSize(1);
  tft.setTextColor(TFT_GREEN);
  tft.setCursor(0, 0);
  tft.setTextDatum(TC_DATUM);
  tft.drawString("Timmy's MacroPad",tft.width() / 2, 0);

  pinMode(COLUMN_1, OUTPUT);
  pinMode(COLUMN_2, OUTPUT);
  pinMode(COLUMN_3, OUTPUT);
  pinMode(COLUMN_4, OUTPUT);
  pinMode(ROW_1, INPUT);
  pinMode(ROW_2, INPUT);
  pinMode(ROW_3, INPUT);

  digitalWrite(COLUMN_1, HIGH);
  //digitalWrite(COLUMN_2, HIGH);
  //digitalWrite(COLUMN_3, HIGH);
  //digitalWrite(COLUMN_4, HIGH);
}

void loop() {
  //check buttons pressed

  Serial.println(digitalRead(ROW_1));
  //if (digitalRead(ROW_1) =)

  //digitalRead(ROW_1);
  //digitalRead(ROW_2);
  //digitalRead(ROW_3);
  //digitalRead(ROW_4);
}
