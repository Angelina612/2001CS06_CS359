
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

# Initialize a table to keep track of the previous costs for each destination for each routing table
previous_costs = deepcopy(routing_tables)

# To synchronize access to console output
print_lock = threading.Lock()

def compute_shortest_path(router):
    # Initialize the distance and predecessor tables
    dist = {router: 0}
    pred = {router: None}
    unvisited = set(router_names)

    for dest in unvisited:
        if dest == router:
            continue
        dist[dest] = float('inf')
        pred[dest] = None

    # Main loop
    while unvisited:
        # Find the unvisited node with the shortest distance
        current = min(unvisited, key=lambda x: dist[x])
        unvisited.remove(current)

        # Update the distance and predecessor tables for each neighbor of the current node
        for neighbor in adjacent_routers[current]:
            if neighbor in unvisited:
                new_cost = dist[current] + cost_matrix[(current, neighbor)]
                if new_cost < dist[neighbor]:
                    dist[neighbor] = new_cost
                    pred[neighbor] = current

    # Return the computed shortest path
    return pred, dist

update_lock = threading.Lock()

def update_routing_table(router):
    pred, dist = compute_shortest_path(router)

    routing_table = routing_tables[router]

    update_lock.acquire()
    for current, distance in dist.items():
        routing_table[current]['dist'] = distance

    for dest in dist:
        if dest != router:
            next_hop = None
            current = dest
            while pred[current] != router:
                current = pred[current]
            next_hop = current
            routing_table[dest]['next_hop'] = next_hop
    
    update_lock.release()

    print_lock.acquire()
    print('Final ', end='')
    displayRoutingTable(router)
    print_lock.release()


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

def lsr():
    print("Initial routing tables: ")
    for router in router_names:
        displayRoutingTable(router)

    # Start a thread for each router
    router_threads = []
    for router in router_names:
        t = threading.Thread(target=update_routing_table, args=(router,))
        t.start()
        router_threads.append(t)

    # Wait for all threads to complete
    for t in router_threads:
        t.join()

lsr()

#This shall be the last lines of the code.
end_time = datetime.now()
print('Duration of Program Execution: {}'.format(end_time - start_time))
