# IoT Security Lab — Real-Time Vélib' Station Monitoring with Kafka & Encryption

## Overview

This project implements a secure, real-time **Internet of Things (IoT)** data pipeline by treating Vélib' bike-sharing stations as a network of smart connected devices constantly transmitting live data. The system collects real-time station information via the JCDecaux API, streams it through Apache Kafka, encrypts sensitive fields using AES symmetric encryption, and stores the secured records in MongoDB. The primary focus is on demonstrating how IoT data can be protected throughout a streaming pipeline — from ingestion to storage.



## Motivation and Importance

IoT devices generate vast amounts of sensitive data continuously. In the context of smart city infrastructure like bike-sharing stations, this data includes precise GPS coordinates, station addresses, and contract identifiers that can reveal behavioral patterns or sensitive location data. Securing this data stream is critical because:

- **Privacy Protection:** Station addresses and geolocation data can be exploited if intercepted in transit.
- **Real-World Relevance:** The architecture mirrors real IoT deployments in smart cities, logistics, and industrial monitoring.
- **End-to-End Security:** Security must be applied at the streaming layer, not just at the database level — a key principle in modern data engineering.

## Key Features

- **Real-Time Data Pipeline:** Kafka handles continuous data streaming from the JCDecaux API, decoupling production from consumption for scalable, fault-tolerant ingestion.
- **Selective Field Encryption:** Applies AES symmetric encryption (via the Fernet library) only to sensitive fields (`address`, `contract_name`), leaving non-sensitive operational data (`available_bikes`, `status`) readable for monitoring.
- **Secure Persistent Storage:** Encrypted station records are stored in MongoDB, ensuring data at rest is protected.
- **Key Management:** Encryption keys are generated once and persisted to `encryption_key.key`, then reloaded on subsequent runs to maintain decryption capability.

## Project Architecture

The directory structure of the project is as follows:

```plaintext
IoT-Security-Lab/
├── src/
│   ├── consumer.py            # Consumer script for data decryption and storage
│   ├── encryption.py          # Encryption and decryption functions
│   ├── encryption_key.key     # Encryption key for symmetric encryption
│   └── producer.py            # Producer script for data ingestion from API to Kafka
└── venv/                      # Python virtual environment for project dependencies
    ├── bin/                   # Executable files
    ├── include/               # Header files for C extensions
    ├── lib/                   # Libraries for Python packages
    └── lib/pythonX.X/         # Python version-specific libraries
        └── site-packages/     # Installed Python packages
```

### Pipeline Flow

```
JCDecaux API (Live Station Data)
         │
         ▼
  ┌─────────────┐
  │ producer.py │  ──► Kafka Topic: "velib-stations"
  └─────────────┘
         │
         ▼
  ┌───────────────────┐
  │  encryption.py    │  ◄── Kafka Consumer
  │  (AES Encryption) │
  └───────────────────┘
         │
         ▼
  ┌──────────────────────────────┐
  │  MongoDB — db: iot           │
  │  Collection: bikes           │
  │  (encrypted station records) │
  └──────────────────────────────┘
```

## Data Source — JCDecaux API

The project uses the **JCDecaux API** to retrieve real-time data on Vélib' stations.

**API Base URL:** `https://api.jcdecaux.com/vls/v1/stations?apiKey=YOUR_API_KEY`

Each station object returned by the API contains the following fields:

| Field | Description | Encrypted |
|---|---|---|
| `address` | Street address of the station |  Yes |
| `contract_name` | Name of the Vélib' system / city |  Yes |
| `position` | Latitude and longitude coordinates |  No |
| `available_bikes` | Number of bikes currently available |  No |
| `available_bike_stands` | Number of free docking stands |  No |
| `bike_stands` | Total capacity of the station |  No |
| `status` | Station status (`OPEN` / `CLOSED`) |  No |
| `last_update` | Timestamp of the last data update |  No |
| `name` | Station name |  No |
| `number` | Unique station identifier |  No |
| `banking` | Whether the station has a payment terminal |  No |
| `bonus` | Whether the station is part of a bonus program |  No |

### Getting an API Key

