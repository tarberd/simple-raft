import socket, sys, time, asyncio, json, random

class Timeout:
    @staticmethod
    def election():
        if socket.gethostbyname(socket.gethostname()) == '172.19.0.3':
            return 2
        return random.randint(150, 300)/1000

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
    def vote(term_num, candidate):
        return Message('vote', {'term_num': term_num, 'candidate': candidate})
    
    def __str__(self):
        return f"type: {self.type} | data:{self.data}"

class ElectionTerm:
    def __init__(self, candidates, number):
        self.number = number
        self.candidates = candidates
        self.candidates_to_vote_count = {candidate: 0 for candidate in candidates}
    
    def vote(self, candidate):
        print(candidate, candidate in self.candidates_to_vote_count ,self.candidates_to_vote_count)
        self.candidates_to_vote_count[candidate] +=1
        print(self.candidates_to_vote_count)
    
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
        self.election_term = ElectionTerm(self.all_nodes, 0)

    async def request(self, message, host, port=5555):
        print("requesting msg:", message)
        while True:
            try:
                reader, writer = await asyncio.open_connection(host, port)
                break
            except:
                pass

        await Node.send_message(message, writer)

        response, _ = await Node.get_message(reader, writer)
        writer.close()
        await writer.wait_closed()
        return response

    @staticmethod
    async def get_message(reader, writer):
        data = await reader.read(1024)
        decoded = data.decode()
        if decoded != '':
            msg = Message.from_json(decoded)
            ip = writer.get_extra_info('peername')[0]
            return (msg, ip)
        return (None, None)

    @staticmethod
    async def send_message(msg, writer):
        writer.write(msg.to_json().encode())
        await writer.drain()
    
    async def broadcast(self, msg):
        for other in self.other_nodes:
            await self.request(msg, other)
    
    async def become_candidate(self):
        await asyncio.sleep(Timeout.election())

        print("Becoming candidate")
        self.state = State.CANDIDATE
        self.election_term = ElectionTerm(self.all_nodes, self.election_term.number+1)
        self.election_term.vote(self.ip)

        print("Requesting votes")
        vote_req = Message.request_vote(self.election_term.number)
        await self.broadcast(vote_req)
        print("Became candidate")

    async def handler(self, reader, writer):
        msg, remote_ip = await Node.get_message(reader, writer)
        if msg == None:
            return
        print(msg)
        if self.state == State.CANDIDATE:
            print("i am candidate, msg:", msg)
            if msg.type == 'vote':
                voted_candidate = msg.data["candidate"]
                self.election_term.vote(voted_candidate)
            elif msg.type == 'request_vote':
                sender_term_num = msg.data["term_num"]
                to_send = Message.vote(sender_term_num, self.ip)
                await self.request(to_send, remote_ip)

        elif self.state == State.FOLLOWER:
            print("i am follower, msg:", msg)
            if msg.type == 'request_vote':
                self.election_task.cancel()
                print("got request_vote")
                
                sender_term_num = msg.data["term_num"]

                self.election_term = ElectionTerm(self.all_nodes, sender_term_num)
                self.election_term.vote(remote_ip) # follower vote
                self.election_term.vote(remote_ip) # candidate's vote


                to_send = Message.vote(sender_term_num, remote_ip)
                await self.request(to_send, remote_ip)
                print("sent msg", to_send)
            elif msg.type == 'heartbeat':
                self.election_task.cancel()
            else:
                print("outra coisa", msg.type)
        writer.close()

    def run(self):
        loop = asyncio.get_event_loop()
        loop.create_task(asyncio.start_server(self.handler, '0.0.0.0', 5555))
        self.election_task = loop.create_task(self.become_candidate())

        loop.run_forever()

       



server_hostname_list = ['alce', 'baleia']

node = Node(server_hostname_list)

print('I am:', node.name)
print('I am at:', node.ip)

print('Other nodes:', node.other_nodes)

node.run()