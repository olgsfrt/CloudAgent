import os
import logging
from azure.servicebus import ServiceBusClient, ServiceBusMessage

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Environment variables for Service Bus
service_bus_connection_str = os.getenv('AZURE_SERVICE_BUS_CONNECTION_STRING')
queue_name = os.getenv('AZURE_SERVICE_BUS_QUEUE_NAME')

# Initialize Service Bus Client
service_bus_client = ServiceBusClient.from_connection_string(service_bus_connection_str)

def send_message_to_queue(message_content):
    """
    Sends a message to the Azure Service Bus queue.

    :param message_content: The content of the message to send.
    """
    with service_bus_client:
        sender = service_bus_client.get_queue_sender(queue_name)
        with sender:
            message = ServiceBusMessage(message_content)
            sender.send_messages(message)
            logging.info(f"Sent message: {message_content}")

def receive_message_from_queue(max_message_count=1, max_wait_time=5):
    """
    Receives messages from the Azure Service Bus queue.

    :param max_message_count: Maximum number of messages to receive.
    :param max_wait_time: Maximum time to wait for a message.
    :return: List of received messages.
    """
    messages = []
    with service_bus_client:
        receiver = service_bus_client.get_queue_receiver(queue_name)
        with receiver:
            for msg in receiver.receive_messages(max_message_count=max_message_count, max_wait_time=max_wait_time):
                logging.info(f"Received message: {msg}")
                messages.append(msg)
                receiver.complete_message(msg)
    return messages

def main():
    # Example usage of the Service Bus functions
    test_message_content = 'Hello, World!'
    
    # Send a message to the queue
    send_message_to_queue(test_message_content)
    
    # Receive messages from the queue
    received_messages = receive_message_from_queue()
    for message in received_messages:
        print(f"Message received: {message}")

if __name__ == "__main__":
    main()
