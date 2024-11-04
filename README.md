# Internet of Things (IoT) Security Lab

## Overview
This project is focused on building a real-time data pipeline for monitoring the availability of Vélib' bike-sharing stations across different cities. It incorporates secure data handling practices using encryption to protect sensitive information, and leverages Kafka for real-time data ingestion and MongoDB for storage.

## Features
- **Real-Time Data Pipeline**: Uses Kafka to stream real-time data from the JCDecaux API.
- **Data Encryption**: Sensitive data is encrypted before storage in MongoDB, ensuring information security.
- **MongoDB Integration**: Stores encrypted data with easy retrieval for monitoring station availability.

## Technologies Used
- **Kafka**: A distributed streaming platform to handle real-time data.
- **MongoDB**: A NoSQL database for persistent data storage.
- **Python**: Scripts for data processing, encryption, and storage.
- **JCDecaux API**: Provides real-time data for Vélib' bike-sharing stations.

## Setup Instructions

### Prerequisites
- **Kafka**: Download and install Kafka from [Kafka's official website](https://kafka.apache.org/).
- **MongoDB**: Follow the installation guide for MongoDB on [Ubuntu](https://www.mongodb.com/docs/manual/tutorial/install-mongodb-on-ubuntu/).
- **Python**: Ensure Python is installed and install required libraries:
  ```bash
  pip install kafka-python cryptography
