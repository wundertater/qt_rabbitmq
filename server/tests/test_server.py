import os
import unittest
import asyncio
import aio_pika
from server.rabbitmq_server.protobuf.message_pb2 import Request, Response
from server.rabbitmq_server.model import RabbitMQServer


class TestRabbitMQServer(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        # Настройки для теста
        self.settings = {
            "Logging": {
                "level": "INFO",
                "filepath": "test.log"
            },
            "Server": {
                "host": os.getenv("RABBITMQ_HOST", "localhost"),
                "port": int(os.getenv("RABBITMQ_PORT", 5672)),
                "queue_name": "test_queue",
                "exchange_name": "test_exchange",
                "routing_key": "test_key"
            }
        }

        self.server = RabbitMQServer(self.settings)

        # Запускаем сервер в отдельной задаче
        self.server_task = asyncio.create_task(self.server.connect())

        # Подключение клиента
        self.client_connection = await aio_pika.connect_robust(
            host=os.getenv("RABBITMQ_HOST", "localhost"),
            port=int(os.getenv("RABBITMQ_PORT", 5672)),
        )

        self.client_channel = await self.client_connection.channel()

        # ждём пока сервер создаст exchange
        for _ in range(20):  # максимум 20 попыток
            try:
                await self.client_channel.get_exchange(self.settings["Server"]["exchange_name"])
                break
            except Exception:
                await asyncio.sleep(0.5)  # ждём полсекунды и пробуем снова
        else:
            raise TimeoutError("Не удалось дождаться запуска сервера")

        # Временная очередь для ответа
        self.callback_queue = await self.client_channel.declare_queue(exclusive=True)

    async def asyncTearDown(self):
        self.server_task.cancel()
        await self.client_connection.close()

    async def test_simple_request_response(self):
        # Формируем запрос
        request = Request(
            request_id="123",
            request=5,
            return_address=self.callback_queue.name
        )

        # Берём exchange, который сервер объявил
        exchange = await self.client_channel.get_exchange("test_exchange")

        # Отправляем запрос туда
        await exchange.publish(
            aio_pika.Message(body=request.SerializeToString()),
            routing_key="test_key"
        )

        # Ждём ответа
        incoming = await self.callback_queue.get(timeout=5)
        response = Response()
        response.ParseFromString(incoming.body)

        # Проверяем результат
        self.assertEqual(response.request_id, "123")
        self.assertEqual(response.response, 10)


if __name__ == "__main__":
    unittest.main()
