import boto3
import json
from decimal import Decimal

# DynamoDB and IoT clients
dynamodb = boto3.resource("dynamodb")
client = boto3.client("iot-data")
table = dynamodb.Table("PrinterProfiles")

# SNS client + topic
sns = boto3.client("sns")
SNS_TOPIC_ARN = "arn:aws:sns:REGION:ACCOUNT_ID:PrinterAnomaliesTopic"  # update this

def lambda_handler(event, context):
    # Normalize case for PrinterId
    device_id = event.get("PrinterId").capitalize()
    sensor_value = event["data"]["value"]

    # Fetch the device profile from DynamoDB
    response = table.get_item(Key={"PrinterId": device_id})

    if "Item" in response:
        device_profile = response["Item"]
        print(f"Device profile fetched: {device_profile}")

        lower_threshold = float(device_profile["Thresholds"]["Lower"])
        upper_threshold = float(device_profile["Thresholds"]["Upper"])
        time_window = int(device_profile["Window"])

        print(f"Processing {device_id} with sensor value: {sensor_value}")
        print(f"Current OutOfBoundsCount: {device_profile['OutOfBoundsCount']}")
        print(f"EventCount before processing: {device_profile.get('EventCount', 0)}")

        # Check anomaly condition
        is_out_of_bounds = sensor_value < lower_threshold or sensor_value > upper_threshold

        # Update OutOfBoundsCount
        if is_out_of_bounds:
            device_profile["OutOfBoundsCount"] = int(device_profile.get("OutOfBoundsCount", 0)) + 1
        else:
            device_profile["OutOfBoundsCount"] = 0

        # If anomaly sustained long enough → trigger event
        if device_profile["OutOfBoundsCount"] >= time_window:
            device_profile["EventCount"] = int(device_profile.get("EventCount", 0)) + 1
            device_profile["OutOfBoundsCount"] = 0
            iot_and_sns_publish(device_id, device_profile)

        # Persist updates in DynamoDB
        response = table.update_item(
            Key={"PrinterId": device_id},
            UpdateExpression="SET OutOfBoundsCount = :oob, EventCount = :ec",
            ExpressionAttributeValues={
                ":oob": device_profile["OutOfBoundsCount"],
                ":ec": device_profile["EventCount"]
            },
            ReturnValues="UPDATED_NEW"
        )
        print(f"Update response: {response}")

    print("Current device processing complete. Generating output:")
    generate_output()
    
    return {"status": "processed"}

def iot_and_sns_publish(device_id, new_record):
    event_count = int(new_record["EventCount"])
    payload = {"PrinterId": device_id, "events": event_count}

    # Republish anomaly to IoT Core
    client.publish(topic="anom/pred", qos=1, payload=json.dumps(payload))

    # Send alert to SNS
    sns.publish(
        TopicArn=SNS_TOPIC_ARN,
        Subject="🚨 Printer Anomaly Detected",
        Message=json.dumps(payload)
    )
    print(f"SNS alert sent for {device_id}")

def generate_output():
    response = table.scan()
    devices = response.get("Items", [])
    sorted_devices = sorted(devices, key=lambda d: int(d["EventCount"]), reverse=True)

    output = [(device["PrinterId"], int(device["EventCount"])) for device in sorted_devices]

    print("Sorted output (PrinterId, EventCount):")
    for device_id, event_count in output:
        print(f"{device_id}, {event_count}")
    
    return output