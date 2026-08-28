#include <Wire.h>

#define MUX_ADDR 0x70
#define AS5600_ADDR 0x36
#define N_CH 7
#define SDA_PIN 18
#define SCL_PIN 19
#define DEADMAN_PIN 23
#define SAMPLE_HZ 100

#define REG_STATUS 0x0B
#define REG_RAW_ANGLE 0x0C

static uint32_t sequenceNumber = 0;

bool muxSelect(uint8_t channel) {
  if (channel >= 8) return false;
  Wire.beginTransmission(MUX_ADDR);
  Wire.write(1 << channel);
  return Wire.endTransmission() == 0;
}

void muxDisableAll() {
  Wire.beginTransmission(MUX_ADDR);
  Wire.write(0x00);
  Wire.endTransmission();
}

int16_t readRawAngle() {
  Wire.beginTransmission(AS5600_ADDR);
  Wire.write(REG_RAW_ANGLE);
  if (Wire.endTransmission(false) != 0) return -1;
  if (Wire.requestFrom(AS5600_ADDR, 2) != 2) return -1;
  const uint8_t highByte = Wire.read();
  const uint8_t lowByte = Wire.read();
  return ((highByte << 8) | lowByte) & 0x0FFF;
}

uint8_t readStatus() {
  Wire.beginTransmission(AS5600_ADDR);
  Wire.write(REG_STATUS);
  if (Wire.endTransmission(false) != 0) return 0;
  if (Wire.requestFrom(AS5600_ADDR, 1) != 1) return 0;
  return Wire.read();
}

void diagnose() {
  Serial.println("# YAM seven-channel encoder scan");
  for (uint8_t channel = 0; channel < N_CH; channel++) {
    if (!muxSelect(channel)) {
      Serial.printf("# ch%u: mux not responding at 0x%02X\n", channel, MUX_ADDR);
      continue;
    }

    Wire.beginTransmission(AS5600_ADDR);
    if (Wire.endTransmission() != 0) {
      Serial.printf("# ch%u: no AS5600 -- check wiring and power\n", channel);
      continue;
    }

    const uint8_t status = readStatus();
    const char *magnet = (status & 0x20) ? "ok"
                         : (status & 0x10) ? "too weak / too far"
                         : (status & 0x08) ? "too strong / too close"
                                           : "not detected";
    Serial.printf("# ch%u: AS5600 found, magnet %s, raw %d\n", channel,
                  magnet, readRawAngle());
  }
  muxDisableAll();
  Serial.println("# scan done");
}

void setup() {
  Serial.begin(115200);
  pinMode(DEADMAN_PIN, INPUT_PULLUP);
  Wire.begin(SDA_PIN, SCL_PIN);
  Wire.setClock(400000);
  delay(300);
  diagnose();
}

void loop() {
  static uint32_t nextSampleMicros = 0;
  const uint32_t periodMicros = 1000000UL / SAMPLE_HZ;
  const uint32_t nowMicros = micros();
  if (static_cast<int32_t>(nowMicros - nextSampleMicros) < 0) return;
  nextSampleMicros += periodMicros;
  if (static_cast<int32_t>(nowMicros - nextSampleMicros) >= 0) {
    nextSampleMicros = nowMicros + periodMicros;
  }

  int16_t angles[N_CH];
  for (uint8_t channel = 0; channel < N_CH; channel++) {
    angles[channel] = muxSelect(channel) ? readRawAngle() : -1;
  }

  // Versioned output lets the host reject controller reboots and stale data:
  // YAM1,sequence,millis,count0,...,count6,deadman
  Serial.print("YAM1,");
  Serial.print(sequenceNumber++);
  Serial.print(',');
  Serial.print(millis());
  for (uint8_t channel = 0; channel < N_CH; channel++) {
    Serial.print(',');
    Serial.print(angles[channel]);
  }
  Serial.print(',');
  Serial.println(digitalRead(DEADMAN_PIN) == LOW ? 1 : 0);
}
