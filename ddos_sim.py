import random
import sys
import getopt


help_string="\n###################\n###DDOS SIM Help###\n###################\n\n#For SYN Flood:\n\n  - ddos_sim.py -m syn_flood -n <qty of botnets> -s <packet size> -p <probability of success>\n\n#For DNS Amplification:\n\n  - ddos_sim.py -m dns_amp -n <qty of botnets> -s <packet size> -a <amplification rate>\n"

#Function to generate the initial load coming from the botnets
def attacker(n_bots, pkt_size, prev_rand):
    rand = (random.randint(40,100)/100 + prev_rand)/2 #Insert uncertainty to the bots availability
    prev_rand = rand
    return pkt_size * n_bots * rand


#Vulnerable DNS for the amplification
def dns(bot_load, amp_rate):
    print("Bots -> DNS : ", round(bot_load, 2))
    return bot_load * amp_rate


#Firewall that is going to filter the attack
def firewall(method, attack_load, defense_clock):
    print("-> Firewall : ", round(attack_load, 2))
    '''if method == "dns_amp":
        defense_clock = defense_clock + (random.randint(0,100)/100)'''
        



def main(argv):
    method = ""
    nBots = ""
    pktSize = ""
    prob = ""
    amp_rate = ""
    prev_attack_rand = 0
    defense_clock = 0
    try:
        opts, args = getopt.getopt(argv,"hm:n:s:pa:")
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
                nBots = float(arg)
            elif opt == "-s":
                pktSize = float(arg)
            elif opt == "-p" and method == "syn_flood":
                if float(arg)>=0 and float(arg)<=1:
                    prob = float(arg)
                else:
                    print("Probability of success (p) should be [0,1]")
                    sys.exit()
            elif opt == "-a" and method == "dns_amp":
                amp_rate = float(arg)
            else:
                print(help_string)
                sys.exit()
#       print("opts: ", opts)
#       print("Chosen method: ", method)
#       print("Quantity of bots: ", nBots)
        if method == "dns_amp":
            for i in range(1,3600):
                firewall(method,dns(attacker(nBots, pktSize, prev_attack_rand), amp_rate), defense_clock)

if __name__ == "__main__":
   main(sys.argv[1:])
