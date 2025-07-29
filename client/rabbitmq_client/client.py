import pika
from uuid import uuid4
from protobuf.message_pb2 import Request, Response

# configs
rabbitmq_address = "192.168.31.220"
rabbitmq_port = 5672
queue_name = "requests_queue"
exchange_name = "request_exchange"
routing_key = "request"


# client_queue_name = "clint_unique_queue"

class RabbitMQClient:
    def __init__(self):
        self.client_queue_name = None
        self.channel = None

    def connect(self):
        credentials = pika.PlainCredentials(username="admin", password="password123")
        params = pika.ConnectionParameters(host=rabbitmq_address, port=rabbitmq_port, virtual_host="/",
                                           credentials=credentials)
        connection = pika.BlockingConnection(params)
        self.channel = connection.channel()

        self.client_queue_name = f"client-{uuid4()}"
        self.channel.queue_declare(self.client_queue_name, exclusive=True)
        print("connected")

    def get_answer(self, request_num: int, delay: float = 0.0):
        request_id = str(uuid4())

        request = Request(
            return_address=self.client_queue_name,
            request_id=request_id,
            process_time_in_seconds=delay,
            request=request_num,
        )

        self.channel.basic_publish(
            exchange=exchange_name,
            routing_key=routing_key,
            body=request.SerializeToString(),
            properties=pika.BasicProperties(
                correlation_id=request_id
            )
        )
        print("sent")
        self.channel.basic_consume(
            queue=self.client_queue_name,
            on_message_callback=self.on_response,
            auto_ack=True,
            consumer_tag=request_id,
        )
        self.channel.start_consuming()

    def on_response(self, ch, method, properties, body):
        response = Response()
        response.ParseFromString(body)
        request_id = response.request_id
        print(" [x] Got response:", response.response)
        if properties.correlation_id != request_id:
            print(f"[!] Skipping unrelated response with id: {properties.correlation_id}")
            return  # пропускаем чужие сообщения

        print(" [<] Got response:", response.response)

        # Останавливаем потребление
        ch.basic_cancel(consumer_tag=request_id)
        ch.stop_consuming()


if __name__ == '__main__':
    client = RabbitMQClient()
    client.connect()
    while True:
        num = int(input("num: "))
        delay = float(input("delay: "))
        client.get_answer(num, delay)
