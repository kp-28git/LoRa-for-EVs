# **LoRa-Based Communication for Battery Monitoring System (BMS) in EVs**

## **Table of Contents**
1. [Overview](#overview)
2. [Features](#features)
3. [Hardware Components](#hardware-components)
4. [Testing and Results](#testing-and-results)
7. [Applications](#applications)

---

## **Overview**
The **LoRa-based Communication for Battery Monitoring System (BMS) in EVs** is a robust solution designed to monitor and manage the performance of a Li-ion battery pack. It features real-time data acquisition, dynamic communication, and safety mechanisms to ensure optimal operation. The system leverages LoRa technology for long-range communication, making it suitable for Vehicle-to-Vehicle (V2V) and Vehicle-to-Infrastructure (V2I) applications.

---

## **Features**
- **Sensor Data Acquisition**:
  - Collects temperature, current, and voltage data from DHT11, ACS712, and voltage sensors.
- **Battery Management**:
  - Calculates State of Charge (SoC) and State of Health (SoH).
  - Automates charging and discharging control using relays.
- **Safety Mechanisms**:
  - Immediate battery isolation via safety relay during over-temperature, over-current, or over-voltage conditions.
- **Communication**:
  - Uses LoRa for reliable and long-range data transfer between nodes.
- **Motor Control**:
  - Drives a 12V motor using the L298 motor driver.

---

## **Hardware Components**
- **ESP32 Microcontroller**: Core processing and communication.
- **3S Li-ion Battery Pack**: 3x18650 cells with 2200mAh capacity.
- **DHT11 Sensor**: Measures temperature and humidity.
- **ACS712 Current Sensor**: Monitors current.
- **Voltage Sensor**: Measures battery voltage.
- **L298 Motor Driver**: Drives a 12V DC motor.
- **5V Relays**: Controls charging/discharging operations.
- **Safety Relay**: Provides immediate battery isolation during anomalies.
- **LoRa Module**: Facilitates long-range communication.
- **12V, 1A Charger**: Charges the 3S Li-ion battery pack.

---

## **Testing and Results**
### **1. Communication Range**
- **Open Areas**: Achieved up to **1.2 km** of stable LoRa communication.
- **Urban Environments**: Reliable operation up to **650 m**, with moderate obstacles causing minimal interference.

### **2. Safety Tests**
- **Over-Voltage**: Threshold exceeded at **> 12.6V**.
- **Over-Current**: Triggered at **> 1A**.
- **Over-Temperature**: Activated at **> 60°C**.

### **3. Battery Performance**
- **Charging**: Maintained stable operation using a **12V, 1A charger**.
- **Discharging**: Delivered consistent performance driving a **12V motor** via the L298 driver.

---

## **Applications**
**Electric Vehicles (EVs)**
  - Real-time battery monitoring and management for EVs.
  - Enables Vehicle-to-Vehicle (V2V) and Vehicle-to-Infrastructure (V2I) communication for charging requests and capacity sharing.

**Renewable Energy Systems**
  - Monitors battery health in solar and wind energy storage setups.
  - Ensures efficient charging and discharging for optimal energy usage.

**Smart Energy Grids**
  - Facilitates IoT-based battery data sharing for grid-level energy distribution.
  - Enables predictive maintenance and load balancing.

**Industrial Applications**
  - Battery monitoring in automated machinery and robotics.
  - Prevents system failures due to battery anomalies.
