import pytest
from src.client import Client


def test_client(mocker):
    mocker.patch.object(Client, "get_robot_state")
    client = Client("192.168.11.17:8000")
    client.get_robot_state()
