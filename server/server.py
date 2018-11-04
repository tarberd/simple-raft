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

#  print('start')
#  while True:
#      their soc  = 0
#      start_new_thread(connect_to, ())
#
#      connection, address = sock.accept()
#      print('connected to: ' + address[0] + ':' + str(address[1]))
#
#      start_new_thread(serve, (connection,))
#      start_new_thread(receive, (connection,))

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
