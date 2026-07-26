"""
Redpanda Multi-Topic Producer — Simulates different event streams
"""

import json, time, random, uuid
from datetime import datetime
from kafka import KafkaProducer

producer = KafkaProducer(
    bootstrap_servers='localhost:19092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

TOPICS = ['customer_events', 'orders', 'alerts']
event_types = ['purchase', 'login', 'cart_abandon', 'product_view']
products = ['Wireless Headphones', 'Running Shoes', 'Coffee Maker', 'Yoga Mat', 'Desk Lamp']
alert_types = ['high_value_purchase', 'churn_risk', 'fraud_suspected', 'inventory_low']

print("Redpanda Multi-Topic Producer started.\n")

while True:
    # Topic 1: Customer Events
    event = {
        'event_id': str(uuid.uuid4()),
        'customer_id': random.randint(1, 500),
        'event_type': random.choice(event_types),
        'product': random.choice(products),
        'amount': round(random.uniform(10, 500), 2),
        'timestamp': datetime.now().isoformat(),
    }
    producer.send(TOPICS[0], value=event)
    print(f"[{TOPICS[0]}] {event['event_type']} | Cust {event['customer_id']} | ${event['amount']}")

    # Topic 2: Orders
    order = {
        'order_id': str(uuid.uuid4()),
        'customer_id': random.randint(1, 500),
        'product': random.choice(products),
        'quantity': random.randint(1, 5),
        'total': round(random.uniform(20, 1000), 2),
        'status': random.choice(['placed', 'confirmed', 'shipped']),
        'timestamp': datetime.now().isoformat(),
    }
    producer.send(TOPICS[1], value=order)
    print(f"[{TOPICS[1]}] Order | Cust {order['customer_id']} | ${order['total']} | {order['status']}")

    # Topic 3: Alerts (occasional)
    if random.random() < 0.3:
        alert = {
            'alert_id': str(uuid.uuid4()),
            'alert_type': random.choice(alert_types),
            'customer_id': random.randint(1, 500),
            'severity': random.choice(['low', 'medium', 'high', 'critical']),
            'message': 'Alert triggered',
            'timestamp': datetime.now().isoformat(),
        }
        producer.send(TOPICS[2], value=alert)
        print(f"[{TOPICS[2]}] {alert['alert_type']} | Severity: {alert['severity']}")

    time.sleep(3)