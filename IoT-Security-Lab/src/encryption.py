import json
from cryptography.fernet import Fernet
from pymongo import MongoClient
from kafka import KafkaConsumer
import  os
# Generate a key
def generate_key(filename):
    key = Fernet.generate_key()
    with open(filename, 'wb') as key_file:
        key_file.write(key)
    return key

# Load the encryption key
def load_key(filename):
    with open(filename, 'rb') as file:
        return file.read()

# Encrypt the sensitive fields
def encrypt_data(data, key):
    f = Fernet(key)
    encrypted_data = {}
    for key, value in data.items():
        if key in ["address", "contract_name"]:
            encrypted_data[key] = f.encrypt(value.encode()).decode()
        else:
            encrypted_data[key] = value
    return encrypted_data

# Connect to MongoDB
client = MongoClient('localhost', 27017)
db = client['iot']
collection = db['bikes']

# Generate or load the encryption key
encryption_key_file = 'encryption_key.key'
if not os.path.isfile(encryption_key_file):
    key = generate_key(encryption_key_file)
else:
    key = load_key(encryption_key_file)

# Consume messages from Kafka
consumer = KafkaConsumer("velib-stations", bootstrap_servers='localhost:9092', group_id="velib-monitor-stations")
for message in consumer:
    # Decode the message
    station = json.loads(message.value.decode())

    # Encrypt sensitive fields
    encrypted_station = encrypt_data(station, key)

    # Insert the encrypted data into MongoDB
    collection.insert_one(encrypted_station)

    print("Message inserted into MongoDB:", encrypted_station)