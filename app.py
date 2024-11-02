from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    algorithm = request.args.get("algorithm", "round_robin")
    if request.method == "POST":
        # Send a request to the load balancer
        try:
            response = requests.get(
                f"http://load_balancer:5004/route?algorithm={algorithm}")
            if response.status_code == 200:
                data = response.json()
                return jsonify(data)
            else:
                return jsonify({"error": "Backend server is down"}), 500

        except requests.RequestException as e:
            return jsonify({"error": "Failed to connect to load balancer", "details": str(e)}), 503
    return render_template("index.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5005)
