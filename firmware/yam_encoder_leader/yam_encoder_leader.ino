// No-solder YAM leader: seven factory-wired B10K potentiometers on a Nano
// I/O sensor shield.  Compatible with the classic ATmega328P Arduino Nano.

#define N_CH 7
#define GRIPPER_CH 6
#define SAMPLE_HZ 100
#define ADC_MIN_VALID 3
#define ADC_MAX_VALID 1020
#define DEADMAN_COUNTS 25

const uint8_t POT_PINS[N_CH] = {A0, A1, A2, A3, A4, A5, A6};

static uint32_t sequenceNumber = 0;
static int16_t releasedGripper = 0;

int16_t readPot(uint8_t channel) {
  uint16_t total = 0;
  for (uint8_t sample = 0; sample < 4; sample++) {
    total += analogRead(POT_PINS[channel]);
  }
  const int16_t value = (total + 2) / 4;
  if (value <= ADC_MIN_VALID || value >= ADC_MAX_VALID) return -1;
  return value;
}

int16_t captureReleasedGripper() {
  uint32_t total = 0;
  uint8_t validSamples = 0;
  for (uint8_t sample = 0; sample < 64; sample++) {
    const int16_t value = readPot(GRIPPER_CH);
    if (value >= 0) {
      total += value;
      validSamples++;
    }
    delay(5);
  }
  return validSamples == 0 ? -1 : total / validSamples;
}

void diagnose() {
  Serial.println(F("# YAM seven-channel potentiometer scan"));
  for (uint8_t channel = 0; channel < N_CH; channel++) {
    Serial.print(F("# ch"));
    Serial.print(channel);
    Serial.print(F(": raw "));
    Serial.println(readPot(channel));
  }
  Serial.print(F("# released gripper baseline: "));
  Serial.println(releasedGripper);
  Serial.println(F("# squeeze gripper to enable commands"));
}

void setup() {
  Serial.begin(115200);
  analogReference(DEFAULT);
  delay(1200);
  // Keep the gripper fully released while the controller starts.  Its printed
  // flexure provides the return action, so no button or extra wire is needed.
  releasedGripper = captureReleasedGripper();
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

  int16_t counts[N_CH];
  bool allValid = releasedGripper >= 0;
  for (uint8_t channel = 0; channel < N_CH; channel++) {
    counts[channel] = readPot(channel);
    if (counts[channel] < 0) allValid = false;
  }
  const bool gripperSqueezed =
      counts[GRIPPER_CH] >= 0 &&
      abs(counts[GRIPPER_CH] - releasedGripper) >= DEADMAN_COUNTS;

  // Versioned output lets the host reject controller reboots and stale data:
  // YAMP1,sequence,millis,count0,...,count6,deadman
  Serial.print(F("YAMP1,"));
  Serial.print(sequenceNumber++);
  Serial.print(',');
  Serial.print(millis());
  for (uint8_t channel = 0; channel < N_CH; channel++) {
    Serial.print(',');
    Serial.print(counts[channel]);
  }
  Serial.print(',');
  Serial.println(allValid && gripperSqueezed ? 1 : 0);
}
