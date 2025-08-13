import unittest
from server.rabbitmq_server.model import RabbitMQServer


class TestDoubleNum(unittest.TestCase):

    def test_double_request(self):
        self.assertEqual(RabbitMQServer.double_request(self, 5), 10)
