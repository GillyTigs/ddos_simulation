import random
import sys
import getopt


def printHelp():
    print("\n###################"
          "\n###DDOS SIM Help###"
          "\n###################\n"
          "\n#For SYN Flood:\n"
          "\n - ddos_sim.py -m syn_flood"
          " -n <qty of IP sources>"
          " -s <packet size (bytes)>"
          " -b <packets per second>"
          " -r <avg reaction time to mitigate/restart the attack (seconds)>"
          " -p <simulation period (seconds)>"
          " -l <bandwidth of the server link (Mbps)>"
          " -c <number of possible SYN connections>\n"
          "\n#For DNS Amplification:\n"
          "\n - ddos_sim.py -m dns_amp"
          " -n <qty of IP sources>"
          " -s <packet size (bytes)>"
          " -b <packets per second>"
          " -r <avg reaction time to mitigate/restart the attack (seconds)>"
          " -p <simulation period (seconds)>"
          " -l <bandwidth of the server link (Mbps)>"
          " -a <amplification rate>\n\n")


#Softened random number creator, prev_rand to soften the variance
def newRand(prev_rand, floor):
    return (random.randint(floor,100)/50 + prev_rand)/3


#Function to generate the initial load coming from the botnets
#Load is generated in Mbps
def attacker(n_bots, pkt_size, band, rand):
    #Insert uncertainty to the bots availability
    return round((pkt_size * n_bots * band * rand)/1000000, 2)


#Function to generate the connections load
def attackerCon(n_bots, band, rand):
    #Insert uncertainty to the bots availability
    return int(n_bots * band * rand)


#Function to create a variable legitim traffic volume
def defaultTraffic(n_bots, pkt_size, band, perc, rand):
    base_traffic = ((pkt_size * n_bots * band)/1000000) * perc
    return round(base_traffic * rand, 2)


#Function to create a variable legitim connectio volume
def defaultCon(n_bots, band, perc, rand):
    return int(n_bots * band * perc * rand)


#Vulnerable DNS for the amplification
def dns(bot_load, amp_rate):
    print("Bots -> DNS        : ", round(bot_load, 2))
    return bot_load * amp_rate


#Non deterministic clock to successfully mitigate/restart the attack
def reactionClock(clock, reaction):
    clock = clock + (random.randint(0,100)/100)
    if clock >= reaction/2:
        return 0
    else:
        return clock


#Check if the server is down and returns why
def isDown(link, attack_load, attack_connections, connections):
    if attack_load > link and attack_connections <= connections:
        return "band"
    elif attack_connections > connections and attack_load <= link:
        return "con"
    elif attack_load > link and attack_connections > connections:
        return "both"
    else:
        return 0


#Firewall that is going to filter the attack
def firewall(method, attack_load, default_traffic, block_status, link, att_con=0, def_con=0, con=0):
    if method == "dns_amp":
        print("DNS -> Firewall    : ", round(attack_load + default_traffic, 2))
    elif method == "syn_flood":
        print("Bots -> Firewall   : ", round(attack_load + default_traffic, 2))
    multi = abs(block_status - 1)
    target_load = (multi * attack_load) + default_traffic
    print("Firewall -> Target : ", round(target_load, 2))
    target_con = (multi * att_con) + def_con
    s_down = isDown(link, target_load, target_con, con)
    if s_down == "band":
        print("Missing bandwidth  : ", round(target_load - link, 2))
        if method == "syn_flood":
            print("Remaining connections: ", con - target_con)
        print("Server is          :  DOWN!!!")
    elif s_down == "con":
        print("Remaining bandwidth: ", round(link - target_load, 2))
        if method == "syn_flood":
            print("Missing connections: ", target_con - con)
        print("Server is          :  DOWN!!!")
    elif s_down == "both":
        print("Missing bandwidth  : ", round(target_load - link, 2))
        if method == "syn_flood":
            print("Missing connections: ", target_con - con)
        print("Server is          :  DOWN!!!")
    else:
        print("Remaining bandwidth: ", round(link - target_load, 2))
        if method == "syn_flood":
            print("Remaining connections: ", con - target_con)
        print("Server is: UP")


def main(argv):
    method = ""
    n_bots = ""
    pkt_size = ""
    amp_rate = ""
    reaction = ""
    period = ""
    band = ""
    link = ""
    connections = ""
    prev_attack_rand = 0
    prev_defense_rand = 0
    prev_traffic_rand = 0
    prev_con_rand = 0
    defense_clock = 0
    attack_clock = 0
    block_status = 0
    server_down = 0
    try:
        opts, args = getopt.getopt(argv,"hm:n:s:b:r:p:l:a:c:")
    except getopt.GetoptError:
        printHelp()
        sys.exit(2)

    if len(opts) != 8:
        printHelp()
        sys.exit()
    else:
        for opt, arg in opts:
            if opt == "-h" or "-" in arg:
                printHelp()
                sys.exit()
            elif opt == "-m" and arg in ["syn_flood","dns_amp"]:
                method = arg
            elif opt == "-n":
                n_bots = float(arg)
            elif opt == "-s":
                pkt_size = float(arg)
            elif opt == "-b":
                band = float(arg)
            elif opt == "-r":
                reaction = float(arg)
            elif opt == "-p":
                period = int(arg)
            elif opt == "-l":
                link = float(arg)
            elif opt == "-a" and method == "dns_amp":
                amp_rate = float(arg)
            elif opt == "-c" and method == "syn_flood":
                connections = int(arg)
            else:
                printHelp()
                sys.exit()

        for i in range (1,period):
            print("\n\n####################")
            print("Second: ", i)
            print("####################")
            if block_status == 0:
                defense_clock = reactionClock(defense_clock, reaction)
                if defense_clock == 0:
                    block_status = 1
            else:
                attack_clock = reactionClock(attack_clock, reaction)
                if attack_clock == 0:
                    block_status = 0
            prev_attack_rand = newRand(prev_attack_rand,70)
            prev_traffic_rand = newRand(prev_traffic_rand,50)
            prev_con_rand = newRand(prev_con_rand,50)
            if method == "dns_amp":
                att_load = dns(attacker(n_bots, pkt_size, band, prev_attack_rand), amp_rate)
                def_traffic = defaultTraffic(n_bots, pkt_size, band, 2, prev_traffic_rand)
                firewall(method, att_load, def_traffic, block_status, link)
            elif method == "syn_flood":
                att_load = attacker(n_bots, pkt_size, band, prev_attack_rand)
                def_traffic = defaultTraffic(n_bots, pkt_size, band, 1, prev_traffic_rand)
                def_con = defaultCon(n_bots, band, 0.2, prev_con_rand)
                att_con = attackerCon(n_bots, band, prev_attack_rand)
                firewall(method, att_load, def_traffic, block_status, link, att_con, def_con, connections)


if __name__ == "__main__":
   main(sys.argv[1:])
