from pytun import TunTapDevice

# Create the TUN device
tun = TunTapDevice(name='meshvpn0')
tun.addr = '10.8.0.1'
tun.netmask = '255.255.255.0'
tun.mtu = 1400
tun.up()

print(f"TUN device '{tun.name}' is up at {tun.addr}")
print("Reading packets... (Ctrl+C to stop)")

try:
    while True:
        packet = tun.read(tun.mtu)
        print(f"Got packet: {len(packet)} bytes")
except KeyboardInterrupt:
    print("\nStopping.")
    tun.down()