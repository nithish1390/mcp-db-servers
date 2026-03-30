import sys
import json
import os
import re
from ibm_mq import MQConnection

# IBM MQ Config from env
MQ_CONFIG = {
    "queue_manager": os.getenv("MQ_QMGR", "QM1"),
    "host": os.getenv("MQ_HOST", "localhost"),
    "port": os.getenv("MQ_PORT", "1414"),
    "channel": os.getenv("MQ_CHANNEL", "DEV.APP.SVRCONN"),
    "user": os.getenv("MQ_USER", "app"),
    "password": os.getenv("MQ_PASSWORD", "password")
}

FILE_PATTERN = r"^[A-Za-z0-9._-]+@MQ\.(xml|txt)$"

def validate_filename(filename):
    if not re.match(FILE_PATTERN, filename):
        raise ValueError(
            "Invalid file name. Expected format: QueueName@MQ.xml or QueueName@MQ.txt"
        )

def extract_queue_name(filename):
    return filename.split("@MQ")[0]

def validate_properties(source, destination, object_name):
    errors = []
    pattern = r"^[A-Za-z0-9._-]+$"

    if not source or len(source) < 2:
        errors.append("Source must be at least 2 characters")

    if not destination or len(destination) < 2:
        errors.append("Destination must be at least 2 characters")

    if not object_name or len(object_name) < 2:
        errors.append("ObjectName must be at least 2 characters")

    for name, value in {
        "Source": source,
        "Destination": destination,
        "ObjectName": object_name
    }.items():
        if value and not re.match(pattern, value):
            errors.append(f"{name} contains invalid characters")

    if errors:
        raise ValueError(", ".join(errors))


def publish_to_mq(queue_name, message):
    """
    Connects and publishes message using ibm-mq client
    """
    conn_str = f"{MQ_CONFIG['host']}({MQ_CONFIG['port']})"

    with MQConnection(
        host=MQ_CONFIG["host"],
        port=int(MQ_CONFIG["port"]),
        channel=MQ_CONFIG["channel"],
        qm=MQ_CONFIG["queue_manager"],
        user=MQ_CONFIG["user"],
        password=MQ_CONFIG["password"]
    ) as mq_conn:

        with mq_conn.open_queue(queue_name, mode="output") as queue:
            queue.put(message)


def process_request(input_data):
    try:
        file_path = input_data.get("filePath")
        source = input_data.get("Source")
        destination = input_data.get("Destination")
        object_name = input_data.get("ObjectName")

        if not file_path:
            raise ValueError("filePath is required")

        if not os.path.exists(file_path):
            raise ValueError("File does not exist")

        filename = os.path.basename(file_path)

        validate_filename(filename)
        queue_name = extract_queue_name(filename)

        validate_properties(source, destination, object_name)

        with open(file_path, "rb") as f:
            file_content = f.read()

        if not file_content:
            raise ValueError("File is empty")

        properties = {
            "Source": source,
            "Destination": destination,
            "ObjectName": object_name,
            "FileName": filename
        }

        message_bytes = json.dumps(properties).encode("utf-8") + b"\n" + file_content

        publish_to_mq(queue_name, message_bytes)

        return {
            "status": "success",
            "queue": queue_name,
            "properties": properties
        }

    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


def main():
    try:
        input_text = sys.stdin.read()
        input_data = json.loads(input_text)
        result = process_request(input_data)
        sys.stdout.write(json.dumps(result))
    except Exception as e:
        sys.stdout.write(json.dumps({
            "status": "error",
            "error": str(e)
        }))


if __name__ == "__main__":
    main()
