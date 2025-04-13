#include "I2Cdev.h"
#include "MPU6050.h"

MPU6050 mpu;

#define BUZZER_PIN 9  // Pin du buzzer

int16_t ax, ay, az;
int16_t gx, gy, gz;
bool blinkState;

void setup() {
  #if I2CDEV_IMPLEMENTATION == I2CDEV_ARDUINO_WIRE
    Wire.begin(); 
  #elif I2CDEV_IMPLEMENTATION == I2CDEV_BUILTIN_FASTWIRE
    Fastwire::setup(400, true);
  #endif

  Serial.begin(38400); 

  Serial.println("Initializing MPU...");
  mpu.initialize();
  Serial.println("Testing MPU6050 connection...");
  if(!mpu.testConnection()){
    Serial.println("MPU6050 connection failed");
    while(true);
  } else {
    Serial.println("MPU6050 connection successful");
  }

  Serial.println("Updating internal sensor offsets...\n");
  mpu.setXAccelOffset(0);
  mpu.setYAccelOffset(0);
  mpu.setZAccelOffset(0);
  mpu.setXGyroOffset(0);
  mpu.setYGyroOffset(0);
  mpu.setZGyroOffset(0);

  pinMode(LED_BUILTIN, OUTPUT);
  pinMode(BUZZER_PIN, OUTPUT);  
}

void loop() {
  mpu.getMotion6(&ax, &ay, &az, &gx, &gy, &gz);


  Serial.print("a/g:\t");
  Serial.print(ax); Serial.print("\t");
  Serial.print(ay); Serial.print("\t");
  Serial.print(az); Serial.print("\t");
  Serial.print(gx); Serial.print("\t");
  Serial.print(gy); Serial.print("\t");
  Serial.print(gz); Serial.print("\t");


  String status = detectPosture(ax, ay, az);
  Serial.println(status);

  blinkState = !blinkState;
  digitalWrite(LED_BUILTIN, blinkState);


  if (Serial.available()) {
    String command = Serial.readStringUntil('\n'); 

    if (command == "CORSET_BONNE") {
      digitalWrite(BUZZER_PIN, LOW); 
    }
    else if (command == "CORSET_MAUVAIS") {
      digitalWrite(BUZZER_PIN, HIGH);  
    }
    else if (command == "CORSET_NONPORTE") {
      digitalWrite(BUZZER_PIN, LOW); 
    }
  }

  delay(500); 
}


String detectPosture(int16_t ax, int16_t ay, int16_t az) {
  float accMagnitude = sqrt(ax * ax + ay * ay + az * az);

  if (accMagnitude < 1000) {
    return "Corset non porté";  
  }

  if (abs(ax) < 2000 && abs(az - 16000) < 2000) {
    return "Bonne posture";  
  } else {
    return "Mauvaise posture"; 
  }
} 