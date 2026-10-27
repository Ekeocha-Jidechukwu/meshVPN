# MeshVPN Architecture

## Goal
A VPN built with a custom handshake, custom encryption, and
peer-to-peer mesh routing — no WireGuard/OpenVPN libraries.

## Status
Day 1 — scaffolding only.

Day 2
## How packets flow (kernel <-> userspace)

A TUN device is a virtual network interface created in software.
The kernel treats it like a real network card, but instead of
sending data out a physical wire, it hands packets to a userspace
program through a file descriptor.

Flow for MeshVPN:
1. Kernel routes outbound IP traffic to the TUN device instead of
   the real network card.
2. My Python program reads the raw IP packet from the TUN device.
3. The program will encrypt it and send it over a UDP socket to a peer.
4. The peer's program receives it, decrypts it, and writes it to
   its own TUN device.
5. The peer's kernel delivers it to the destination app.

TUN vs TAP: TUN handles IP packets only (layer 3) — this project
uses TUN since it only needs to tunnel IP traffic, not emulate a
full virtual network card like TAP does.

## Why UDP, and how reliability is handled

MeshVPN uses UDP, not TCP, for the tunnel transport. Rationale:
- Inner traffic (e.g. a TCP connection from an app) already handles
  its own retransmission; duplicating that at the tunnel layer
  causes "TCP meltdown" (nested retransmissions).
- Three things ARE handled reliably at the tunnel layer:
  1. Handshake packets: retried with a timeout, since no inner
     protocol protects them.
  2. NAT keepalive: small packets sent periodically (~25s) to
     prevent the NAT mapping from expiring and breaking the tunnel.
  3. Peer liveness: no traffic for N seconds -> mark session dead,
     require fresh handshake.

IP masking comes from encryption + routing, not UDP reliability.
The real risk to "always masked" is silent tunnel failure causing
traffic to leak outside the tunnel — to be addressed by a
kill-switch mechanism (see threat model doc, Day 14).

## Day 3: First working TUN device

Created a TUN interface (meshvpn0) using pytun-pmd3, brought it up
with a static IP (10.8.0.1), and confirmed the kernel hands packets
to userspace: pinging the device produced "Got packet" output in
the script, confirming the read() loop captures real kernel traffic.
Ping itself showed 100% loss, as expected — the script only reads
packets, it doesn't yet send replies.