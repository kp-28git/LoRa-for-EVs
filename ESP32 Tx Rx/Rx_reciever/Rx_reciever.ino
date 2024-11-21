#include <SPI.h>
#include <LoRa.h>
#include <DHT.h>

// Pin Definitions for LoRa
#define SS     21    // Slave Select Pin
#define RST    22   // Reset Pin
#define DIO0   2    // DIO0 Pin for packet transmission

// DHT11 sensor settings
#define DHTPIN 13    // Pin connected to the DHT11 data pin
#define DHTTYPE DHT11

DHT dht(DHTPIN, DHTTYPE);

// Modes for operation
enum OperationMode {
  IDLE,
  RECEIVING,
  SCANNING
};

// Structure to hold self data
struct SelfData {
  float soc;             // State of Charge in percentage
  float voltage;         // Voltage in Volts
  float temperature;     // Temperature in Celsius
  String vehicleID;      // Unique Vehicle ID
  float chargerWattage;  // Charger wattage in kW
  float requiredCapacity; // Required charging capacity in kWh
  float currentCapacity;  // Current capacity in kWh (calculated only in setup)
};

// Initialize the self data
SelfData selfdata = {
  85.5,             // soc
  3.7,              // voltage
  0.0,              // temperature (updated in loop)
  "EVab1111",       // vehicleID
  22.5,             // chargerWattage
  0.0,              // requiredCapacity
  0.0               // currentCapacity (calculated in setup)
};

// Current operation mode, starting with RECEIVING mode
OperationMode currentMode = RECEIVING;

void setup() {
  Serial.begin(115200);

  // Initialize LoRa module
  LoRa.setPins(SS, RST, DIO0);
  if (!LoRa.begin(915E6)) {  // Set frequency to 915 MHz (adjust as per your region)
    Serial.println("Starting LoRa failed!");
    while (1);
  }

  Serial.println("LoRa Transmitter/Receiver Initialized in RECEIVING mode");

  // Initialize DHT11 sensor
  dht.begin();

  // Calculate the initial current capacity based on SOC and voltage
  selfdata.currentCapacity = calculateCurrentCapacity(selfdata.soc, selfdata.voltage);

  // Print the initial calculated current capacity to Serial Monitor
  Serial.print("Initial Current Capacity: ");
  Serial.println(selfdata.currentCapacity);
}

void loop() {

  // Update temperature data from DHT11
  selfdata.temperature = getTemperature();

  // Check for mode change request
  checkForModeChange();

  // Run the appropriate function based on the current mode
  if (currentMode == RECEIVING) {
    receiveAndParseBMSData();
  } else if (currentMode == SCANNING) {
    requestChargingCapacity();
  }
}

// Function to get temperature from DHT11
float getTemperature() {
  float temp = dht.readTemperature();
  if (isnan(temp)) {
    Serial.println("Failed to read temperature from DHT11 sensor!");
    return selfdata.temperature;  // Return last known temperature if read fails
  }
  return temp;
}


// Function to check Serial for mode change
void checkForModeChange() {
  if (Serial.available() > 0) {
    char input = Serial.read();
    if (input == 'R') {
      currentMode = RECEIVING;  // Switch to RECEIVING mode
      Serial.println("Switched to RECEIVING mode.");
      clearSerialBuffer(); // Clear any leftover input
    } else if (input == 'S') {
      currentMode = SCANNING;  // Switch to SCANNING mode
      Serial.println("Switched to SCANNING mode. Enter required charging capacity:");
      clearSerialBuffer(); // Clear any leftover input
    }
  }
}

// Function to calculate current capacity based on SOC and voltage
float calculateCurrentCapacity(float soc, float voltage) {
  const float nominalCapacity = 60.0; // Nominal full capacity in kWh (adjustable)
  
  // Calculate current capacity based on SOC percentage
  float currentCapacity = (soc / 100.0) * nominalCapacity;

  return currentCapacity;
}

// Function to request and send charging capacity (Scanning mode)
void requestChargingCapacity() {
  // Give time for the user to enter the input completely
  delay(200);  // Short delay to allow for input capture

  // Wait for user to enter required capacity
  if (Serial.available() > 0) {
    String input = Serial.readStringUntil('\n');  // Read user input from Serial Monitor
    input.trim();  // Remove any leading/trailing whitespace

    // Clear any leftover characters from the buffer to prevent issues
    clearSerialBuffer();

    // Convert input to a float and check if it's valid
    float capacity = input.toFloat();
    
    if (capacity > 0) {  // Ensure valid capacity input
      selfdata.requiredCapacity = capacity;  // Store in structure

      // Update current capacity before comparison
      selfdata.currentCapacity = calculateCurrentCapacity(selfdata.soc, selfdata.voltage);

      // Transmit vehicle ID, required capacity, charger wattage, and current capacity
      String message = String("Vehicle ID: ") + selfdata.vehicleID + 
                       String(", Required Capacity: ") + selfdata.requiredCapacity + 
                       String(" kWh, Charger Wattage: ") + selfdata.chargerWattage + 
                       String(" kW, Current Capacity: ") + selfdata.currentCapacity + String("kWh");

      LoRa.beginPacket();
      LoRa.print(message);
      LoRa.endPacket();

      // Print the sent message to the Serial Monitor
      Serial.println("Sent: " + message);

      // Switch back to RECEIVING mode after scanning
      currentMode = RECEIVING;
      Serial.println("Switched back to RECEIVING mode.");
      clearSerialBuffer(); // Clear input after transmitting
    } else {
      Serial.println("Invalid input. Please enter a valid numeric capacity.");
      clearSerialBuffer(); // Clear invalid input to avoid repeated errors
    }
  }
}


