from prometheus_client import Counter, Histogram, Info, Gauge, REGISTRY, CollectorRegistry
import time

# Clear default registry to avoid duplicate metrics
for collector in list(REGISTRY._collector_to_names.keys()):
    REGISTRY.unregister(collector)

# API Metrics
REQUEST_COUNT = Counter(
    'api_requests_total',
    'Total number of API requests',
    ['method', 'endpoint', 'status']
)

REQUEST_DURATION = Histogram(
    'api_request_duration_seconds',
    'Request duration in seconds',
    ['method', 'endpoint'],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0]
)

DOCUMENT_SIZE = Histogram(
    'document_size_bytes',
    'Document content size in bytes',
    buckets=[100, 500, 1000, 5000, 10000]
)

# Consumer Metrics
PROCESSING_TIME = Histogram(
    'document_processing_seconds',
    'Time spent processing documents',
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0]
)

PROCESSING_SUCCESS = Counter(
    'document_processing_success_total',
    'Number of successfully processed documents'
)

PROCESSING_FAILED = Counter(
    'document_processing_failed_total',
    'Number of failed document processing attempts'
)

# System Metrics
MEMORY_USAGE = Gauge(
    'app_memory_usage_bytes',
    'Memory usage in bytes'
)

CPU_USAGE = Gauge(
    'app_cpu_usage_percent',
    'CPU usage percentage'
)

# Metrics
DOCUMENTS_PROCESSED = Counter(
    'documents_processed_total',
    'Number of documents processed'
)

KAFKA_MESSAGES_SENT = Counter(
    'kafka_messages_sent_total',
    'Number of messages sent to Kafka'
)

KAFKA_MESSAGES_FAILED = Counter(
    'kafka_messages_failed_total',
    'Number of failed Kafka message sends'
)

APP_INFO = Info('document_processor', 'Document processor information') 