"""Redpanda Producer — Simulates real-time customer events"""
import json, time, random, uuid
from datetime import datetime
from kafka import KafkaProducer

producer = KafkaProducer(
    bootstrap_servers='localhost:19092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

TOPIC = 'customer_events'
event_types = ['purchase', 'login', 'cart_abandon', 'product_view']
products = ['Wireless Headphones', 'Running Shoes', 'Coffee Maker', 'Yoga Mat', 'Desk Lamp']

print("Redpanda Producer started. Sending events...")
while True:
    event = {
        'event_id': str(uuid.uuid4()),
        'customer_id': random.randint(1, 500),
        'event_type': random.choice(event_types),
        'product': random.choice(products) if random.random() > 0.5 else None,
        'amount': round(random.uniform(10, 500), 2),
        'timestamp': datetime.now().isoformat(),
    }
    producer.send(TOPIC, value=event)
    print(f"Sent: {event['event_type']} | Customer {event['customer_id']} | ${event['amount']}")
    time.sleep(2)