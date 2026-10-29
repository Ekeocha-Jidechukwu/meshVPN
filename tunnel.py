import socket
import threading
import subprocess
from pytun import TunTapDevice

# --- Config (you'll change these per machine) ---
LOCAL_IP = '10.8.0.1'      # this machine's TUN address
PEER_UDP_ADDR = ('127.0.0.1', 5001)  # where to send packets (testing: localhost)
LISTEN_PORT = 5000          # port this machine listens on for incoming tunnel traffic


# --- Set up TUN device ---
tun = TunTapDevice(name='meshvpn0')
tun.addr = LOCAL_IP
tun.netmask = '255.255.255.0'
tun.mtu = 1400
tun.up()

print("Current routes for this interface:")
subprocess.run(['ip', 'route', 'show', 'dev', tun.name])

# --- Set up UDP socket ---
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('0.0.0.0', LISTEN_PORT))

print(f"Tunnel up: {tun.name} ({LOCAL_IP}) <-> UDP {LISTEN_PORT}")

def tun_to_udp():
    """Read packets from TUN, send them out over UDP to the peer."""
    while True:
        packet = tun.read(tun.mtu)
        sock.sendto(packet, PEER_UDP_ADDR)
        print(f"TUN -> UDP: {len(packet)} bytes")

def udp_to_tun():
    """Receive packets over UDP, write them into TUN."""
    while True:
        packet, addr = sock.recvfrom(2048)
        tun.write(packet)
        print(f"UDP -> TUN: {len(packet)} bytes from {addr}")

# Run both directions at once using threads
threading.Thread(target=tun_to_udp, daemon=True).start()
threading.Thread(target=udp_to_tun, daemon=True).start()

try:
    while True:
        pass
except KeyboardInterrupt:
    print("\nStopping.")
    tun.down()