/*
  TFmini-S Basic Verification Sketch (Arduino C++)
  
  Wiring:
    - LiDAR TX -> Board RX pin (e.g., board.RX)
    - LiDAR RX -> Board TX pin (e.g., board.TX)
    - LiDAR 5V -> 5V Power Source
    - LiDAR GND -> Ground (GND)
*/

#define LIDAR_BAUD 115200

void setup() {
  // Serial monitor for viewing output on computer
  Serial.begin(115200);
  while (!Serial) {
    delay(10);
  }
  
  // Initialize hardware serial for the LiDAR sensor
  Serial1.begin(LIDAR_BAUD);
  Serial.println("TFmini-S Sensor Verification Initialized...");
}

void loop() {
  // Check if a full 9-byte packet is waiting in the buffer
  if (Serial1.available() >= 9) {
    // Look for the 2-byte header (0x59, 0x59)
    if (Serial1.read() == 0x59) {
      if (Serial1.read() == 0x59) {
        uint8_t data[7];
        for (int i = 0; i < 7; i++) {
          data[i] = Serial1.read();
        }
        
        // Calculate 8-bit checksum for data integrity
        uint8_t checksum = 0x59 + 0x59;
        for (int i = 0; i < 6; i++) {
          checksum += data[i];
        }
        
        // If checksum matches, parse distance and signal strength
        if (checksum == data[6]) {
          int distance = data[0] + (data[1] << 8); // Distance in cm
          int strength = data[2] + (data[3] << 8); // Signal strength quality
          
          Serial.print("Distance: ");
          Serial.print(distance);
          Serial.print(" cm  |  Strength: ");
          Serial.println(strength);
        } else {
          Serial.println("Checksum mismatch (ignoring noisy packet)");
        }
      }
    }
  }
}