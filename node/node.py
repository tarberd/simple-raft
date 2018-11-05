import socket, sys, time, asyncio, json, random

class State:
    FOLLOWER = 1
    CANDIDATE = 2
    LEADER = 3

class Message:
    def __init__(self, t, d=''):
        self.type = t
        self.data = d
    
    def to_json(self):
        return json.dumps({"type":self.type, "data":self.data})

    @staticmethod
    def from_json(msg):
        decoded = json.loads(msg)
        return Message(decoded["type"], decoded["data"])

    @staticmethod
    def heartbeat():
        return Message('heartbeat')

class Node:
    def __init__(self, nodes_names):
        all_nodes = {socket.gethostbyname(name): name for name in nodes_names}
        self.other_nodes = all_nodes.copy()
        self.ip = socket.gethostbyname(socket.gethostname())
        del self.other_nodes[self.ip]
        self.other_nodes = list(self.other_nodes)
        self.name = all_nodes[self.ip]
        self.state = State.FOLLOWER

    async def request(self, message, host, port=5555):
        while True:
            try:
                reader, writer = await asyncio.open_connection(host, port)
                break
            except:
                pass

        await Node.send_message(message, writer)

        message = await Node.get_message(reader)
        writer.close()
        await writer.wait_closed()
        return message

    @staticmethod
    async def get_message(reader):
        data = await reader.read(100)
        msg = Message.from_json(data.decode())
        return msg

    @staticmethod
    async def send_message(msg, writer):
        writer.write(msg.to_json().encode())
        await writer.drain()

    async def handler(self, reader, writer):
        msg = await Node.get_message(reader)

        if msg.type == 'heartbeat':
            print("HEARTBEAT CRL")
        else:
            print("outra coisa", msg.type)

        to_send = Message('response')
        await Node.send_message(to_send, writer)
        writer.close()

    async def tick(self):
        def tick_sleep():
            return random.randint(150, 450)/1000
        while True:
            await asyncio.sleep(tick_sleep())
            for other in self.other_nodes:
                await self.request(Message.heartbeat(), other)

    def run(self):
        loop = asyncio.get_event_loop()
        loop.create_task(asyncio.start_server(self.handler, '0.0.0.0', 5555))
        loop.create_task(self.tick())

        loop.run_forever()



server_hostname_list = ['alce', 'baleia']


node = Node(server_hostname_list)
print('I am:', node.name)
print('I am at:', node.ip)


print(node.other_nodes)

node.run()