// Function to clear the Serial input buffer
void clearSerialBuffer() {
  while (Serial.available()) {
    Serial.read();  // Read and discard any remaining input
  }
}

// Function to receive and parse BMS data (Receiving mode)
void receiveAndParseBMSData() {
  int packetSize = LoRa.parsePacket();
  if (packetSize) {
    String receivedMessage = "";
    while (LoRa.available()) {
      receivedMessage += (char)LoRa.read();
    }
    if (receivedMessage.indexOf("Established.") == -1) {
      Serial.println("Received: " + receivedMessage);

      // Parse the message to extract Vehicle ID, SOC, Voltage, Temperature, Charger Wattage, and Required Capacity
      String receivedID;
      float receivedChargerWattage;
      float receivedRequiredCapacity;
      parseMessage(receivedMessage, receivedID, receivedChargerWattage, receivedRequiredCapacity);

      // Update selfdata's current capacity
      selfdata.currentCapacity = calculateCurrentCapacity(selfdata.soc, selfdata.voltage);

      // Compare required capacity with current capacity
      if (receivedRequiredCapacity < selfdata.currentCapacity) {
        Serial.println("Requested capacity is within the limits.");
        Serial.println("Do you accept the charging request? (Y/N)");

        while (true) {
          if (Serial.available() > 0) {
            char response = Serial.read();
            clearSerialBuffer();  // Clear any leftover input
            if (response == 'Y' || response == 'y') {
              // Call the function to calculate and display estimated charging time
              estimateChargingTime(receivedChargerWattage, receivedRequiredCapacity);
              break;  // Exit the loop after accepting
            } else if (response == 'N' || response == 'n') {
              // Transmit rejection message

              String rejectionMessage = String("Link Cannot Be Established. ") + String("Charging request rejected by ") + selfdata.vehicleID ;
              LoRa.beginPacket();
              LoRa.print(rejectionMessage);
              LoRa.endPacket();
              Serial.println("Transmitted: " + rejectionMessage);

              // Print link cannot be established message
              Serial.println("Link Cannot Be Established.");

              // Switch back to RECEIVING mode after rejection
              currentMode = RECEIVING;
              Serial.println("Switched back to RECEIVING mode.");

              break;  // Exit the loop after rejecting
            }
          }
        }
      } else {
        Serial.println("Requested capacity exceeds current capacity.");
        currentMode = RECEIVING;
      }
    }
      else if (receivedMessage.indexOf("Established.") != -1) {
      Serial.println("Received: " + receivedMessage);
      }
  }
}

// Function to calculate and display estimated charging time
void estimateChargingTime(float receivedChargerWattage, float receivedRequiredCapacity) {
  // Calculate the minimum charger wattage between selfdata and received charger wattage
  //float effectiveChargerWattage = min(selfdata.chargerWattage, receivedChargerWattage);

  // Calculate the estimated charging time in hours based on required capacity and effective wattage
  float estimatedTime = (receivedRequiredCapacity / receivedChargerWattage)*60;

  // Convert the estimated time to minutes for better readability
  //estimatedTime *= 60;

  // Display the calculated charging time and link established
  Serial.print("Estimated Charging Time: ");
  Serial.print(estimatedTime);
  Serial.println(" minutes");
  
  // Print link established message
  Serial.println("Link Established.");

  // Optionally transmit the accepted request message
  String acceptedMessage = String("Link Established. ") + String("Charging request accepted from ") + selfdata.vehicleID +
                           String(", Estimated Charging Time: ") + estimatedTime + " minutes.";
  LoRa.beginPacket();
  LoRa.print(acceptedMessage);
  LoRa.endPacket();
  Serial.println("Transmitted: " + acceptedMessage);

  // Switch back to RECEIVING mode after acceptance
  currentMode = RECEIVING;
  Serial.println("Switched back to RECEIVING mode.");
}

// Function to parse the received message
void parseMessage(String message, String &vehicleIDString, float &receivedChargerWattage, float &receivedRequiredCapacity) {
  int idIndex = message.indexOf("Vehicle ID: ");
  int chargerWattageIndex = message.indexOf("Charger Wattage: ");
  int capacityIndex = message.indexOf("Required Capacity: ");
  
  // Extract Vehicle ID value
  int idEnd = message.indexOf(',', idIndex);
  vehicleIDString = message.substring(idIndex + 12, idEnd);  

  // Extract Charger Wattage value
  int chargerEnd = message.indexOf(',', chargerWattageIndex);
  String chargerWattageString = message.substring(chargerWattageIndex + 17, chargerEnd);
  receivedChargerWattage = chargerWattageString.toFloat();

  // Extract Required Capacity value
  int capacityEnd = message.indexOf('kWh', capacityIndex);
  String requiredCapacityString = message.substring(capacityIndex + 18, capacityEnd);
  receivedRequiredCapacity = requiredCapacityString.toFloat();
}