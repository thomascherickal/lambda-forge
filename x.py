import json
import time
import boto3
import click

from lambda_forge.live_iam import LiveIAM
from lambda_forge.printer import Printer


class LiveSQS:
    def __init__(self, region, printer):
        self.sqs = boto3.client("sqs", region_name=region)
        self.iam = LiveIAM(region)
        self.iam_client = boto3.client('iam', region_name=region)
        self.printer = printer
        self.lambda_client = boto3.client("lambda", region_name=region)
        self.queue_url = self.sqs.create_queue(QueueName="Live-Queue")["QueueUrl"]

    def subscribe(self, function_arn, stub_name):
        self.printer.change_spinner_legend("Setting up Lambda Trigger for SQS Queue")

        try:
            response = self.sqs.get_queue_attributes(QueueUrl=self.queue_url, AttributeNames=["QueueArn"])
            queue_arn = response["Attributes"]["QueueArn"]

            policy = {"Version": "2012-10-17", "Statement": [{"Effect": "Allow", "Action": "sqs:*", "Resource": "*"}]}
            
            self.iam = self.iam.attach_policy_to_lambda(policy, function_arn)
            
            self.sqs.set_queue_attributes(
                QueueUrl=self.queue_url,
                Attributes={'VisibilityTimeout': "900"}
            )
       
            self.lambda_client.create_event_source_mapping(
                EventSourceArn=queue_arn,
                FunctionName=function_arn,
            )
            self.printer.print("Successfully subscribed Lambda to SQS Queue.", "green")
            return queue_arn
        except Exception as e:
            self.printer.print(f"Error setting up Lambda trigger: {str(e)}", "red")
            return None

    def publish(self, subject, msg_attributes):
        self.printer.show_banner("SQS")
        self.printer.print(f"Subject: {subject}", "white", 1)
        self.printer.print(f"Message Attributes: {msg_attributes}", "white", 1, 1)

        message_attributes = {}
        if msg_attributes:
            try:
                message_attributes = json.loads(msg_attributes)
                if not isinstance(message_attributes, dict):
                    self.print_failure(self.printer)
                    exit()
            except:
                self.print_failure(self.printer)
                exit()

        message = click.prompt(click.style("Message", fg=(37, 171, 190)), type=str)
        try:
            self.sqs.send_message(QueueUrl=self.queue_url, MessageBody=message, MessageAttributes=message_attributes)
        except:
            self.print_failure(self.printer)

    @staticmethod
    def print_failure(printer):
        printer.print("Failed to Publish Message!", "red")
        printer.print("Example of a Valid Payload: ", "gray", 1)
        payload = {
            "message": "Hello World!",
            "subject": "Hello World!",
            "message_attributes": {"Author": {"StringValue": "Daniel", "DataType": "String"}},
        }
        printer.print(json.dumps(payload, indent=4), "gray", 1, 1)

    @staticmethod
    def parse_prints(event):
        record = event["Records"][0]
        message_body = record["body"]
        message_attributes = record.get("messageAttributes", {})

        return {
            "Records": [
                {
                    "body": message_body,
                    "messageAttributes": message_attributes,
                }
            ]
        }



