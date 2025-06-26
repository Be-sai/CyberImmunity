from kafka import KafkaProducer, KafkaConsumer
import json

KAFKA_BROKER = 'kafka:9092'

TOPICS = {
    'commands': 'smart_home_commands',
    'notifications': 'smart_home_notifications',
    'sensor_data': 'sensor_data',
    'security_alerts': 'security_alerts',
    'emergency_calls': 'emergency_calls',
    'access_logs': 'access_logs',
    'system_logs': 'system_logs'
}

def create_producer():
    return KafkaProducer(
        bootstrap_servers=[KAFKA_BROKER],
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )

def create_consumer(topic, group_id=None):
    return KafkaConsumer(
        topic,
        bootstrap_servers=[KAFKA_BROKER],
        auto_offset_reset='earliest',
        group_id=group_id,
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )