from Tariff import Tariff
import csv
import matplotlib.pyplot as plt
import numpy as np
import random as rnd
import pandas
import string
import scipy.stats
"""
The broker model:

The model predicts the demand per hour based on the average consumption of 100 customers. Than it splits the day into 
3 sections from 

Section I: 0 to 4 and 20 to 24
Section II: from 4 to 8 and 16 to 24
Section III: from 8 to 16

For each section there is a seperate demand multiplier that multiplies the demand at each hour based,
on which section the hour is in. 
Same goes for the Ask price.


"""
def randomString(stringLength=5):
    """Generate a random string of fixed length """
    letters = string.ascii_lowercase
    return ''.join(rnd.choice(letters) for i in range(stringLength))

class Broker():

    def __init__( self, idx, gene="Genetic_Code_ground_zero"):
        # self.upload_genes()
        ## ID number, cash balance, energy balance
        self.get_other_data()
        self.idx   = idx
        self.cash  = 0
        self.power = 0
        self.control=False
        self.usage = {}
        self.split_usage=None
        self.other = {}
        self.genetic_table=pandas.read_csv("C:/Users/lomiag/PycharmProjects/Energy_Broker/Genetic_Library/Genetic_Code_ultimate.csv",index_col=0,header=0)
        ##     asks: tuples of the form ( quantity, price )
        ##     tariffs: Tariff objects to submit to the market
        ##     customers: integers representing which customers are subscribed
        ##                to your tariffs.
        self.asks = []
        self.tariffs = []
        self.customers = []
        self.market_info = {}
        self.demand=[]

    ## A function to accept the bootstrap data set.  The data set contains:
    ##     usage_data, a dict in which keys are integer customer ID numbers,
    ##                     and values are lists of customer's past usage profiles.
    ##     other_data, a dict in which 'Total Demand' is a list of past aggregate demand
    ##                 figures, 'Cleared Price' is a list of past wholesale prices,
    ##                 'Cleared Quantity' is a list of past wholesale quantities,
    ##                 and 'Difference' is a list of differences between cleared
    ##                 quantities and actual usage.
        self.predict_demand("CustomerNums.csv")
    def get_initial_data( self, usage_data, other_data ):
        """
        Get the initial information about usage and customers.
        :param usage_data:
        :param other_data:
        :return:
        """
        self.usage=usage_data
        self.other=other_data
    def save_genetics(self,ask_p_list,tar_p_list,tar_ex_list,dur_list,index):
        """
        Save the Genetic Material
        :param ask_p_list: ask price list per section
        :param tar_p_list: tarif price list per section
        :param tar_ex_list: exit price list per section
        :param dur_list: tarif duration list per section
        :return: None
        """
        data={"AskPrice":ask_p_list,"TarifPrice":tar_p_list,"ExitFee":tar_ex_list,"Duration":dur_list}
        gen_code=pandas.DataFrame(data,index=["Section I","Section II","Section III"])
        self.genetic_table=gen_code
        gen_code.to_csv("C:/Users/lomiag/PycharmProjects/Energy_Broker/Genetic_Library/Genetic_Code_{}.csv".format(index))
    def upload_genes(self,index):
        self.genetic_table=pandas.read_csv("C:/Users/lomiag/PycharmProjects/Energy_Broker/Genetic_Library/Genetic_Code_{}.csv".format(index),header=0,index_col=0)


    def create_mutation_table(self):
        data={"AskPrice":[rnd.uniform(0.1,2),rnd.uniform(0.1,2),rnd.uniform(0.1,2)],
              "TarifPrice":[rnd.uniform(0.1,2),rnd.uniform(0.1,2),rnd.uniform(0.1,2)],
              "ExitFee":[rnd.uniform(0.1,2),rnd.uniform(0.1,2),rnd.uniform(0.1,2)],
              "Duration":[rnd.randint(1,3),rnd.randint(1,3),rnd.randint(1,3)]}
        mutation_table = pandas.DataFrame(data, index=["Section I", "Section II", "Section III"])
        return mutation_table

    def apply_mutation_multiplication(self,mutaion):
        self.genetic_table=self.genetic_table.multiply(mutaion)
        return self.genetic_table

    def apply_mutation_combine(self,gene_2):
        self.genetic_table=self.genetic_table.add(gene_2)
        self.genetic_table = self.genetic_table.multiply(0.5)
        return self.genetic_table

    def apply_mutation_reverse(self):
        self.genetic_table=self.genetic_table.iloc[::-1]
        self.genetic_table.index=self.genetic_table.index[::-1]
        return self.genetic_table

    def predict_demand(self,data):
        """
        Predicts the demand per hour based on the data
        :param data: customer data
        :return: predicted demand at hour LIST
        """
        dataF=pandas.read_csv(data,header=0, index_col=0)
        x = [str(i) for i in range(336)]
        y=[]
        for hour in x:
            y.append(dataF[hour].mean())
        self.demand=y
        return y[:24]

    def plot_demand(self):
        plt.plot(self.demand)
        plt.show()
    ## Returns a list of asks of the form ( price, quantity ).
    def post_asks( self,step):
        #For some reason the simulation is not selling anything if I do not submit and ask despite the fact that I have
        #reserve energy.
        time_of_day = step % 24
        if time_of_day<=4 or time_of_day>=20:
            ask_price=self.genetic_table["AskPrice"]["Section I"]
        elif time_of_day>8 and time_of_day<16:
            ask_price = self.genetic_table["AskPrice"]["Section III"]
        else:
            ask_price = self.genetic_table["AskPrice"]["Section II"]

        # ask_quant=((self.demand[(step%24)]*100)-self.power)//100
        # print(ask_quant)
        self.asks = [(self.demand[time_of_day]*ask_price,max(0,(self.demand[time_of_day]*100-self.power))) for i in range(1,101)]
        # print("Broker: ",self.idx,self.asks)

        return self.asks
    ## Returns a list of Tariff objects.
    def get_other_data(self):
        self.other_d = pandas.read_csv("C:/Users/lomiag/PycharmProjects/Energy_Broker/OtherData.csv",index_col=0,header=0)

    def post_tariffs(self,step):
        time_of_day=step%24
        if time_of_day<=4 or time_of_day>=20:
            tar_price=self.genetic_table["TarifPrice"]["Section I"]+self.genetic_table["AskPrice"]["Section I"]
            duration=self.genetic_table["Duration"]["Section I"]
            exit_fee=self.genetic_table["ExitFee"]["Section I"]
        elif time_of_day>8 and time_of_day<16:
            tar_price = self.genetic_table["TarifPrice"]["Section III"]+self.genetic_table["AskPrice"]["Section III"]
            duration = self.genetic_table["Duration"]["Section III"]
            exit_fee = self.genetic_table["ExitFee"]["Section III"]
        else:
            tar_price = self.genetic_table["TarifPrice"]["Section II"]+self.genetic_table["AskPrice"]["Section II"]
            duration = self.genetic_table["Duration"]["Section II"]
            exit_fee = self.genetic_table["ExitFee"]["Section II"]
        duration=min(duration,7)
        exit_fee = min(2000, exit_fee)

        tar = [Tariff( self.idx, price=tar_price*self.demand[time_of_day], duration= duration, exitfee= duration)]
        # print(tar[0])

        return tar
    ## Receives data for the last time period from the server.
    def receive_message(self, msg):
        self.market_info = msg
        print(self.cash)
        # print(msg)
        # print("Cash: ",self.cash,"Power: ",self.power)
        # print(self.market_info)
        # print("Broker: ", self.idx, "Cash: ",self.cash,"Power: ",self.power)
        
    ## Returns a negative number if the broker doesn't have enough energy to
    ## meet demand.  Returns a positive number otherwise.
    def get_energy_imbalance(self, data):
        return self.power

    def gain_revenue(self, customers, data):
        for c in self.customers:
            self.cash += data[c] * customers[c].tariff.price
            self.power -= data[c]

    ## Alter broker's cash balance based on supply/demand match.
    def adjust_cash( self, amt):
        self.cash += amt

def main():
    b = Broker(1)
    b.get_initial_data("CustomerNums.csv","OtherData.csv")
    b.predict_demand("CustomerNums.csv")
    # b.plot_demand()
    b.save_genetics([0.9,1.1,0.9],[1.5,2,1.5],[100,500,100],[1,4,1],"1")

if __name__== "__main__":
    main()