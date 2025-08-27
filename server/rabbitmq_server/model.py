import asyncio
import logging
import aio_pika
from aio_pika import exceptions
from server.rabbitmq_server.protobuf.message_pb2 import Response, Request


def setup_logger(level=logging.INFO, filename='server.log'):
    logger = logging.getLogger('RabbitMQServer')
    logger.setLevel(level)
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")

    # Handler для логов в файл
    file_handler = logging.FileHandler(filename, mode='w', encoding='UTF-8')
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Handler для логов в консоль
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger


class RabbitMQServer:
    def __init__(self, settings):
        logging_level = settings['Logging'].get('level', 'INFO')
        logging_filepath = settings['Logging'].get('filepath')
        self.logger = setup_logger(logging_level, logging_filepath)

        self.con_address = settings['Server']['host']
        self.con_port = int(settings['Server'].get('port', 5672))
        self.login = settings['Server'].get('login')
        self.password = settings['Server'].get('password')

        self.queue_name = settings['Server']['queue_name']
        self.exchange_name = settings['Server']['exchange_name']
        self.routing_key = settings['Server']['routing_key']
        self.reconnect_timeout = 5
        self.channel = None

    async def connect(self) -> None:
        while True:
            try:
                self.logger.info('Попытка подключения')
                connection = await aio_pika.connect_robust(host=self.con_address, port=self.con_port,
                                                           login=self.login,
                                                           password=self.password,
                                                           )
                async with connection:
                    self.channel = await connection.channel()
                    queue = await self.channel.declare_queue(self.queue_name, durable=True)
                    exchange = await self.channel.declare_exchange(self.exchange_name, aio_pika.ExchangeType.DIRECT,
                                                                   durable=True)
                    await queue.bind(exchange, self.routing_key)
                    self.logger.info('Успешно подключено')

                    await queue.consume(self.on_request)
                    await asyncio.Future()

            except exceptions.CONNECTION_EXCEPTIONS as e:
                self.logger.warning(f'Ошибка подключения, {e}')
                await asyncio.sleep(self.reconnect_timeout)

    async def on_request(self, message: aio_pika.IncomingMessage) -> None:
        async with message.process():
            request = Request()
            request.ParseFromString(message.body)
            self.logger.info(
                f'Входящее сообщение: {request.request}, id: {request.request_id}, return@: {request.return_address}')
            delay = request.process_time_in_seconds
            if delay:
                await asyncio.sleep(delay)
                self.logger.info(f'Delayed: {delay}')
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
            self.logger.info(
                f'Ответ отправлен: {response_num}, id: {request.request_id}, return@: {request.return_address}')

    def double_request(self, request: int) -> int:
        return request * 2

    def start(self) -> None:
        asyncio.run(self.connect())
