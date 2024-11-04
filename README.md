# IoT Security Lab

## Overview
This project implements a secure, real-time data pipeline for monitoring Vélib' bike-sharing station availability. Using Kafka for data ingestion and MongoDB for storage, it encrypts sensitive data fields to ensure secure handling and storage.

## Features
- **Real-Time Data Pipeline**: Kafka handles data streaming from the JCDecaux API.
- **Data Encryption**: Encrypts sensitive information before storage in MongoDB.
- **Storage**: MongoDB used for persistent data storage with added encryption for security.

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
