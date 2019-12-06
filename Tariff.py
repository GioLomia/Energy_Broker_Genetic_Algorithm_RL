import math
import random

class Tariff:

    def __init__( self, idx, price=0, duration=0, exitfee=0 ):
        self.publisher = idx
        self.price     = price
        self.duration  = duration
        self.exitfee   = exitfee

    def dec_time( self ):
        self.duration -= 1

    def __str__( self ):
        return 'id=%s price=%s dur=%s exit=%s' % ( self.publisher, self.price, self.duration, self.exitfee )

    def __eq__( self, other ):
        return (self.publisher == other.publisher) and \
               (self.price == other.price) and \
               (self.duration == other.duration) and \
               (self.exitfee == other.exitfee)

class Customer:

    def __init__( self ):
        ## Keeps track of the customer's current tariff.
        self.tariff = None

    ## Returns a float representing the customer's usage at a certain time and
    ## at a particular temperature.
    def get_use_at_time( self, time ):
        t = time % 24
        use = 50 * (1 - math.cos( (float(t) / 24) * 2 * math.pi )) + \
              ( (random.random() * 30) - 15 )+ 25
##        use += abs( temp - 50 ) - 15
        if use < 0: return 0
        return use

    def update_tariff( self, t ):
        self.tariff = t

    ## Takes a list of Tariff objects and choose one to subscribe to.
    def choose_tariff( self, tariffs ):

        def value(tariff):
            return (tariff.price * self.get_use_at_time(0)) + \
                    0.5 * tariff.exitfee

        t_vec = [ (value(t), t) for t in tariffs ]
        t_vec.sort()

        if self.tariff is not None and self.tariff.duration > 0:
            if t_vec[0][0] < value(self.tariff):
                return self.tariff
            else:
                self.update_tariff( t_vec[0][1] )
                return self.tariff
        else:
            self.update_tariff( t_vec[0][1] )
            return self.tariff
