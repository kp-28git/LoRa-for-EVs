# **LoRa-Based Communication for Battery Monitoring System (BMS) in EVs**

![LoRa-BMS Banner](https://via.placeholder.com/800x200.png?text=LoRa-Based+Battery+Monitoring+System)

## **Table of Contents**
1. [Overview](#overview)
2. [Features](#features)
3. [Hardware Components](#hardware-components)
4. [System Architecture](#system-architecture)
5. [Software Implementation](#software-implementation)
6. [Testing and Results](#testing-and-results)
7. [Applications](#applications)
8. [Future Enhancements](#future-enhancements)
9. [Conclusion](#conclusion)

---

## **Overview**
The **LoRa-based Communication for Battery Monitoring System (BMS) in EVs** is a robust solution designed to monitor and manage the performance of a Li-ion battery pack. It features real-time data acquisition, dynamic communication, and safety mechanisms to ensure optimal operation. The system leverages LoRa technology for long-range communication, making it suitable for Vehicle-to-Vehicle (V2V) and Vehicle-to-Infrastructure (V2I) applications.

---

## **Features**
- **Sensor Data Acquisition**:
  - Collects temperature, current, and voltage data from DHT11, ACS712, and voltage sensors.
- **Battery Management**:
  - Calculates State of Charge (SoC) and State of Health (SoH).
  - Automates charging and discharging control using 5V relays.
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
- **ACS712 Current Sensor**: Monitors real-time current.
- **Voltage Sensor**: Measures battery voltage.
- **L298 Motor Driver**: Drives a 12V DC motor.
- **5V Relays**: Controls charging/discharging operations.
- **Safety Relay**: Provides immediate battery isolation during anomalies.
- **LoRa Module**: Facilitates long-range communication.
- **12V, 1A Charger**: Charges the 3S Li-ion battery pack.

---

## **System Architecture**

```mermaid
graph TD
    A[ESP32 Microcontroller] -->|Temperature Data| B[DHT11 Sensor]
    A -->|Current Data| C[ACS712 Current Sensor]
    A -->|Voltage Data| D[Voltage Sensor]
    A -->|Control Signals| E[5V Relays]
    E -->|Battery Pack Connection| F[3S Li-ion Battery Pack]
    F -->|Power Supply| G[L298 Motor Driver]
    G -->|Load| H[12V Motor]
    A -->|LoRa Communication| I[LoRa Module]
    A -->|Safety Trigger| J[Safety Relay]
