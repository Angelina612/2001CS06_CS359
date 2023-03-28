from scapy.all import *


ip = '172.16.102.82'
url = 'www.sports.yahoo.com'

# ARP
def arp():
    pckt =  Ether(dst ="ff:ff:ff:ff:ff:ff") / ARP()
    wrpcap(f"output/ARP_2001CS06.pcap",pckt,append = False)

# ARP request response
def arp_req_resp():
    pckt =  Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=ip)

    wrpcap(f"output/ARP_request_response_2001CS06.pcap",pckt,append = True)
    pckt = srp1(pckt,timeout=5,filter="arp")
    wrpcap(f"output/ARP_request_response_2001CS06.pcap",pckt,append = True)

# FTP
def ftp_job(dstIP):
    pkt = (IP(dst=dstIP) / TCP(sport=RandShort(),
                               dport=21,flags="S",options=[
                                   ('MSS', 1460), ('SAckOK', ''),
                                   ('Timestamp', (5693231, 0)),
                                   ('NOP', None), ('WScale', 6)
                                   ]
                               ))
    wrpcap(f"output/FTP_open_connection_2001CS06.pcap",pkt,append=True)
    ans = srp1(pkt, timeout=10)
    wrpcap(f"output/FTP_open_connection_2001CS06.pcap",ans,append=True)

    sseq=ans.seq
    sack=ans.ack

    ack=(IP(proto=6, tos=0, dst=dstIP, options='',
            version=4)/TCP(seq=sack, ack=sseq+1, dport=21, flags="A", options=[
                ('NOP', None),
                ('NOP', None),
                ('Timestamp', (981592, 525503134))
                ]))
    wrpcap(f"output/FTP_open_connection_2001CS06.pcap",ack,append=True)
    ans=srp1(ack, timeout=10)

    # FIN START
    fin=(IP(proto=6, tos=0, dst=dstIP, options='',
            version=4)/TCP(dport=21, flags="F", options=[
                ('NOP', None),
                ('NOP', None),
                ('Timestamp', (981592, 525503134))
                ]))
    wrpcap(f"output/FTP_connection_end_2001CS06.pcap", fin, append=True)
    ans=srp1(fin, timeout=10)
    if ans is not None:
        wrpcap(f"output/FTP_connection_end_2001CS06.pcap", ans, append=True)
    ack=(IP(proto=6, tos=0, dst=dstIP, options='',
            version=4)/TCP(dport=21, flags="A", options=[
                ('NOP', None),
                ('NOP', None),
                ('Timestamp', (981592, 525503134))
                ]))
    wrpcap(f"output/FTP_connection_end_2001CS06.pcap", ack, append=True)


# TCP
def tcp():
    sport = 1234
    dport = 80

    SYN= IP(src=ip, dst=url) / TCP(sport=sport, dport=dport, flags='S', seq=1000)
    SYNACK = srp1(SYN, timeout=10)
    ACK = IP(src=ip, dst=url) / TCP(sport=sport, dport=dport, flags='A', seq=SYNACK.ack, ack=SYNACK.seq + 1)
    sendp(ACK, timeout=10)
    wrpcap("output/TCP_3_way_handshake_start_2001CS06.pcap",[SYN, SYNACK, ACK],append = True)

    FIN= IP(dst=url) / TCP(sport=sport,dport=dport,flags = 'F')
    FINACK = srp1(FIN, timeout=10)
    ACK = IP(dst=url) / TCP(sport=sport, dport=dport, flags='A', seq=FINACK.ack, ack=FINACK.seq + 1)
    sendp(ACK, timeout=10)
    wrpcap("output/TCP_handshake_close_2001CS06.pcap", [FIN, FINACK, ACK], append = True)

# DNS
def dns():
    dns_req = IP(dst=url) / UDP(dport=53) /  DNS(rd=1, qd=DNSQR(qname=url))
    answer = srp1(dns_req, verbose=0, timeout=10)

    wrpcap("output/DNS_request_response_2001CS06.pcap",[dns_req, answer],append = True)

# PING
def ping():
    icmp = IP(dst=url)/ICMP()
    wrpcap("output/PING_request_response_2001CS06.pcap",icmp,append = True)

    resp = srp1(icmp,timeout=10)

    # Check if a response was received
    if resp is not None:
        print("Ping response received from", ip)
        wrpcap("output/PING_request_response_2001CS06.pcap",resp,append =True)
    else:
        print("No ping response received from", ip)

if __name__ == "__main__":
    arp()
    # tcp()
    # dns()
    ping()
    arp_req_resp()
    ftp_job('54.228.213.93')
