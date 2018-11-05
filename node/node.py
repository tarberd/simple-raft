import socket, sys, time, asyncio, json, random

class Timeout:
    @staticmethod
    def election():
        return random.randint(150, 300)/1000


class Timer:
    def __init__(self, timeout, callback):
        self._timeout = timeout
        self._callback = callback
        self._task = asyncio.ensure_future(self._job())

    async def _job(self):
        print("begin job, sleep:", self._timeout)
        await asyncio.sleep(self._timeout)
        print("after sleep")
        await self._callback()
        print("after callback")

    def cancel(self):
        self._task.cancel()

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
    def request_vote(term_num):
        return Message('request_vote', {'term_num': term_num})

    @staticmethod
    def grant_vote(term_num):
        return Message('grant_vote', {'term_num': term_num})

class ElectionTerm:
    total = 0
    def __init__(self, candidates):
        self.number = ElectionTerm.total
        ElectionTerm.total += 1
        self.candidates = candidates
        self.candidates_to_vote_count = {candidate: 0 for candidate in candidates}
    
    def vote(self, candidate):
        self.candidates_to_vote_count[candidate] +=1
    
    def vote_count(self, candidate):
        return self.candidates_to_vote_count[candidate]
    
    def elected(self):
        return max(self.candidates_to_vote_count, key=self.candidates_to_vote_count.get)

class Node:
    def __init__(self, nodes_names):
        all_nodes_dict = {socket.gethostbyname(name): name for name in nodes_names}
        self.all_nodes = list(all_nodes_dict)
        self.other_nodes = all_nodes_dict.copy()
        self.ip = socket.gethostbyname(socket.gethostname())
        del self.other_nodes[self.ip]
        self.other_nodes = list(self.other_nodes)
        self.name = all_nodes_dict[self.ip]
        self.state = State.FOLLOWER
        self.election_timer = 0
        self.election_term = ElectionTerm(self.all_nodes)

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
        print('peername',reader.get_extra_info('peername'))
        return msg

    @staticmethod
    async def send_message(msg, writer):
        writer.write(msg.to_json().encode())
        await writer.drain()
    
    async def broadcast(self, msg):
        for other in self.other_nodes:
            await self.request(msg, other)
    
    async def become_candidate(self):
        print("Becoming candidate")
        self.state = State.CANDIDATE
        self.election_term = ElectionTerm(self.all_nodes)
        self.election_term.vote(self.ip)

        print("Requesting votes")
        vote_req = Message.request_vote(self.election_term.number)
        await self.broadcast(vote_req)
        print("Became candidate")

    def new_election_timer(self):
        return Timer(Timeout.election(), self.become_candidate)

    def reset_election_timer(self):
        print("Resetting election timer")
        self.election_timer.cancel()
        self.election_timer = self.new_election_timer()

    async def handler(self, reader, writer):
        msg = await Node.get_message(reader)

        if self.state == State.FOLLOWER:
            if msg.type == 'request_vote':
                print("got request_vote")
                
                sender_term_num = msg.data["term_num"]

                self.election_term = ElectionTerm(sender_term_num)

                to_send = Message.grant_vote(sender_term_num)
                await Node.send_message(to_send, writer)
            else:
                print("outra coisa", msg.type)
        
        to_send = Message('response')
        await Node.send_message(to_send, writer)
        writer.close()

    async def loop(self):
        while True:
            if self.state == State.LEADER:
                pass
            elif self.state == State.FOLLOWER:
                pass
            elif self.state == State.CANDIDATE:
                pass

    def run(self):
        loop = asyncio.get_event_loop()
        loop.create_task(asyncio.start_server(self.handler, '0.0.0.0', 5555))
        loop.create_task(self.loop())

        loop.run_forever()

       



server_hostname_list = ['alce', 'baleia']

node = Node(server_hostname_list)

print('I am:', node.name)
print('I am at:', node.ip)

print('Other nodes:', node.other_nodes)

node.run()