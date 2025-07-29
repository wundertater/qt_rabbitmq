import asyncio
import aio_pika
from aio_pika import exceptions
from protobuf.message_pb2 import Response, Request

# configs
rabbitmq_address = "192.168.31.220"
rabbitmq_port = 5672
queue_name = "requests_queue"
exchange_name = "request_exchange"
routing_key = "request"


class RabbitMQServer:
    def __init__(self, rabbitmq_address, rabbitmq_port):
        self.con_address = rabbitmq_address
        self.con_port = rabbitmq_port
        self.reconnect_timeout = 5

        self.channel = None

    async def connect(self) -> None:
        while True:
            try:
                connection = await aio_pika.connect_robust(host=self.con_address, port=self.con_port,
                                                           login='admin',
                                                           password='password123',
                                                           virtualhost='/'
                                                           )
                async with connection:
                    self.channel = await connection.channel()
                    queue = await self.channel.declare_queue(queue_name, durable=True)
                    exchange = await self.channel.declare_exchange(exchange_name, aio_pika.ExchangeType.DIRECT,
                                                                   durable=True)
                    await queue.bind(exchange, routing_key)

                    print("Подключено")
                    await queue.consume(self.on_request)
                    await asyncio.Future()

            except exceptions.CONNECTION_EXCEPTIONS as e:
                print("reconnect", e)
                await asyncio.sleep(self.reconnect_timeout)

    async def on_request(self, message: aio_pika.IncomingMessage) -> None:
        async with message.process():
            request = Request()
            request.ParseFromString(message.body)
            print("get message", request.request)
            delay = request.process_time_in_seconds
            if delay:
                await asyncio.sleep(delay)
                print("delayed")
            response_num = self.double_request(request.request)
            response = Response(
                request_id=request.request_id,
                response=response_num,
            )

            await self.channel.default_exchange.publish(
                aio_pika.Message(
                    body=response.SerializeToString(),
                    correlation_id=request.request_id,
                ),
                routing_key=request.return_address
            )
            print("sent back")

    def double_request(self, request) -> int:
        return request * 2

    def start(self) -> None:
        asyncio.run(self.connect())


serv = RabbitMQServer(rabbitmq_address, rabbitmq_port)
serv.start()
