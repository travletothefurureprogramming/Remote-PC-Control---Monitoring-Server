from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
import psutil
import time
import os
import threading
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

devices = AudioUtilities.GetSpeakers()

volume = devices.EndpointVolume


net_sent = 0
net_recv = 0

def get_cpu():
    return psutil.cpu_percent(interval=0.5)

def get_ram():
    return psutil.virtual_memory().percent

def get_disk_usage():
    return psutil.disk_usage('/').percent

def network_monitor():
    global net_sent, net_recv
    old_sent = psutil.net_io_counters().bytes_sent
    old_recv = psutil.net_io_counters().bytes_recv

    while True:
        time.sleep(1)
        new_sent = psutil.net_io_counters().bytes_sent
        new_recv = psutil.net_io_counters().bytes_recv

        net_sent = new_sent - old_sent
        net_recv = new_recv - old_recv

        old_sent = new_sent
        old_recv = new_recv

def sleep_pc():
    os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")

def shutdown_pc():
    os.system("shutdown /s /t 0")

def restart_pc():
    os.system("shutdown /r")

def get_volume():

    current_volume = volume.GetMasterVolumeLevelScalar() * 100
    return int(current_volume)

def increase_volume():
    current = volume.GetMasterVolumeLevelScalar()
    new_volume = min(current + 0.01, 1.0)  

    volume.SetMasterVolumeLevelScalar(new_volume, None)

def decrease_volume():
    current = volume.GetMasterVolumeLevelScalar()
    new_volume = min(current - 0.01, 1.0)  

    volume.SetMasterVolumeLevelScalar(new_volume, None)


server = Flask(__name__)
CORS(server)

threading.Thread(target=network_monitor, daemon=True).start()

@server.route("/")
def dashboard():
    return render_template("index.html")

@server.route("/api/system", methods=["GET"])
def return_system_info():
    system_info = {
        "cpu": get_cpu(),
        "ram": get_ram(),
        "disk": get_disk_usage(),
        "net_sent": net_sent,
        "net_recv": net_recv,
        "volume":get_volume()
    }
    return jsonify(system_info)

@server.route("/api/actions/sleep", methods=["POST"])
def sleep_api():
    data = request.json
    if data.get("action") == "sleep":
        sleep_pc()
    return jsonify({"message": "ok", "status": 200})

@server.route("/api/actions/volume", methods=["GET","POST"])
def volume_api():
    if request.method == "GET":
        return jsonify({"volume":int(get_volume())}) 
    else:
        data = request.json
        if data.get("action") == "increase":
            increase_volume()
        else:
            decrease_volume()
        return jsonify({"message": "ok", "status": 200})

@server.route("/api/actions/shutdown", methods=["POST"])
def shutdown_api():
    data = request.json
    if data.get("action") == "shutdown":
        shutdown_pc()
    return jsonify({"message": "ok", "status": 200})


@server.route("/api/actions/restart", methods=["POST"])
def restart_api():
    data = request.json
    if data.get("action") == "restart":
        restart_pc()
    return jsonify({"message": "ok", "status": 200})


server.run("0.0.0.0", 8080)