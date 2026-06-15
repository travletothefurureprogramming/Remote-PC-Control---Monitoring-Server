from flask import Flask, jsonify, render_template
from flask_cors import CORS
import psutil
import time

def get_cpu():
    return psutil.cpu_percent(interval=0.5)

def get_ram():
    return psutil.virtual_memory().percent

def get_disk_usage():
    usage = psutil.disk_usage('/')
    return usage.percent

def get_network_usage():
    sent1 = psutil.net_io_counters().bytes_sent
    recv1 = psutil.net_io_counters().bytes_recv

    time.sleep(1)

    sent2 = psutil.net_io_counters().bytes_sent
    recv2 = psutil.net_io_counters().bytes_recv

    bytes_sent = sent2 - sent1
    bytes_recv = recv2 - recv1

    return bytes_sent,bytes_recv
    

server = Flask(__name__)
CORS()

@server.route("/")
def dashboard():
    return render_template("index.html")

@server.route("/api/system",methods=["GET"])
def return_system_info():
    cpu = get_cpu()
    ram = get_ram()
    disk = get_disk_usage()
    net = get_network_usage()

    system_info = {
        "cpu":cpu,
        "ram":ram,
        "disk":disk,
        "net_sent": net[0],
        "net_recv": net[1]
    }

    return jsonify(system_info)



server.run("0.0.0.0","8080")