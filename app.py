from flask import Flask, render_template
import subprocess
import re

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/find_ip', methods=['POST'])
def find_ip():
    try:
        # Use nmap to scan the network for devices
        result = subprocess.run(['nmap', '-sn', '192.168.1.0/24'], capture_output=True, text=True)
        nmap_output = result.stdout

        devices = parse_nmap_output(nmap_output)

        cameras = filter_cameras(devices)

        return render_template('result.html', cameras=cameras)
    except Exception as e:
        error_message = f"Error occurred: {str(e)}"
        return render_template('error.html', error_message=error_message)

def parse_nmap_output(output):
    ip_pattern = re.compile(r'Nmap scan report for (\d+\.\d+\.\d+\.\d+)')
    mac_pattern = re.compile(r'MAC Address: ([0-9A-F:]{17})')
    lines = output.splitlines()
    devices = []
    current_ip = None
    for line in lines:
        ip_match = ip_pattern.search(line)
        mac_match = mac_pattern.search(line)
        if ip_match:
            current_ip = ip_match.group(1)
        if mac_match and current_ip:
            mac_address = mac_match.group(1)
            devices.append({'ip_address': current_ip, 'mac_address': mac_address})
            current_ip = None
    return devices

def filter_cameras(devices):
    # Custom logic to identify camera devices
    # This might be based on MAC address patterns, IP address patterns, or other heuristics
    cameras = [device for device in devices if is_camera(device)]
    return cameras

def is_camera(device):
    # Example heuristic: checking if the MAC address matches known camera manufacturers
    known_camera_mac_prefixes = ['00:1A:2B', '00:1E:C2']  # Replace with actual prefixes
    for prefix in known_camera_mac_prefixes:
        if device['mac_address'].startswith(prefix):
            return True
    return False

if __name__ == '__main__':
    app.run(debug=True)