import math
import random

## Check power and cash balances

from functions import *
from Tariff import Tariff, Customer
import os
from Broker import Broker
from Broker import randomString
import shutil


class Generation():
    def __init__(self,server):
        self.server=server
        self.all_brokers=[]
    def clear_old_genes(self):
        shutil.rmtree("C:/Users/lomiag/PycharmProjects/Energy_Broker/Genetic_Library/")
        os.mkdir("C:/Users/lomiag/PycharmProjects/Energy_Broker/Genetic_Library/")
        shutil.copy("C:/Users/lomiag/PycharmProjects/Energy_Broker/Genetic_Code_ground_zero.csv",
                    "C:/Users/lomiag/PycharmProjects/Energy_Broker/Genetic_Library/Genetic_Code_ground_zero.csv")
    def move_new_to_old(self):
        # self.clear_old_genes()
        new_gen="C:/Users/lomiag/PycharmProjects/Energy_Broker/New_Generation/"
        old_gen="C:/Users/lomiag/PycharmProjects/Energy_Broker/Genetic_Library/"
        new_life=os.listdir(new_gen)
        for life in new_life:
            shutil.move(new_gen+life, old_gen+life)

    def write_best_genes(self,best):
        for broker in best:
            self.save_current_gen(randomString(7),self.all_brokers[broker])

    def save_current_gen(self,index,brk):
        brk.genetic_table.to_csv("C:/Users/lomiag/PycharmProjects/Energy_Broker/New_Generation/Genetic_Code_{}.csv".format(index))


    def evolve(self,generations):
        for g in range(generations):
            # current_generation=os.listdir("C:/Users/lomiag/PycharmProjects/Energy_Broker/Genetic_Library")
            self.all_brokers=self.server.run()
            bst=self.find_best_broker()
            print("Max Cash: ",self.all_brokers[bst[len(bst)-1]].cash,"Max Power: ",self.all_brokers[bst[len(bst)-1]].power)
            print(self.all_brokers[bst[len(bst)-1]].genetic_table)
            self.write_best_genes(bst)
            self.clear_old_genes()
            self.move_new_to_old()
            self.server=Server()


    def find_best_broker(self):
        broker_dict={}
        five_highest=[]

        for broker in self.all_brokers:
            broker_dict[broker.cash]=broker.idx
        for i in sorted(broker_dict.keys()):
            five_highest.append(broker_dict[i])
        return five_highest[-10:]
