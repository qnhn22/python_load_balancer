import random
from itertools import cycle
import hashlib
import requests
import logging
import time
import threading


class LoadBalancer:
    def __init__(self):
        self.all_servers = {
            "http://backend1:8001": {"weight": 3, "healthy": True, "failures": 0, "connections": 0, "response_time": random.uniform(0.1, 0.3)},
            "http://backend2:8002": {"weight": 2, "healthy": True, "failures": 0, "connections": 0, "response_time": random.uniform(0.1, 0.3)},
            "http://backend3:8003": {"weight": 1, "healthy": True, "failures": 0, "connections": 0, "response_time": random.uniform(0.1, 0.3)}
        }
        self.healthy_servers = {k: v for k,
                                v in self.all_servers.items() if v["healthy"]}
        self.unhealthy_servers = {}
        self.servers = list(self.healthy_servers.keys())
        self.backend_cycle = cycle(self.servers)  # For round robin
        self.MAX_FAILURES = 2  # Max consecutive failures to mark as unhealthy
        self.HEALTH_CHECK_INTERVAL = 10
        self.lock = threading.Lock()  # Lock for thread safety

    def update_load_balancer(self):
        while True:
            with self.lock:
                for server, fields in self.all_servers.items():
                    try:
                        response = requests.get(f"{server}/health", timeout=2)
                        if response.status_code == 200:
                            fields["failures"] = 0
                            fields["healthy"] = True
                            if server in self.unhealthy_servers:
                                logging.info(
                                    f"{server} recovered, adding back to healthy pool.")
                                self.healthy_servers[server] = fields
                                del self.unhealthy_servers[server]
                                self.servers = list(
                                    self.healthy_servers.keys())
                                self.backend_cycle = cycle(self.servers)
                    except requests.RequestException:
                        fields["failures"] += 1
                        if fields["failures"] >= self.MAX_FAILURES:
                            fields["healthy"] = False
                            if server in self.healthy_servers:
                                logging.warning(
                                    f"{server} failed health check, removing from pool.")
                                self.unhealthy_servers[server] = fields
                                del self.healthy_servers[server]
                                self.servers = list(
                                    self.healthy_servers.keys())
                                self.backend_cycle = cycle(self.servers)
            time.sleep(self.HEALTH_CHECK_INTERVAL)

    def route_request(self, algorithm, ip):
        if algorithm == "round_robin":
            return self.round_robin()
        elif algorithm == "least_connections":
            return self.least_connections()
        elif algorithm == "source_ip_hash":
            return self.source_ip_hash(ip)  # Example IP
        elif algorithm == "weighted_round_robin":
            return self.weighted_round_robin()
        elif algorithm == "random":
            return self.random_choice()
        else:
            raise ValueError("Unknown load balancing algorithm")

    # This is one of the simplest load balancing algorithms. It distributes incoming requests sequentially among all
    # available servers. Each server is assigned a request in turn, cycling back to the first server after the last
    # one is reached.
    def round_robin(self):
        return next(self.backend_cycle)

    # This algorithm directs incoming traffic to the server with the fewest active connections. It is especially useful
    # in environments where connections have varying durations and resource usage.
    def least_connections(self):
        # Simple mock-up (real implementation requires tracking connections)
        return min(self.all_servers, key=lambda s: self.all_servers[s]["connections"])

    # In this method, a hash of the client's IP address is computed to assign them to a specific server. This creates
    # a consistent mapping, ensuring that a client is always routed to the same server for subsequent requests.
    def source_ip_hash(self, ip):
        index = int(hashlib.sha256(ip.encode()).hexdigest(),
                    16) % len(self.servers)
        return self.servers[index]

    # This is an extension of the Round Robin algorithm that assigns a weight to each server based on its capacity or
    # performance. Servers with higher weights receive more requests compared to those with lower weights.
    def weighted_round_robin(self):
        weighted_list = [s for s, details in self.all_servers.items()
                         for _ in range(details["weight"])]
        return random.choice(weighted_list)

    def least_response_time(self):
        return min(self.all_servers, key=lambda s: self.all_servers[s]["response_time"])
