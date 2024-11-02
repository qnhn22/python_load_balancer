from flask import Flask, jsonify
import sys
import socket

app = Flask(__name__)


@app.route("/")
def index():
    # Send back a message with the server port to identify this server
    return jsonify({"server": socket.gethostname()})


@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"})


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    app.run(host="0.0.0.0", port=port)
