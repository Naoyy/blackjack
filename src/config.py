
class Color:
    pique='pique' 
    coeur='coeur' 
    trefle='trèfle' 
    carreau= 'carreau'

class End:
    win = 1
    lose = 0
    draw = -1
    proceed = -2

class Gain: #TODO attention au paiement cf notes carnet
    hit = 1
    bj = 1.5
    double = 2
    stay = 1

class Loss:
    hit= -1
    bj = -1
    double = -2
    stay = -1
    
