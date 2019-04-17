import random
import sys
import getopt
import pandas as pd
import matplotlib.pyplot as plt


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


# Softened random number creator, prev_rand to soften the variance
def newRand(prev_rand, floor):
    return (random.randint(floor, 100)/50 + prev_rand)/3


# Function to generate the initial load coming from the botnets
# Load is generated in Mbps
def attacker(n_bots, pkt_size, band, rand):
    # Insert uncertainty to the bots availability
    return round((pkt_size * n_bots * band * rand)/1000000, 2)


# Function to generate the connections load
def attackerCon(n_bots, band, rand):
    # Insert uncertainty to the bots availability
    return int(n_bots * band * rand)


# Function to create a variable legitim traffic volume
def defaultTraffic(n_bots, pkt_size, band, perc, rand):
    base_traffic = ((pkt_size * n_bots * band)/1000000) * perc
    return round(base_traffic * rand, 2)


# Function to create a variable legitim connectio volume
def defaultCon(n_bots, band, perc, rand):
    return int(n_bots * band * perc * rand)


# Vulnerable DNS for the amplification
def dns(bot_load, amp_rate):
    # print("Bots -> DNS        : ", round(bot_load, 2))
    return bot_load * amp_rate


# Non deterministic clock to successfully mitigate/restart the attack
def reactionClock(clock, reaction):
    clock = clock + (random.randint(0,100)/100)
    if clock >= reaction/2:
        return 0
    else:
        return clock


# Check if the server is down and returns why
def isDown(link, attack_load, attack_connections, connections):
    if attack_load > link or attack_connections > connections:
        return 1
    else:
        return 0


# Firewall that is going to filter the attack
def firewall(method, attack_load, default_traffic, block_status, link, row, att_con=0, def_con=0, con=0):
    inbound = round(attack_load + default_traffic, 2)
    row.append(inbound)
    '''if method == "dns_amp":
        print("DNS -> Firewall    : ", inbound)
    elif method == "syn_flood":
        print("Bots -> Firewall   : ", inbound)'''
    multi = abs(block_status - 1)
    target_load = (multi * attack_load) + default_traffic
    row.append(round(target_load, 2))
    # print("Firewall -> Target : ", round(target_load, 2))
    target_con = (multi * att_con) + def_con
    s_down = isDown(link, target_load, target_con, con)
    rem_band = round(link - target_load, 2)
    rem_con = con - target_con
    row.append(rem_band)
    # print("Remaining bandwidth: ", rem_band)
    if method == "syn_flood":
        # print("Remaining connections: ", rem_con)
        row.append(rem_con)
    '''if s_down == 1:
        print("Server is          :  DOWN!!!")
    else:
        print("Server is: UP")
    '''
    row.append(s_down)

