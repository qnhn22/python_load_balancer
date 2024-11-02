from flask import Flask, jsonify, request
from load_balancer import LoadBalancer
import requests
import threading

app = Flask(__name__)

load_balancer = LoadBalancer()


@app.route("/route", methods=["GET"])
def route_request():
    algorithm = request.args.get('algorithm')
    ip = None
    if algorithm == 'source_ip_hash':
        ip = request.remote_addr
    backend = load_balancer.route_request(algorithm, ip)
    try:
        # Forward request to selected backend server
        response = requests.get(backend)

        if response.status_code == 200:
            data = response.json()
            response_data = {
                "server": data.get("server"),
                "algorithm": algorithm
            }

            return jsonify(response_data)
    except requests.RequestException:
        return jsonify({"error": "Backend server is down"}), 500


if __name__ == "__main__":
    health_thread = threading.Thread(
        target=load_balancer.update_load_balancer, daemon=True)
    health_thread.start()
    app.run(host="0.0.0.0", port=5004)
