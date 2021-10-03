import os
from scapy.all import *
from scapy.layers.dns import *
import tldextract

# dns_packets = rdpcap('test.pcap')
# for packet in dns_packets:
#     if packet.haslayer(DNS):
#         print(str(packet[DNSQR].qname))
def handle_packet(a):
    def find_domain(packet):
        if packet.haslayer(DNS):
            url = packet[DNSQR].qname
            url_str = url.decode()
            # print(str(packet[DNSQR].qname))
            dns = tldextract.extract(url_str)
            print(dns.domain)
            print(a)
    return find_domain


sniff(iface = "ens33", prn=handle_packet(1), store = 0)

