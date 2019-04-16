import random
import sys
import getopt


help_string="ddos_sim.py -m <syn_flood | dns_amp> -n <qty of botnets> -s <packet size> -p <probability of success>"

#Function to generate a load based on the attacking parameters
def attacker (method, nBots, pktSize, prob):
    if method == "syn_flood":
        print("syn")
    elif method == "dns_amp":
        print("dns")
    
    print("Chosen method: ", method)
    print("Quantity of bots: ", nBots)
    print("Packet size: ", pktSize)
    print("Probability of success: ", prob)

def main(argv):
    method = ""
    nBots = ""
    pktSize = ""
    prob = ""
    try:
        opts, args = getopt.getopt(argv,"hm:n:s:p:")
    except getopt.GetoptError:
        print(help_string)
        sys.exit(2)

    if len(opts) !=4:
        print(help_string)
        sys.exit()
    else:
        for opt, arg in opts:
            if opt == "-h" or "-" in arg:
                print(help_string)
                sys.exit()
            elif opt == "-m" and arg in ["syn_flood","dns_amp"]:
                method = arg
            elif opt == "-n":
                nBots = arg
            elif opt == "-s":
                pktSize = arg
            elif opt == "-p":
                if float(arg)>=0 and float(arg)<=1:
                    prob = arg
                else:
                    print("Probability of success (p) should be [0,1]")
                    sys.exit()
            else:
                print(help_string)
                sys.exit()
#       print("opts: ", opts)
#       print("Chosen method: ", method)
#       print("Quantity of bots: ", nBots)
        attacker(method, nBots, pktSize, prob)

if __name__ == "__main__":
   main(sys.argv[1:])