def plotGraph(method, df):
    if method == "dns_amp":
        plt.close('all')

        plt.figure(1)
        plt.plot(df['second'], df['rem_bandwidth'],
                    color='red', label='remaining bandwidth')
        plt.plot(df['second'], df['bot-->dns'],
                    color='blue', label='bot-->dns')
        plt.plot(df['second'], df['dns-->firewall'],
                    color='yellow', label='dns-->firewall')
        plt.plot(df['second'], df['firewall-->target'],
                    color='green', label='firewall-->target')
        plt.legend(loc='best', bbox_to_anchor=(0.5, 0., 0.5, 0.5))
        plt.xlabel('Time (s)')
        plt.ylabel('Bandwidth (Mbps)')
        plt.title("Bandwidth Status")
        plt.grid(True)
        plt.savefig('bandwidth_status.png', bbox_inches='tight')

        plt.figure(2)
        plt.plot(df['second'], df['server_down'],
                    color='purple', label='server status')
        plt.legend(loc='best', bbox_to_anchor=(0.5, 0., 0.5, 0.5))
        plt.xlabel('Time (s)')
        plt.ylabel('Up/Down')
        plt.title("Server Status")
        plt.grid(True)
        plt.savefig('server_status.png', bbox_inches='tight')

        plt.show()
    elif method == "syn_flood":
        plt.close('all')

        plt.figure(1)
        plt.plot(df['second'], df['bot-->firewall'],
                    color='red', label='bot-->firewall')
        plt.plot(df['second'], df['firewall-->target'],
                    color='green', label='firewall-->target')
        plt.plot(df['second'], df['rem_bandwidth'],
                    color='blue', label='rem_bandwidth')
        plt.legend(loc='best', bbox_to_anchor=(0.5, 0., 0.5, 0.5))
        plt.xlabel('Time (s)')
        plt.ylabel('Bandwidth (Mbps)')
        plt.title("Bandwidth Status")
        plt.grid(True)
        plt.savefig('bandwidth_status.png', bbox_inches='tight')

        plt.figure(2)
        plt.plot(df['second'], df['server_down'],
                    color='purple', label='server status')
        plt.legend(loc='best', bbox_to_anchor=(0.5, 0., 0.5, 0.5))
        plt.xlabel('Time (s)')
        plt.ylabel('Up/Down')
        plt.title("Server Status")
        plt.grid(True)
        plt.savefig('server_status.png', bbox_inches='tight')

        plt.figure(3)
        plt.plot(df['second'], df['rem_connections'],
                    color='blue', label='remaining connections')
        plt.legend(loc='best', bbox_to_anchor=(0.5, 0., 0.5, 0.5))
        plt.xlabel('Time (s)')
        plt.ylabel('Connections')
        plt.title("Remaining Connections")
        plt.grid(True)
        plt.savefig('connections.png', bbox_inches='tight')

        plt.show()
        pass
    else:
        pass


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
        opts, args = getopt.getopt(argv, "hm:n:s:b:r:p:l:a:c:")
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
            elif opt == "-m" and arg in ["syn_flood", "dns_amp"]:
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

        if method == "dns_amp":
            df = pd.DataFrame(columns=["second",
                                       "bot-->dns",
                                       "dns-->firewall",
                                       "firewall-->target",
                                       "rem_bandwidth",
                                       "server_down"])
        elif method == "syn_flood":
            df = pd.DataFrame(columns=["second",
                                       "bot-->firewall",
                                       "firewall-->target",
                                       "rem_bandwidth",
                                       "rem_connections",
                                       "server_down"])

        for i in range (1,period+1):
            # print("\n\n####################")
            # print("Second: ", i)
            # print("####################")
            if block_status == 0:
                defense_clock = reactionClock(defense_clock, reaction)
                if defense_clock == 0:
                    block_status = 1
            else:
                attack_clock = reactionClock(attack_clock, reaction)
                if attack_clock == 0:
                    block_status = 0
            prev_attack_rand = newRand(prev_attack_rand, 75)
            prev_traffic_rand = newRand(prev_traffic_rand, 50)
            prev_con_rand = newRand(prev_con_rand, 50)
            if method == "dns_amp":
                row = [i]
                bot_load = attacker(n_bots, pkt_size, band, prev_attack_rand)
                row.append(round(bot_load, 2))
                att_load = dns(bot_load, amp_rate)
                def_traffic = defaultTraffic(n_bots, pkt_size, band, 2, prev_traffic_rand)
                firewall(method, att_load, def_traffic, block_status, link, row)
            elif method == "syn_flood":
                row = [i]
                att_load = attacker(n_bots, pkt_size, band, prev_attack_rand)
                def_traffic = defaultTraffic(n_bots, pkt_size, band, 1, prev_traffic_rand)
                def_con = defaultCon(n_bots, band, 0.2, prev_con_rand)
                att_con = attackerCon(n_bots, band, prev_attack_rand)
                firewall(method, att_load, def_traffic, block_status, link, row, att_con, def_con, connections)

            # print("LINHA:           ", row)
            df.loc[len(df)] = row

        print(df)
        plotGraph(method, df)


if __name__ == "__main__":
    main(sys.argv[1:])
