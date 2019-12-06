import random

## Return a uniformly random number between low and high
def get_rand_between( low, high ):

    spread = high - low
    return low + ( random.random() * spread )

## Given a marginal cost, return a random bid according to the probability distribution
## probs.
def get_random_bid( mc ):

    p = random.random()

    probs = [ 0.5, 0.3, 0.1, 0.05, 0.025, 0.025 ]

    for i in range( 1, len( probs ) ):
        if p < sum( probs[:i] ):
            if mc == 0.0: mc = 10.0
            return get_rand_between( i * mc, (i+2) * mc )
    return get_rand_between( i * mc, (i+2) * mc )
