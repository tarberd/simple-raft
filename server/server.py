import socket
import sys
import time
import asyncio

def serve(connection):
    print('Start serving')
    while True:
        connection.send(str.encode('heartbeat\n'))
        time.sleep(5)

def receive(connection):
    print('Start receiving')
    while True:
        data = connection.recv(2048)
        if not data:
            break
        print('received:', data.decode('utf-8'))

server_hostname_list = ['alce', 'baleia']

server_hostname_to_ip = {}
server_ip_to_hostname = {}

for host in server_hostname_list:
    server_hostname_to_ip[host] = socket.gethostbyname(host)
    server_ip_to_hostname[socket.gethostbyname(host)] = host

print(server_hostname_to_ip)

my_ip_address = socket.gethostbyname(socket.gethostname())

print('I am:', server_ip_to_hostname[my_ip_address])
print('I am at:', my_ip_address)

del server_ip_to_hostname[my_ip_address]

other_nodes_ips = []

for ip, hostname in server_ip_to_hostname.items():
    other_nodes_ips.append(ip)

print(other_nodes_ips)

async def tcp_echo_client(message, host, port):
    reader, writer = await asyncio.open_connection(host, port)

    print(f'Send: {message!r}')
    writer.write(message.encode())

    data = await reader.read(100)
    print(f'Received: {data.decode()!r}')

    print('Close the connection')
    writer.close()
    await writer.wait_closed()

async def handle_echo(reader, writer):
    data = await reader.read(100)
    message = data.decode()
    addr = writer.get_extra_info('peername')

    print(f"Received {message!r} from {addr!r}")

    print(f"Send: {message!r}")
    writer.write(data)
    await writer.drain()

    print("Close the connection")
    writer.close()

async def main():
    server = await asyncio.start_server(handle_echo, '0.0.0.0', 5555)

    addr = server.sockets[0].getsockname()
    print(f'Serving on {addr}')

    async with server:
        await server.serve_forever()

asyncio.run(main())
asyncio.run(tcp_echo_client('hy',other_nodes_ips[0],5555))
