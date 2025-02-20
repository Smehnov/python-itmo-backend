from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import TopicAlreadyExistsError
from src.app.core.config import settings

def setup_kafka():
    print("Setting up Kafka topic...")
    admin_client = KafkaAdminClient(
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS
    )
    
    topic = NewTopic(
        name=settings.KAFKA_TOPIC,
        num_partitions=1,
        replication_factor=1
    )
    
    try:
        admin_client.create_topics([topic])
        print(f"Created topic: {settings.KAFKA_TOPIC}")
    except TopicAlreadyExistsError:
        print(f"Topic {settings.KAFKA_TOPIC} already exists")
    except Exception as e:
        print(f"Error creating topic: {e}")
    finally:
        admin_client.close()

if __name__ == "__main__":
    setup_kafka() 