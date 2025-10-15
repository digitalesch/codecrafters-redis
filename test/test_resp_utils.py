# test/test_resp_utils.py
import socket
from app import main

REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379

# --- TEST UTILS ---

def clear_key_before_test():
    send_raw_redis_command(["RESET"])

def send_raw_redis_command(command: list[str]) -> str:
    with socket.create_connection((REDIS_HOST, REDIS_PORT), timeout=3) as sock:
        sock.sendall(main.encode_resp_command(command))
        data = sock.recv(4096)
        return data
    
def use_multiple_commands(args: tuple[list,bytes]):
    clear_key_before_test()

    for command, expected_response in args:
        response = send_raw_redis_command(command)
        assert response == expected_response

# --- ACTUAL TESTS, functions that start with test_XXXX ---

def test_simple_ping():
    response = send_raw_redis_command(["PING"])
    assert response == b'+PONG\r\n'

def test_dual_rpush():
    args = [
        (["RPUSH","list_key","banana","pear","pineapple","nstrawberry","nblueberry"], b':5\r\n'),
        (["RPUSH","list_key","test","test2"], b':7\r\n')
    ]

    use_multiple_commands(args)

def test_ping_rpush__get():
    args = [
        (["PING"],b'+PONG\r\n'),
        (["RPUSH","list_key","banana","pear","pineapple","strawberry","blueberry"], b':5\r\n'),
        (["GET","list_key"], b'*5\r\n$6\r\nbanana\r\n$4\r\npear\r\n$9\r\npineapple\r\n$10\r\nstrawberry\r\n$9\r\nblueberry\r\n')
    ]

    use_multiple_commands(args)