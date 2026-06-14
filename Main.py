from flask import Flask, jsonify, render_template
from flask_cors import CORS
import psutil

def get_cpu():
    return psutil.cpu_percent(interval=0.5)

def get_ram():
    return psutil.virtual_memory().percent

def get_disk_usage():
    return psutil.disk_io_counters().write_bytes, psutil.disk_io_counters().read_bytes

server = Flask(__name__)

@server.route("/")
def dashboard():
    return render_template("index.html")

@server.route("/api/system",methods=["GET"])
def return_system_info():
    cpu = get_cpu()
    ram = get_ram()
    disk = get_disk_usage()

    system_info = {
        "cpu":cpu,
        "ram":ram,
        "disk":disk
    }

    return jsonify(system_info)

server.run("0.0.0.0","8080")