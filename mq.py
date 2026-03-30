from flask import Flask, request, jsonify
import pymqi
import re

app = Flask(__name__)

# IBM MQ Config
MQ_CONFIG = {
    "queue_manager": "QM1",
    "channel": "DEV.APP.SVRCONN",
    "host": "localhost",
    "port": "1414",
    "user": "app",
    "password": "password"
}

# Regex for file naming convention
FILE_PATTERN = r"^[A-Za-z0-9._-]+@MQ\.(xml|txt)$"

def connect_mq():
    conn_info = f"{MQ_CONFIG['host']}({MQ_CONFIG['port']})"
    
    cd = pymqi.CD()
    cd.ChannelName = MQ_CONFIG['channel']
    cd.ConnectionName = conn_info
    cd.ChannelType = pymqi.CMQC.MQCHT_CLNTCONN
    cd.TransportType = pymqi.CMQC.MQXPT_TCP

    sco = pymqi.SCO()

    qmgr = pymqi.QueueManager(None)
    qmgr.connect_with_options(
        MQ_CONFIG['queue_manager'],
        user=MQ_CONFIG['user'],
        password=MQ_CONFIG['password'],
        cd=cd,
        sco=sco
    )

    return qmgr


def validate_filename(filename):
    if not re.match(FILE_PATTERN, filename):
        raise ValueError(
            "Invalid file name. Expected format: QueueName@MQ.xml or QueueName@MQ.txt"
        )


def extract_queue_name(filename):
    return filename.split("@MQ")[0]


def validate_properties(source, destination, object_name):
    errors = []

    if not source or len(source) < 2:
        errors.append("Source is required and must be at least 2 characters")

    if not destination or len(destination) < 2:
        errors.append("Destination is required and must be at least 2 characters")

    if not object_name or len(object_name) < 2:
        errors.append("ObjectName is required and must be at least 2 characters")

    # Optional stricter validation
    pattern = r"^[A-Za-z0-9._-]+$"

    for field_name, value in {
        "Source": source,
        "Destination": destination,
        "ObjectName": object_name
    }.items():
        if value and not re.match(pattern, value):
            errors.append(f"{field_name} contains invalid characters")

    if errors:
        raise ValueError(", ".join(errors))


@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        # -------- FILE VALIDATION --------
        if 'file' not in request.files:
            return jsonify({"error": "File is required"}), 400

        file = request.files['file']
        filename = file.filename

        validate_filename(filename)
        queue_name = extract_queue_name(filename)

        # -------- PROPERTY VALIDATION --------
        source = request.form.get('Source')
        destination = request.form.get('Destination')
        object_name = request.form.get('ObjectName')

        validate_properties(source, destination, object_name)

        # -------- FILE CONTENT --------
        file_content = file.read()
        if not file_content:
            return jsonify({"error": "File is empty"}), 400

        # -------- CONNECT MQ --------
        qmgr = connect_mq()
        queue = pymqi.Queue(qmgr, queue_name)

        # -------- MESSAGE DESCRIPTOR --------
        md = pymqi.MD()
        md.Format = pymqi.CMQC.MQFMT_STRING

        # -------- BUILD MESSAGE --------
        properties = {
            "Source": source,
            "Destination": destination,
            "ObjectName": object_name,
            "FileName": filename
        }

        # Convert properties to structured header
        props_str = str(properties)

        message = props_str.encode('utf-8') + b"\n" + file_content

        pmo = pymqi.PMO()
        queue.put(message, md, pmo)

        # -------- CLEANUP --------
        queue.close()
        qmgr.disconnect()

        return jsonify({
            "status": "success",
            "queue": queue_name,
            "properties": properties
        }), 200

    except ValueError as ve:
        return jsonify({
            "status": "validation_error",
            "error": str(ve)
        }), 400

    except pymqi.MQMIError as mq_err:
        return jsonify({
            "status": "mq_error",
            "error": str(mq_err)
        }), 500

    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500


if __name__ == "__main__":
    app.run(port=5000, debug=True)
