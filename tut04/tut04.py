
from datetime import datetime
from copy import deepcopy
import queue
import threading
import time

start_time = datetime.now()

# Parse the network topology from the input file
with open('topology.txt', 'r') as f:
    num_routers = int(f.readline().strip())
    router_names = f.readline().split()
    cost_matrix = {}
    for line in f:
        if line.strip() == 'EOF':
            break
        src, dest, cost = line.strip().split()
        cost_matrix[(src, dest)] = int(cost)
        cost_matrix[(dest, src)] = int(cost)

# Initialize a dictionary to keep track of which routers are adjacent to each router
adjacent_routers = {}
for router in router_names:
    adjacent_routers[router] = [neighbor for neighbor in router_names if cost_matrix.get((router, neighbor)) is not None]

# Initialize the routing table for each router
routing_tables = {}
for router in router_names:
    routing_tables[router] = {router: {'dist': 0, 'next_hop': router}}
    for neighbor in router_names:
        if neighbor != router:
            routing_tables[router][neighbor] = {'dist': float('inf'), 'next_hop': '-'}

# Initialize a queue and convergence check variable for each router
queues = {}
conv_check = {}
for router in router_names:
    queues[router] = queue.Queue()
    conv_check[router] = False

# Initialize a table to keep track of the previous costs for each destination for each routing table
previous_costs = deepcopy(routing_tables)

print_lock = threading.Lock()

send_lock = {}
for router in router_names:
    send_lock[router] = threading.Lock()

def check_convergence(threshold=0):
    for router in router_names:
        if conv_check[router] == False:
            return False
    return True

# Define a function to send updates to adjacent routers
def send_updates(router):
    while True:
        # Wait for 2 seconds before broadcasting the routing table to all adjacent routers
        time.sleep(2)
        for neighbor in adjacent_routers[router]:
            # Lock to ensuring that same routers routing table is not forwarded while neighbour's routing table is being updated
            send_lock[neighbor].acquire(blocking=False)   
            # Send the routing table to the adjacent router's queue
            queues[neighbor].put((router, routing_tables[router]))
            send_lock[neighbor].release()
        if check_convergence():
            break

# Define a function to receive updates from adjacent routers and update the routing table
def receive_updates(router, adjacent_routers):
    iteration = 0
    while True:
        # Wait until all adjacent routers have sent their routing tables
        while queues[router].qsize() < len(adjacent_routers[router]):
            time.sleep(1)

        send_lock[router].acquire()
        # Combine the received routing tables and update the routing table for the current router
        updated = False

        # Update routing table using Bellman Ford equation
        while not queues[router].empty():
            (neighbor, received_table) = queues[router].get()
            for dest, value in received_table.items():
                if router == dest:
                    continue
                new_cost = cost_matrix[(router, neighbor)] + value['dist']
                if new_cost < routing_tables[router][dest]['dist']:
                    routing_tables[router][dest]['dist'] = new_cost
                    routing_tables[router][dest]['next_hop'] = neighbor
                    updated = True

        if not updated:
            conv_check[router] = True
        
        # If the routing table was updated, display it
        print_lock.acquire()
        iteration += 1
        print(f"Iteration {iteration}:")
        displayRoutingTable(router)
        print_lock.release()

        send_lock[router].release()

        if check_convergence():
            break

        time.sleep(2)
        

def displayRoutingTable(router):
    print(f"Routing table for router {router}")
    headers = ['Destination', 'Distance', 'Next Hop']

    format_row = ""
    for head in headers:
        format_row += ('{'+f':>{len(head)+3}'+'}')
    print(format_row.format(*headers))
    for dest, value in routing_tables[router].items():
        cost = value['dist']
        next_hop = value['next_hop']
        if dest == router or router == next_hop:
            continue                
        if dest not in previous_costs[router] or previous_costs[router][dest]['dist'] != cost:
            print(format_row.format(dest, cost, next_hop), '*')
        else:
            print(format_row.format(dest, cost, next_hop))
    print()
    previous_costs[router] = deepcopy(routing_tables[router])


def dvr():
    print("Initial routing tables: ")
    for router in router_names:
        displayRoutingTable(router)

    # Start a thread for each router
    router_threads = []
    for router in router_names:
        t = threading.Thread(target=send_updates, args=(router,))
        t.start()
        router_threads.append(t)

    # Start a thread for each router to receive updates from adjacent routers
    for router in router_names:
        t = threading.Thread(target=receive_updates, args=(router, adjacent_routers, ))
        t.start()
        router_threads.append(t)

    # Wait for all threads to complete
    for t in router_threads:
        t.join()

dvr()

#This shall be the last lines of the code.
end_time = datetime.now()
print('Duration of Program Execution: {}'.format(end_time - start_time))