1. Create an account at [https://developer.jcdecaux.com/#/signup](https://developer.jcdecaux.com/#/signup)
2. Retrieve your API key from your user profile.
3. Verify your key:
   ```bash
   curl "https://api.jcdecaux.com/vls/v1/stations?apiKey=YOUR_API_KEY"
   ```
4. To filter by city (e.g., Dublin):
   ```bash
   curl "https://api.jcdecaux.com/vls/v1/stations?apiKey=YOUR_API_KEY&contract=Dublin"
   ```

## Data Pipeline Implementation

### Producer (`producer.py`)

The producer runs in a continuous loop, polling the JCDecaux API every second and publishing each station's raw JSON data to the Kafka topic `"velib-stations"` (broker at `localhost:9092`).

```python
from kafka import KafkaProducer

producer = KafkaProducer(bootstrap_servers="localhost:9092")

while True:
    response = urllib.request.urlopen(url)
    stations = json.loads(response.read().decode())
    for station in stations:
        producer.send("velib-stations", json.dumps(station).encode())
    time.sleep(1)
```

### Consumer & Encryption (`encryption.py`)

The consumer subscribes to the `"velib-stations"` Kafka topic, decodes each message, encrypts the sensitive fields using **Fernet (AES)** symmetric encryption, and inserts the resulting record into MongoDB (`db: iot`, collection: `bikes`).

```python
def encrypt_data(data, key):
    f = Fernet(key)
    encrypted_data = {}
    for key, value in data.items():
        if key in ["address", "contract_name"]:
            encrypted_data[key] = f.encrypt(value.encode()).decode()
        else:
            encrypted_data[key] = value
    return encrypted_data
```

## Encryption Method

The project implements **symmetric encryption** using the **Advanced Encryption Standard (AES)** through Python's `cryptography.fernet` library.

**How it works:**
- A single secret key is shared between producer and consumer — generated once with `Fernet.generate_key()` and saved to `encryption_key.key`.
- On startup, the consumer checks if the key file exists: if yes, it loads it; if not, it generates a new one.
- Fernet guarantees both encryption (AES-128-CBC) and authentication (HMAC-SHA256), protecting against eavesdropping and tampering.

**Security Considerations:**
- The security of the entire system depends on protecting `encryption_key.key`. If this file is compromised, all stored data can be decrypted.
- MongoDB's native encryption at rest should be enabled in production for an additional protection layer.
- In a production environment, key management should be delegated to a secrets manager (e.g., HashiCorp Vault, AWS KMS).

## Environment Setup

### 1. Install Java (required for Kafka)

```bash
sudo yum install java-1.8.0-openjdk
java -version
```

### 2. Install and Configure Kafka

```bash
wget https://dlcdn.apache.org/kafka/3.4.0/kafka_2.13-3.4.0.tgz
tar -xvf kafka_2.13-3.4.0.tgz
cd kafka_2.13-3.4.0
```

Start ZooKeeper:
```bash
./bin/zookeeper-server-start.sh ./config/zookeeper.properties
```

Start the Kafka broker:
```bash
./bin/kafka-server-start.sh ./config/server.properties
```

### 3. Install MongoDB

Follow the official guide at [https://www.mongodb.com/docs/manual/tutorial/install-mongodb-on-ubuntu/](https://www.mongodb.com/docs/manual/tutorial/install-mongodb-on-ubuntu/), then:

```bash
sudo service mongod start
sudo service mongod status
```

### 4. Install Python Dependencies

```bash
pip install kafka-python cryptography pymongo
```

## Running the Application

**Step 1 — Start the producer:**
```bash
python src/producer.py
```

**Step 2 — Start the consumer:**
```bash
python src/encryption.py
```

Expected producer output:
```
1715458053.201 Produced 2386 station records
1715458057.961 Produced 2386 station records
...
```

Expected consumer output:
```
Message inserted into MongoDB: {'number': 38, 'contract_name': 'gAAAAA...', 'address': 'gAAAAA...', ...}
```

## Technology Stack

- **Streaming:** Apache Kafka 3.4.0, ZooKeeper
- **Encryption:** Python `cryptography` — Fernet (AES-128-CBC + HMAC-SHA256)
- **Database:** MongoDB (`db: iot`, collection: `bikes`)
- **API:** JCDecaux REST API (JSON)
- **Language:** Python 3
- **Core Libraries:** `kafka-python`, `cryptography`, `pymongo`, `urllib`, `json`

## Limitations and Future Work

- **Key Distribution:** The encryption key is stored as a local file. A production system should use a centralized secrets manager for safe key distribution across services.
- **Geolocation Encryption:** The `position` field (latitude/longitude) is not encrypted. For full location privacy, it should be added to the sensitive fields list.
- **Kafka Security:** The broker currently runs without TLS or SASL authentication. Enabling SSL/TLS would secure the channel between producer and consumer.
- **Decryption Utility:** No decryption script is currently provided. A future `decrypt.py` utility should be added for authorized data retrieval and auditing.
- **Scalability:** The current setup is single-node. A production deployment would use a multi-broker Kafka cluster and a replicated MongoDB setup.