class Server():

    def __init__(self,gen_code="Genetic_Code_ground_zero"):
        global brk_id
        ## Default tariff
        self.DT = self.get_default_tariff()

        ## List of Brokers participating
        ## List of Customers
        ## List of published Tariffs

        ## You need to initialize a Broker here (change the name in the
        ## imports at the top to reflect your broker's name), and then
        ## put it in the list self.brokers.

        self.brokers = []
        NUMBER_OF_BROKERS=10
        self.brokers=self.create_brokers(15)


        self.customers = [Customer() for i in range(100)]
        self.tariffs = [self.DT]

        # self.run()
    def create_brokers(self,children_num):
        path="C:/Users/lomiag/PycharmProjects/Energy_Broker/"
        parents=os.listdir(path+"Genetic_Library")
        brks=[Broker(1)]
        brk_id=1
        for parent in range(len(parents)):
            for child in range(children_num):

                br=Broker(brk_id,parents[parent][:-4])
                brks.append(br)
                mutation_table=br.create_mutation_table()
                random_gene=random.choice(brks).genetic_table
                # print(random.choice(brks).genetic_table)
                mutaion_options = [br.apply_mutation_multiplication(mutation_table),
                                   br.apply_mutation_combine(random_gene),
                                   br.apply_mutation_reverse()]
                br.genetic_table=random.choice(mutaion_options)
                brks.append(br)
                brk_id += 1

        return brks

    def expand_broker(self,brk_list):
        for brk in self.brokers:
            brk_list.append(brk)
        return brk_list



    def run(self):

        NUMSTEPS = 24

        ## Gather bootstrap data and send it off to brokers
        usage_data, other_data = self.read_initial_data()
        for b in self.brokers:
            b.get_initial_data(usage_data, other_data)

        ## Run simulation for a number of steps
        for step in range(NUMSTEPS):

            ## Let brokers post asks in the wholesale market
            asks = []
            asks_by_broker = dict()
            for b in self.brokers:
                a = b.post_asks(step)
                asks.extend(a)
                asks_by_broker[b.idx] = a

            ## Get bids from producers
            ## Clear market
            ## Distribute energy to brokers
            price, quantity = self.clear_market(asks, self.get_bids())

            for b in self.brokers:
                for ask in asks_by_broker[b.idx]:
                    if ask[0] >= price:
                        b.power += ask[1]

            usage = []
            for c in self.customers:
                usage.append(c.get_use_at_time(step))

            ## Get total demand for each broker
            ## Pay brokers based on their subscriptions
            ## Assess each broker's surplus or deficit
            ## Pay/charge brokers accordingly
            for b in self.brokers:
                b.gain_revenue(self.customers, usage)
                b.adjust_cash(b.get_energy_imbalance(usage) * price)
                b.power = 0

            ## Let customers decide between tariffs and subscribe
            for c in range(len(self.customers)):
                t = self.customers[c].choose_tariff(self.tariffs)

            for b in self.brokers:
                b.customers = [i for i in range(len(self.customers)) if \
                               self.customers[i].tariff.publisher == b.idx]

                ## newdata is a dictionary to hold updated information from the current
            ## time step.  Total is the total energy demand from all 100 customers,
            ## Cleared Price is the wholesale clearing price, Cleared Quantity is
            ## the wholesale market clearing quantity, and Customer Usage is a list
            ## in which element i is customer i's energy usage for the current time
            ## step.
            newdata = {'Total': sum(usage),
                       'Cleared Price': price,
                       'Cleared Quantity': quantity,
                       'Customer Usage': usage,
                       'Tariffs': self.tariffs}

            for b in self.brokers:
                b.receive_message(newdata)

            for t in self.tariffs:
                if t.publisher != 0: t.dec_time()

            self.tariffs = [t for t in self.tariffs if t.duration > 0]

            print(newdata)

            ## Let brokers post new tariffs
            for b in self.brokers:
                self.tariffs.extend(b.post_tariffs(step))
        return self.brokers

    def clear_market(self, asks, bids):

        bids.sort()
        asks.sort(reverse=True)

        total_asked = 0
        total_bidded = 0
        i, j = 0, 0

        while True:
            if total_asked < total_bidded:
                total_asked += asks[i][1]
                i += 1
            elif total_bidded < total_asked:
                total_bidded += bids[j][1]
                j += 1
            else:
                total_asked += asks[i][1]
                total_bidded += bids[j][1]
                i += 1
                j += 1
            try:
                if asks[i][0] < bids[j][0]:
                    price = bids[j - 1][0]
                    quantity = total_asked
                    break
            except:
                if i == len(asks):
                    i -= 1
                if j == len(bids):
                    j -= 1
                price = (abs(asks[i][0] + bids[j][0])) / 2
                quantity = total_asked

        return price, quantity

    def read_initial_data(self):
        customer_usage = dict()
        other_data = dict()

        f = open('CustomerNums.csv', 'r')
        raw = [i[:-1].split(',')[1:] for i in f.readlines()[1:]]
        for i in range(1, len(raw) + 1):
            customer_usage[i] = [float(dat) for dat in raw[i - 1]]
        f.close()

        f = open('OtherData.csv')
        raw = [i[:-1].split(',')[1:] for i in f.readlines()[1:]]
        other_data['Cleared Price'] = [float(dat) for dat in raw[0]]
        other_data['Cleared Quantity'] = [float(dat) for dat in raw[1]]
        other_data['Difference'] = [float(dat) for dat in raw[2]]
        other_data['Total Demand'] = [float(dat) for dat in raw[3]]

        return customer_usage, other_data

    def get_bids(self):

        f = open('GenCos.csv', 'r')
        data = [i[:-1].split(',') for i in f.readlines()[1:]]
        f.close()

        bids = []

        ## Get a bid from each plant, keep their capacity as well
        for d in data:
            bids.append((get_random_bid(float(d[5])), int(d[4])))

        return bids

    def get_default_tariff(self):
        return Tariff(0, price=1000, duration=1, exitfee=500)

    def expand_brokers(self,broker_list):
        for brk in self.brokers:
            broker_list.apend(brk)
        return broker_list

s = Server()
gen = Generation(s)
gen.evolve(3)