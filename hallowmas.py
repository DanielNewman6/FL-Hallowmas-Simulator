import random
import itertools
from fractions import Fraction
import numpy
import typing
import time

#numpy is strange about array comparisons; it returns an array of elementwise comparisons. This is inconvenient, so I'm overloading it
#unfortunately numpy.array is just a helper function to construct ndarray, so we have to subclass ndarray and make our own helper function
#it will not be a very general helper function, because I am lazy
class my_array(numpy.ndarray):
    def __eq__(self, other):
        return not (self-other).any()

    def dominates(self,other):
        return (self>=other).all()

def array(in_list):
    return my_array((len(in_list),), buffer=numpy.array(in_list),offset=0,dtype=numpy.int_)

def unique_list(in_list):
    if isinstance(in_list[0],typing.Hashable):
        return list(set(in_list))
    else:
        temp = []
        for i in in_list:
            if i not in temp: temp.append(i)
        return temp

##probability distributions written as e.g. [(1,Fraction('0.33')),(2,Fraction('0.67'))]
class pdf:
    def __init__(self, value):
        if sum([i[1] for i in value])!=1:
            print(value)
            print(sum([i[1] for i in value]))
            raise Exception("Probabilities must sum to 1")
        values = unique_list([i[0] for i in value])
        temp = [(i, sum([j[1] for j in value if j[0]==i])) for i in values]
        temp = [i for i in temp if i[1]>0]
        self.value=temp

    def __add__(self,other):
        temp = [(i[0]+j[0], i[1]*j[1]) for i in self.value for j in other.value]
        return pdf(temp)

    def menaceBonus(self,items):
        temp=[]
        if items>=0:
            chance=Fraction('0.15')*((Fraction('0.75')**items)-1)/(Fraction('0.75')-1)
            for i in self.value:
                temp.append((i[0],i[1]*max(1-i[0]*chance,0)))
                if i[0]*chance<=1:
                    temp.append((i[0]+1,i[1]*min(i[0]*chance,1)))
                else:
                    temp.append((i[0]+1,i[1]*(1-min(max(i[0]*chance-1,0),1))))
                    temp.append((i[0]+2,i[1]*min(max(i[0]*chance-1,0),1)))
        else:
            chance=Fraction('0.15')*((Fraction('0.75')**abs(items))-1)/(Fraction('0.75')-1)
            for i in self.value:
                temp.append((i[0],i[1]*max(1-i[0]*chance,0)))
                if i[0]*chance<=1:
                    temp.append((i[0]-1,i[1]*min(i[0]*chance,1)))
                else:
                    temp.append((i[0]-1,i[1]*(1-min(max(i[0]*chance-1,0),1))))
                    temp.append((i[0]-2,i[1]*min(max(i[0]*chance-1,0),1)))
        return pdf(temp)

    def menaceBonusMix(self,itemsa,itemsb):
        temp=[]
        if itemsa>=0:
            chancea=Fraction('0.15')*((Fraction('0.75')**itemsa)-1)/(Fraction('0.75')-1)
            for i in self.value:
                temp.append((i[0],i[1]*max(1-i[0][0]*chancea,0)))
                if i[0][0]*chancea<=1:
                    temp.append((i[0]+array([1,0,0,0]),i[1]*min(i[0][0]*chancea,1)))
                else:
                    temp.append((i[0]+array([1,0,0,0]),i[1]*(1-min(max(i[0][0]*chancea-1,0),1))))
                    temp.append((i[0]+array([2,0,0,0]),i[1]*min(max(i[0][0]*chancea-1,0),1)))
        else:
            chancea=Fraction('0.15')*((Fraction('0.75')**abs(itemsa))-1)/(Fraction('0.75')-1)
            for i in self.value:
                temp.append((i[0],i[1]*max(1-i[0][0]*chancea,0)))
                if i[0]*chancea<=1:
                    temp.append((i[0]-array([1,0,0,0]),i[1]*min(i[0][0]*chancea,1)))
                else:
                    temp.append((i[0]-array([1,0,0,0]),i[1]*(1-min(max(i[0][0]*chancea-1,0),1))))
                    temp.append((i[0]-array([2,0,0,0]),i[1]*min(max(i[0][0]*chancea-1,0),1)))
        tempPDF = pdf(temp)
        tempb=[]
        if itemsb>=0:
            chanceb=Fraction('0.15')*((Fraction('0.75')**itemsb)-1)/(Fraction('0.75')-1)
            for i in tempPDF.value:
                tempb.append((i[0],i[1]*max(1-i[0][1]*chanceb,0)))
                if i[0][1]*chanceb<=1:
                    tempb.append((i[0]+array([0,1,0,0]),i[1]*min(i[0][1]*chanceb,1)))
                else:
                    tempb.append((i[0]+array([0,1,0,0]),i[1]*(1-min(max(i[0][1]*chanceb-1,0),1))))
                    tempb.append((i[0]+array([0,2,0,0]),i[1]*min(max(i[0][1]*chanceb-1,0),1)))
        else:
            chanceb=Fraction('0.15')*((Fraction('0.75')**abs(itemsb))-1)/(Fraction('0.75')-1)
            for i in tempPDF.value:
                tempb.append((i[0],i[1]*max(1-i[0][1]*chanceb,0)))
                if i[0][1]*chanceb<=1:
                    tempb.append((i[0]-array([0,1,0,0]),i[1]*min(i[0][1]*chanceb,1)))
                else:
                    tempb.append((i[0]-array([0,1,0,0]),i[1]*(1-min(max(i[0][1]*chanceb-1,0),1))))
                    tempb.append((i[0]-array([0,2,0,0]),i[1]*min(max(i[0][1]*chanceb-1,0),1)))
        return pdf(tempb)

    def atMost(self,threshold):
        return sum([i[1] for i in self.value if i[0]<=threshold])

def menaceBonus(amount,items):
    bonus=0
    chance=0.15*((0.75**items)-1)/(0.75-1)
    if random.random()<chance*amount: bonus+=1
    if random.random()<(chance*amount)-1: bonus+=1
    return amount+bonus

def elmo(items,scint=True,coll=True):
    actionPDF = pdf([(3+4*scint,Fraction('0.33')),(1,Fraction('0.33')),(3+4*coll,Fraction('0.34'))]).menaceBonus(items)
    masqueradeSpace = [actionPDF]
    while masqueradeSpace[-1].atMost(27) > Fraction(1,1000000000): #although arbitrarily long runs are possible, past a point their contribution to the average is negligble.
        masqueradeSpace.append(masqueradeSpace[-1]+actionPDF)
    endings = [1-j.atMost(27) for j in masqueradeSpace]
    avgLength = 0
    for i in range(1,len(endings)):
        avgLength += (i+1)*(endings[i]-endings[i-1])
    avgLength += 1*endings[0]
    return [round(float(28/(avgLength+3)),3), round(float(avgLength+2),3)]

def dunstan(items,tls=True,mask=True):
    actionPDF = pdf([(3+2*mask,Fraction('0.33')),(1,Fraction('0.33')),(3+4*tls*mask,Fraction('0.34'))]).menaceBonus(items)
    masqueradeSpace = [actionPDF]
    while masqueradeSpace[-1].atMost(27) > Fraction(1,1000000000):
        masqueradeSpace.append(masqueradeSpace[-1]+actionPDF)
    endings = [1-j.atMost(27) for j in masqueradeSpace]
    avgLength = 0
    for i in range(1,len(endings)):
        avgLength += (i+1)*(endings[i]-endings[i-1])
    avgLength += 1*endings[0]
    return [round(float(28/(avgLength+3)),3), round(float(avgLength+2),3)]

def infant(items,sa=True,mask=True):
    actionPDF = pdf([(3+2*mask,Fraction('0.33')),(1,Fraction('0.33')),(3+4*sa*mask,Fraction('0.34'))]).menaceBonus(items)
    masqueradeSpace = [actionPDF]
    while masqueradeSpace[-1].atMost(27) > Fraction(1,1000000000):
        masqueradeSpace.append(masqueradeSpace[-1]+actionPDF)
    endings = [1-j.atMost(27) for j in masqueradeSpace]
    avgLength = 0
    for i in range(1,len(endings)):
        avgLength += (i+1)*(endings[i]-endings[i-1])
    avgLength += 1*endings[0]
    return [round(float(28/(avgLength+3)),3), round(float(avgLength+2),3)]

def pavilion(items):
    actionPDF = pdf([(5,Fraction('0.33')),(1,Fraction('0.33')),(7,Fraction('0.34'))]).menaceBonus(items)
    masqueradeSpace = [actionPDF]
    while masqueradeSpace[-1].atMost(27) > Fraction(1,1000000000):
        masqueradeSpace.append(masqueradeSpace[-1]+actionPDF)
    endings = [1-j.atMost(27) for j in masqueradeSpace]
    avgLength = 0
    for i in range(1,len(endings)):
        avgLength += (i+1)*(endings[i]-endings[i-1])
    avgLength += 1*endings[0]
    return [round(float(28/(avgLength+3)),3), round(float(avgLength+2),3)]

def pavilionBreakEven(items):
    #start=time.time()
    actions = 0
    absinthe = 0
    length=100000000
    for i in range(0,length):
        nightmares = 0
        actions+=3
        while nightmares<28:
            airs = random.randint(1,100)
            if airs<=33:
                nightmares+=menaceBonus(5,items)
            elif airs<=66 or absinthe<0:
                nightmares+=menaceBonus(1,items)
                absinthe+=random.randint(1,2)
            else:
                nightmares+=menaceBonus(7,items)
                absinthe-=5
            actions+=1
    #end=time.time()
    #print(end-start)
    return [28*length/actions, (actions/length)-1]

def carousel(items,gainper,chancegain,travel):
    actionPDF = pdf([(gainper,chancegain),(0,1-chancegain)]).menaceBonus(items)
    space = [actionPDF]
    while space[-1].atMost(27) > Fraction(1,1000000000):
        space.append(space[-1]+actionPDF)
    endings = [1-j.atMost(27) for j in space]
    avgLength = 1+travel
    for i in range(1,len(endings)):
        avgLength += (i+1)*(endings[i]-endings[i-1])
    avgLength += 1*endings[0]
    return round(float(28/avgLength),3)

def carouselmix(itemsa,gainpera,chancegaina,itemsb,gainperb,chancegainb,travel):
    #start=time.time()
    spirit = 0
    menacea = 0
    menaceb = 0
    actions = 0
    for i in range(0,10000000):
        actions+=1
        if random.random()<chancegaina: menacea+=menaceBonus(gainpera,itemsa)
        if random.random()<chancegainb: menaceb+=menaceBonus(gainperb,itemsb)
        if menacea>=28 and menaceb<28:
            spirit+=28
            actions+=1+travel
            menacea=0
        elif menacea<28 and menaceb>=28:
            spirit+=28
            actions+=1+travel
            menaceb=0
        elif menacea>=28 and menaceb>=28:
            spirit+=56
            actions+=2+travel
            menacea=0
            menaceb=0
    #end=time.time()
    #print(end-start)
    return spirit/actions

''' #needs work! very inefficient
def carouselmix2(itemsa,gainpera,chancegaina,itemsb,gainperb,chancegainb,travel):
    actionPDF = pdf([(array([gainpera,gainperb,0,0]),chancegaina*chancegainb),(array([gainpera,0,0,0]),chancegaina*(1-chancegainb)),(array([0,gainperb,0,0]),chancegainb*(1-chancegaina)),(array([0,0,0,0]),(1-chancegaina)*(1-chancegainb))])#.menaceBonusMix(itemsa,itemsb)
    actionPDF = actionPDF.menaceBonusMix(itemsa,itemsb)
    state=actionPDF
    if len(actionPDF.value)==2:
        length=1400
    else:
        length=140
    for i in range(0,length):
        print(i/length)
        state=state+actionPDF
        temp = state.value
        temp = [(array([0,i[0][1],i[0][2]+1,i[0][3]]),i[1]) for i in temp if i[0][0]>=28]+[i for i in temp if i[0][0]<28]
        temp = [(array([i[0][0],0,i[0][2],i[0][3]+1]),i[1]) for i in temp if i[0][1]>=28]+[i for i in temp if i[0][1]<28]
        state = pdf(temp)
    return round(float(sum([i[1]*28*(i[0][2]+i[0][3])/(length+(i[0][2]+i[0][3])*(1+travel)) for i in state.value])),3)
'''

def hungry(nitems,witems,fillnitems,scitems,method='Duchess'):
    spirit=0
    nightmares=0
    scandal=0
    wounds=0
    actions=0
    watchful=0
    for i in range(0,150000):#should be sufficient to get sample mean s.d. ~0.01
        while (nightmares<16 and nitems==0) or nightmares<14:
            actions+=1
            wounds+=menaceBonus(1,2*witems)
            nightmares+=menaceBonus(random.randint(1,20),nitems)
            watchful-=50
            if wounds>=28:
                actions+=1
                spirit+=28
                wounds=0
        if method=='Duchess':
            while nightmares<28:
                actions+=1
                scandal+=menaceBonus(1+3,scitems)
                nightmares+=menaceBonus(4,fillnitems)
                if scandal>=28:
                    actions+=1
                    spirit+=28
                    scandal=0
            spirit+=28
            actions+=1
            nightmares=0
        elif method=='Underclay':
            while nightmares<28:
                actions+=1
                nightmares+=menaceBonus(5,fillnitems)
            spirit+=28
            actions+=1
            nightmares=0
    return [spirit/actions, watchful/actions]

def missive(nitems,sitems,witems,fillnitems):
    spirit=0
    nightmares=0
    suspicion=0
    wounds=0
    actions=0
    for i in range(0,200000):
        while nightmares<20:
            actions+=2
            nightmares+=menaceBonus(random.randint(2,14),nitems)
            suspicion+=menaceBonus(random.randint(1,7),sitems)
            wounds+=menaceBonus(random.randint(1,9),witems)
            if wounds>=28:
                actions+=1
                spirit+=28
                wounds=0
            elif wounds==27 or (witems>0 and wounds>=25):
                actions+=2
                spirit+=28
                wounds=0
                nightmares+=menaceBonus(1,nitems)
            if suspicion==27:
                actions+=2
                spirit+=28
                suspicion=0
            elif suspicion>=28:
                actions+=1
                spirit+=28
                suspicion=0
        while nightmares<28:
            actions+=1
            nightmares+=menaceBonus(5,fillnitems)
        actions+=1
        spirit+=28
        nightmares=0
    return spirit/actions

#(scandal, suspicion, nightmares, wounds)
burdens=[(0,0,0,0),(1,1,1,1),(0,0,1,0),(1,1,2,1),(0,2,0,1),(1,3,1,2),(0,2,1,1),(1,4,2,2)]
hats=[(0,0,0,0),(1,0,0,0),(0,1,0,0),(0,0,1,0)]
clothing=[(0,0,0,0),(1,0,0,0)]
adornment=[(0,0,0,0),(1,0,0,0),(0,0,1,0),(0,0,0,1)]
weapon=[(0,0,0,0),(1,0,0,0),(0,1,0,0),(0,0,2,0),(0,0,1,0),(0,0,0,1)]
boots=[(0,0,0,0),(1,0,0,0)]
luggage=[(0,0,0,0),(0,1,0,0),(0,0,1,0)]
companion=[(0,0,0,0), (0,1,0,0),(0,0,1,0),(-1,0,1,0),(0,0,0,2),(1,0,0,0)]
affiliation=[(0,0,0,0)]
homeComfort=[(0,0,0,0),(1,0,0,0),(0,0,1,0),(0,0,0,1)]
crew=[(0,0,0,0),(1,0,0,0)]

possibilities = [tuple([sum(i) for i in zip(*j)]) for j in itertools.product(burdens,hats,clothing,adornment,weapon,boots,luggage,companion,affiliation,homeComfort,crew)]
possibilities = list(set(possibilities))

possibilitiesWoesel = [[sum(i) for i in zip(*j)] for j in itertools.product(burdens,hats,clothing,adornment,weapon,boots,luggage,affiliation,homeComfort,crew)]
for i in possibilitiesWoesel: i[3]+=2
possibilitiesWoesel = [tuple(i) for i in possibilitiesWoesel]
possibilitesWoesel = list(set(possibilitiesWoesel))

possibilitiesMask = [tuple([sum(i) for i in zip(*j)]) for j in itertools.product(burdens,clothing,adornment,weapon,boots,luggage,companion,affiliation,homeComfort,crew)]
possibilitiesMask = list(set(possibilitiesMask))
'''
print('Elmo')
for k in [True, False]:
    for j in [True, False]:
        if k or j:
            for i in sorted(list(set([i[1] for i in possibilitiesMask]))):
                print('items '+str(i)+' scintillack '+str(j)+' collated '+str(k)+' '+str(elmo(i,scint=j,coll=k)))
        else:
            for i in sorted(list(set([i[1] for i in possibilities]))):
                print('items '+str(i)+' scintillack '+str(j)+' collated '+str(k)+' '+str(elmo(i,scint=j,coll=k)))

print('\r\nFalse Curriculum Vitae')
for i in list(set([i[1] for i in possibilitiesWoesel])):
    print('items '+str(i)+' '+str(carousel(i,3,1,0)))


print('\r\nDunstan')
for k in [True, False]:
    for j in [True, False]:
        if k:
            for i in sorted(list(set([i[0] for i in possibilitiesMask]))):
                print('items '+str(i)+' mask '+str(k)+' tls '+str(j)+' '+str(dunstan(i,mask=k,tls=j)))
        elif not j:
            for i in sorted(list(set([i[0] for i in possibilities]))):
                print('items '+str(i)+' mask '+str(k)+' '+str(dunstan(i,mask=k,tls=j)))

print('\r\nScandal Woesel')
for i in sorted(list(set([i[0] for i in possibilities]))):
    print('items '+str(i)+' '+str(carousel(i,2,1,0)))

print('\r\nShrouded Soiree')
print(menaceBonus(2,max([i[0] for i in possibilities]))*0.9)
print(carousel(max([i[0] for i in possibilities]),2,Fraction('0.9'),1))

print('\r\nRoof Below')
for k in [True, False]:
    for j in [True, False]:
        if k:
            for i in sorted(list(set([i[3] for i in possibilitiesMask]))):
                print('items '+str(i)+' mask '+str(k)+' sa '+str(j)+' '+str(infant(i,mask=k,sa=j)))
        elif not j:
            for i in sorted(list(set([i[3] for i in possibilities]))):
                print('items '+str(i)+' mask '+str(k)+' '+str(infant(i,mask=k,sa=j)))

print('\r\nWounds Woesel')
for i in range(3,max([i[3] for i in possibilitiesWoesel])+1):
    p1ExtraJourney = min(2*0.15*((0.75**i)-1)/(0.75-1),1)
    p2ExtraJourney = max(2*0.15*((0.75**i)-1)/(0.75-1),1)-1
    p2ExtraProgress = min((5*0.15*((0.75**i)-1)/(0.75-1))-1,1)
    pQuick = p1ExtraJourney*(p2ExtraProgress**3)+3*p2ExtraJourney*(p2ExtraProgress**2)*(1-p2ExtraProgress)
    avg = 4*(1-pQuick)+(28/6)*pQuick
    print(str(i)+' '+str(pQuick)+' '+str(avg))

print('\r\nPavilion')
for i in sorted(list(set([i[2] for i in possibilitiesMask]))):
    print('items '+str(i)+' absinthe True '+str(pavilion(i)))
for i in sorted(list(set([i[2] for i in possibilitiesMask]))):
    print('items '+str(i)+' absinthe False '+str(pavilionBreakEven(i)))

print('\r\nConsole')
for i in sorted(list(set([i[2] for i in possibilitiesWoesel]))):
    print('items '+str(i)+' '+str(carousel(i,5,1,0)))

print('\r\nListen to the silence')
for i in sorted(list(set([i[2] for i in possibilities]))):
    for j in range(4,8):
        print('items '+str(i)+' SotD '+str(j)+' '+str(carousel(i,5,Fraction(13-j,10),0)))

print('\r\nAttend and speak of terrible things - Woesel')
for i in sorted(list(set([(i[2],i[0]) for i in possibilitiesWoesel]))):
    print('nightmares '+str(i[0])+' scandal '+str(i[1])+' '+str(carouselmix(i[0],4,1,i[1],4,1,0)))

print('\r\nAttend and speak of terrible things - non-Woesel')
for i in sorted(list(set([(i[2],i[0]) for i in possibilities]))):
    print('nightmares '+str(i[0])+' scandal '+str(i[1])+' '+str(carouselmix(i[0],4,1,i[1],1,1,0)))

print('\r\nCarve')
for i in sorted(list(set([(i[2],i[3]) for i in possibilitiesWoesel]))):
    print('nightmares '+str(i[0])+' wounds '+str(i[1])+' '+str(carouselmix(i[0],5,1,i[1],3,1,2)))

print('\r\nCoax')
for i in sorted(list(set([(i[0],i[3]) for i in possibilitiesWoesel]))):
    print('scandal '+str(i[0])+' wounds '+str(i[1])+' '+str(carouselmix(i[0],5,1,i[1],3,1,2)))

print('\r\nScour')
for i in sorted(list(set([(i[2],i[1]) for i in possibilities]))):
    print('nightmares '+str(i[0])+' suspicion '+str(i[1])+' '+str(carouselmix(i[0],5,1,i[1],3,1,2)))


'''
#(scandal, nightmares, wounds, name)
#burdens: [(0,1,0,'no_wings no_diminished '),(1,2,1,'wings no_diminished '),(0,1,1,'no_wings diminished '),(1,2,2,'wings diminished ')]
#hats: [(1,0,0,'modish '),(0,1,0,'sporing ')]
#clothing: [(1,0,0,'barrel ')]
#adornment: [(1,0,0,'necktie '), (0,1,0,'reptile '), (0,0,1,'guiltgift ')]
#weapon: [(1,0,0,'census '),(0,2,0,'law-glass '),(0,1,0,'vakeclaw '),(0,0,1,'mark/liturgy ')]
#boots: [(1,0,0,'stockings ')]
#companion: [(0,1,0,'albatross '),(0,0,2,'woesel '),(1,0,0,'thespian ')]
#crew: [(1,0,0,'rantipoles ')]
#homeComfort: [(1,0,0,'newt '),(0,1,0,'midnight/elephant '),(0,0,1,'relic ')]
#luggage: [(0,1,0,'chess_set ')]

#1 Vake Claw
#2 Mark of Disdain/Liturgy of Metes and Bounds
#3 At the Shore of Midnight, 5th Edition/An Elephant that is Yet to be Refuted
#4 Diamond Newt
#5 Sound of Wings
#6 Law-Glass
#7 Relic of the Revolution
#8 Red-and-Gold Reptile
#9 Guiltgift Pendant
#10 High-Rolling Rantipoles
#11 Portable Mutable Unlosable Chess-Set
#12 I WILL NOT BE DIMINISHED


def sum2(iterable):
    if isinstance(iterable[0], str): return iterable
    else: return sum(iterable)
'''
#just nightmares+wounds
possibilitiesHunger = [tuple([sum2(i) for i in zip(*j)]) for j in itertools.product([(0,1,0,'no_wings no_diminished ', array([0,0,0,0,0,0,0,0,0,0,0,0])),(1,2,1,'wings no_diminished ', array([0,0,0,0,1,0,0,0,0,0,0,0])),(0,1,1,'no_wings diminished ', array([0,0,0,0,0,0,0,0,0,0,0,1])),(1,2,2,'wings diminished ', array([0,0,0,0,1,0,0,0,0,0,0,1]))],
                                                                                    [(0,1,0,'sporing ', array([0,0,0,0,0,0,0,0,0,0,0,0]))],
                                                                                    [(0,0,0,'N/A ', array([0,0,0,0,0,0,0,0,0,0,0,0]))],
                                                                                    [(0,0,0,'nothing ', array([0,0,0,0,0,0,0,0,0,0,0,0])),(0,1,0,'reptile ', array([0,0,0,0,0,0,0,1,0,0,0,0])), (0,0,1,'guiltgift ', array([0,0,0,0,0,0,0,0,1,0,0,0]))],
                                                                                    [(0,0,0,'nothing ', array([0,0,0,0,0,0,0,0,0,0,0,0])),(0,2,0,'law-glass ', array([0,0,0,0,0,1,0,0,0,0,0,0])),(0,1,0,'vakeclaw ', array([1,0,0,0,0,0,0,0,0,0,0,0])),(0,0,1,'mark/liturgy ', array([0,1,0,0,0,0,0,0,0,0,0,0]))],
                                                                                    [(0,0,0,'N/A ', array([0,0,0,0,0,0,0,0,0,0,0,0]))],
                                                                                    [(0,1,0,'albatross ', array([0,0,0,0,0,0,0,0,0,0,0,0])),(0,0,2,'woesel ', array([0,0,0,0,0,0,0,0,0,0,0,0]))],
                                                                                    [(0,0,0,'nothing ', array([0,0,0,0,0,0,0,0,0,0,0,0])),(1,0,0,'rantipoles ', array([0,0,0,0,0,0,0,0,0,1,0,0]))],
                                                                                    [(0,0,0,'nothing ', array([0,0,0,0,0,0,0,0,0,0,0,0])),(0,1,0,'midnight/elephant ', array([0,0,1,0,0,0,0,0,0,0,0,0])),(0,0,1,'relic ', array([0,0,0,0,0,0,1,0,0,0,0,0]))],
                                                                                    [(0,0,0,'nothing ', array([0,0,0,0,0,0,0,0,0,0,0,0])),(0,1,0,'chess_set ', array([0,0,0,0,0,0,0,0,0,0,1,0]))])]
#just nightmares+scandal
possibilitiesHungerDuchess = [tuple([sum2(i) for i in zip(*j)]) for j in itertools.product([(0,1,0,'no_wings N/A ', array([0,0,0,0,0,0,0,0,0,0,0,0])),(1,2,1,'wings N/A ', array([0,0,0,0,1,0,0,0,0,0,0,0]))],
                                                                                           [(1,0,0,'modish ', array([0,0,0,0,0,0,0,0,0,0,0,0])),(0,1,0,'sporing ', array([0,0,0,0,0,0,0,0,0,0,0,0]))],
                                                                                           [(1,0,0,'barrel ', array([0,0,0,0,0,0,0,0,0,0,0,0]))],
                                                                                           [(1,0,0,'necktie ', array([0,0,0,0,0,0,0,0,0,0,0,0])), (0,1,0,'reptile ', array([0,0,0,0,0,0,0,1,0,0,0,0]))],
                                                                                           [(1,0,0,'census ', array([0,0,0,0,0,0,0,0,0,0,0,0])),(0,2,0,'law-glass ', array([0,0,0,0,0,1,0,0,0,0,0,0])),(0,1,0,'vakeclaw ', array([1,0,0,0,0,0,0,0,0,0,0,0]))],
                                                                                           [(1,0,0,'stockings ', array([0,0,0,0,0,0,0,0,0,0,0,0]))],
                                                                                           [(0,0,2,'woesel ', array([0,0,0,0,0,0,0,0,0,0,0,0]))],
                                                                                           [(0,0,0,'nothing ', array([0,0,0,0,0,0,0,0,0,0,0,0])),(1,0,0,'rantipoles ', array([0,0,0,0,0,0,0,0,0,1,0,0]))],
                                                                                           [(0,0,0,'nothing ', array([0,0,0,0,0,0,0,0,0,0,0,0])),(1,0,0,'newt ', array([0,0,0,1,0,0,0,0,0,0,0,0])),(0,1,0,'midnight/elephant ', array([0,0,1,0,0,0,0,0,0,0,0,0]))],
                                                                                           [(0,0,0,'nothing ', array([0,0,0,0,0,0,0,0,0,0,0,0])),(0,1,0,'chess_set ', array([0,0,0,0,0,0,0,0,0,0,1,0]))])]
#just nightmares
possibilitiesHungerUnderclay = [tuple([sum2(i) for i in zip(*j)]) for j in itertools.product([(0,1,0,'no_wings N/A ', array([0,0,0,0,0,0,0,0,0,0,0,0])),(1,2,1,'wings N/A ', array([0,0,0,0,1,0,0,0,0,0,0,0]))],
                                                                                             [(0,1,0,'sporing ', array([0,0,0,0,0,0,0,0,0,0,0,0]))],
                                                                                             [(0,0,0,'N/A ', array([0,0,0,0,0,0,0,0,0,0,0,0]))],
                                                                                             [(0,0,0,'N/A ', array([0,0,0,0,0,0,0,0,0,0,0,0]))],
                                                                                             [(0,0,0,'nothing ', array([0,0,0,0,0,0,0,0,0,0,0,0])),(0,2,0,'law-glass ', array([0,0,0,0,0,1,0,0,0,0,0,0])),(0,1,0,'vakeclaw ', array([1,0,0,0,0,0,0,0,0,0,0,0]))],
                                                                                             [(0,0,0,'N/A ', array([0,0,0,0,0,0,0,0,0,0,0,0]))],
                                                                                             [(0,0,2,'woesel ', array([0,0,0,0,0,0,0,0,0,0,0,0]))],
                                                                                             [(0,0,0,'N/A ', array([0,0,0,0,0,0,0,0,0,0,0,0]))],
                                                                                             [(0,0,0,'nothing ', array([0,0,0,0,0,0,0,0,0,0,0,0])),(0,1,0,'midnight/elephant ', array([0,0,1,0,0,0,0,0,0,0,0,0]))],
                                                                                             [(0,0,0,'nothing ', array([0,0,0,0,0,0,0,0,0,0,0,0])),(0,1,0,'chess_set ', array([0,0,0,0,0,0,0,0,0,0,1,0]))])]


SoHungryDuchessCombos = []

print('\r\nPreparing So Hungry - Duchess')
for iVals, iGroup in itertools.groupby(sorted([(i[1],i[2],i[3],i[4]) for i in possibilitiesHunger]), lambda x: (x[0],x[1])):
    for jVals, jGroup in itertools.groupby(sorted([(i[1],i[0],i[3],i[4]) for i in possibilitiesHungerDuchess]), lambda x: (x[0],x[1])):
        iGroup=list(iGroup)
        jGroup=list(jGroup)
        if not set([iFit[2][0][0] for iFit in iGroup]).isdisjoint([jFit[2][0][0] for jFit in jGroup]):#ugly, but works: check both outfits have compatible Burdens i.e. both wings or both no_wings
            SoHPerAction=hungry(iVals[0],iVals[1],jVals[0],jVals[1],method='Duchess')[0]
            for iFit in iGroup:
                for jFit in jGroup:
                    if iFit[2][0][0]==jFit[2][0][0]:
                        #print(''.join(iFit[2])+''.join(jFit[2])+' nightmares '+str(iVals[0])+' wounds '+str(iVals[1])+' fill nightmares '+str(jVals[0])+' fill scandal '+str(jVals[1])+' Duchess '+str(SoHPerAction))
                        SoHungryDuchessCombos.append([numpy.logical_or(iFit[3],jFit[3]),iVals[0],iVals[1],jVals[0],jVals[1],'Duchess',SoHPerAction])

SoHungryConsoleCombos = []

print('Preparing So Hungry - Console')
for iVals, iGroup in itertools.groupby(sorted([(i[1],i[2],i[3],i[4]) for i in possibilitiesHunger]), lambda x: (x[0],x[1])):
    for jVals, jGroup in itertools.groupby(sorted([(i[1],i[0],i[3],i[4]) for i in possibilitiesHungerUnderclay]), lambda x: (x[0],x[1])):
        iGroup=list(iGroup)
        jGroup=list(jGroup)
        if not set([iFit[2][0][0] for iFit in iGroup]).isdisjoint([jFit[2][0][0] for jFit in jGroup]):
            SoHPerAction=hungry(iVals[0],iVals[1],jVals[0],0,method='Underclay')[0]
            iGroup=list(iGroup)
            jGroup=list(jGroup)
            for iFit in iGroup:
                for jFit in jGroup:
                    if iFit[2][0][0]==jFit[2][0][0]:
                        #print(''.join(iFit[2])+''.join(jFit[2])+' nightmares '+str(iVals[0])+' wounds '+str(iVals[1])+' fill nightmares '+str(jVals[0])+' fill scandal '+str(jVals[1])+' Underclay '+str(SoHPerAction))
                        SoHungryConsoleCombos.append([numpy.logical_or(iFit[3],jFit[3]),iVals[0],iVals[1],jVals[0],jVals[1],'Console',SoHPerAction])

optimalFits=[]
correspondenceDuchess=[]
correspondenceConsole=[]

for i in itertools.product([0,1],repeat=12):
    constraint=list(i)
    bestFit = max([j[1:] for j in SoHungryDuchessCombos if array(constraint).dominates(j[0])],key=lambda x:x[-1])
    if not bestFit in optimalFits:
        optimalFits.append(bestFit)
        correspondenceDuchess.append([''.join([str(j) for j in constraint]),len(optimalFits)-1])
    else:
        correspondenceDuchess.append([''.join([str(j) for j in constraint]),optimalFits.index(bestFit)+1])
    bestFit = max([j[1:] for j in SoHungryConsoleCombos if array(constraint).dominates(j[0])],key=lambda x:x[-1])
    if not bestFit in optimalFits:
        optimalFits.append(bestFit)
        correspondenceConsole.append([''.join([str(j) for j in constraint]),len(optimalFits)-1])
    else:
        correspondenceConsole.append([''.join([str(j) for j in constraint]),optimalFits.index(bestFit)+1])

print('Correspondences - Duchess')
print('{'+', '.join(['["'+i[0]+'"]='+str(i[1]) for i in correspondenceDuchess])+'}')
print('\r\n\r\nCorrespondences - Console')
print('{'+', '.join(['["'+i[0]+'"]='+str(i[1]) for i in correspondenceConsole])+'}')
print('\r\n\r\nOutfit details')
print('{{'+'}, {'.join([','.join([str(round(i[5],2)),str(i[0]),str(i[1]),str(i[2]),str(i[3])]) for i in optimalFits])+'}}')
'''
#(suspicion, nightmares, wounds, name)
#burdens: [(0,1,0,'no_wings no_diminished '),(1,2,1,'wings no_diminished '),(2,1,1,'no_wings diminished '),(3,2,2,'wings diminished ')]
#hats: [(0,1,0,'sporing '), (1,0,0,'pirate ')]
#adornments: [(0,1,0,'reptile '), (0,0,1,'guiltgift ')]
#weapon: [(0,2,0,'law-glass '),(1,1,0,'vakeclaw '),(0,0,1,'mark/liturgy ')]
#luggage: [(1,0,0,'six-by-two '),(0,1,0,'chess_set ')]
#companion: [(0,1,0,'albatross '),(0,0,2,'woesel '),(1,0,0,'polymath ')]
#homeComfort: [(0,0,0,'nothing '),(0,1,0,'midnight/elephant '),(0,0,1,'relic ')]

#1 sound of wings
#2 law-glass
#3 vake claw
#4 mark/liturgy
#5 six-by-two carryall
#6 sun-kissed polymath
#7 at the shore of midnight/elephant
#8 relic
#9 diminished
#10 reptile
#11 guiltgift
#12 chess set

#just suspicion
possibilitiesSend = [tuple([sum2(i) for i in zip(*j)]) for j in itertools.product([(0,1,0,'no_wings no_diminished ', array([0,0,0,0,0,0,0,0,0,0,0,0])),(1,2,1,'wings no_diminished ', array([1,0,0,0,0,0,0,0,0,0,0,0])),(2,1,1,'no_wings diminished ', array([0,0,0,0,0,0,0,0,1,0,0,0])),(3,2,2,'wings diminished ', array([1,0,0,0,0,0,0,0,1,0,0,0]))],
                                                                                  [(1,0,0,'pirate ', array([0,0,0,0,0,0,0,0,0,0,0,0]))],
                                                                                  [(0,0,0,'nothing ', array([0,0,0,0,0,0,0,0,0,0,0,0])),(1,1,0,'vakeclaw ', array([0,0,1,0,0,0,0,0,0,0,0,0]))],
                                                                                  [(0,0,0,'nothing ', array([0,0,0,0,0,0,0,0,0,0,0,0])),(1,0,0,'six-by-two ', array([0,0,0,0,1,0,0,0,0,0,0,0]))],
                                                                                  [(0,0,0,'nothing ', array([0,0,0,0,0,0,0,0,0,0,0,0])),(1,0,0,'polymath ', array([0,0,0,0,0,1,0,0,0,0,0,0]))])]
#just wounds+nightmares
possibilitiesRead = [tuple([sum2(i) for i in zip(*j)]) for j in itertools.product([(0,1,0,'no_wings no_diminished ', array([0,0,0,0,0,0,0,0,0,0,0,0])),(1,2,1,'wings no_diminished ', array([1,0,0,0,0,0,0,0,0,0,0,0])),(2,1,1,'no_wings diminished ', array([0,0,0,0,0,0,0,0,1,0,0,0])),(3,2,2,'wings diminished ', array([1,0,0,0,0,0,0,0,1,0,0,0]))],
                                                                                  [(0,1,0,'sporing ', array([0,0,0,0,0,0,0,0,0,0,0,0]))],
                                                                                  [(0,0,0,'nothing ', array([0,0,0,0,0,0,0,0,0,0,0,0])),(0,1,0,'reptile ', array([0,0,0,0,0,0,0,0,0,1,0,0])),(0,0,1,'guiltgift ', array([0,0,0,0,0,0,0,0,0,0,1,0]))],
                                                                                  [(0,0,0,'nothing ', array([0,0,0,0,0,0,0,0,0,0,0,0])),(0,2,0,'law-glass ', array([0,1,0,0,0,0,0,0,0,0,0,0])),(1,1,0,'vakeclaw ', array([0,0,1,0,0,0,0,0,0,0,0,0])),(0,0,1,'mark/liturgy ', array([0,0,0,1,0,0,0,0,0,0,0,0]))],
                                                                                  [(0,1,0,'albatross ', array([0,0,0,0,0,0,0,0,0,0,0,0])),(0,0,2,'woesel ', array([0,0,0,0,0,0,0,0,0,0,0,0]))],
                                                                                  [(0,0,0,'nothing ', array([0,0,0,0,0,0,0,0,0,0,0,0])),(0,1,0,'midnight/elephant ', array([0,0,0,0,0,0,1,0,0,0,0,0])),(0,0,1,'relic ', array([0,0,0,0,0,0,0,1,0,0,0,0]))])]
#just nightmares
possibilitiesFill = [tuple([sum2(i) for i in zip(*j)]) for j in itertools.product([(0,1,0,'no_wings N/A ', array([0,0,0,0,0,0,0,0,0,0,0,0])),(1,2,1,'wings N/A ', array([1,0,0,0,0,0,0,0,0,0,0,0]))],
                                                                                  [(0,1,0,'sporing ', array([0,0,0,0,0,0,0,0,0,0,0,0]))],
                                                                                  [(0,0,0,'nothing ', array([0,0,0,0,0,0,0,0,0,0,0,0])),(0,1,0,'reptile ', array([0,0,0,0,0,0,0,0,0,1,0,0]))],
                                                                                  [(0,0,0,'nothing ', array([0,0,0,0,0,0,0,0,0,0,0,0])),(0,2,0,'law-glass ', array([0,1,0,0,0,0,0,0,0,0,0,0])),(1,1,0,'vakeclaw ', array([0,0,1,0,0,0,0,0,0,0,0,0]))],
                                                                                  [(0,0,0,'nothing ', array([0,0,0,0,0,0,0,0,0,0,0,0])),(0,1,0,'chess_set ', array([0,0,0,0,0,0,0,0,0,0,0,1]))],
                                                                                  [(0,0,2,'woesel ', array([0,0,0,0,0,0,0,0,0,0,0,0]))],
                                                                                  [(0,0,0,'nothing ', array([0,0,0,0,0,0,0,0,0,0,0,0])),(0,1,0,'midnight/elephant ', array([0,0,0,0,0,0,1,0,0,0,0,0]))])]

MissiveCombos = []

print('\r\nDiscordant missive')
for iVals, iGroup in itertools.groupby(sorted([(i[0],i[3],i[4]) for i in possibilitiesSend]), lambda x: x[0]):
    for jVals, jGroup in itertools.groupby(sorted([(i[1],i[2],i[3],i[4]) for i in possibilitiesRead]), lambda x: (x[0],x[1])):
        for kVals, kGroup in itertools.groupby(sorted([(i[1],i[3],i[4]) for i in possibilitiesFill]), lambda x: x[0]):
            iGroup = list(iGroup)
            jGroup = list(jGroup)
            kGroup = list(kGroup)
            if set([iFit[1][0][0] for iFit in iGroup]) & set([jFit[2][0][0] for jFit in jGroup]) & set([kFit[1][0][0] for kFit in kGroup]) != set([]):
                SoHPerAction=missive(jVals[0],iVals,jVals[1],kVals)
                for iFit in iGroup:
                    for jFit in jGroup:
                        for kFit in kGroup:
                            if iFit[1][0][0]==jFit[2][0][0] and jFit[2][0][0]==kFit[1][0][0]:
                                #print(''.join(iFit[1])+''.join(jFit[2])+'suspicion '+str(iVals)+' nightmares '+str(jVals[0])+' wounds '+str(jVals[1])+' fillnightmares '+str(kVals)+' '+str(SoHPerAction))
                                MissiveCombos.append([numpy.logical_or(iFit[2],numpy.logical_or(jFit[3],kFit[2])),iVals,jVals[0],jVals[1],kVals,SoHPerAction])

optimalFitsMissive=[]
correspondenceMissive=[]

for i in itertools.product([0,1],repeat=12):
    constraint=list(i)
    bestFit = max([j[1:] for j in MissiveCombos if array(constraint).dominates(j[0])],key=lambda x:x[-1])
    if not bestFit in optimalFitsMissive:
        optimalFitsMissive.append(bestFit)
        correspondenceMissive.append([''.join([str(j) for j in constraint]),len(optimalFitsMissive)-1])
    else:
        correspondenceMissive.append([''.join([str(j) for j in constraint]),optimalFitsMissive.index(bestFit)+1])

print('\r\n\r\nCorrespondences - Missive')
print('{'+', '.join(['["'+i[0]+'"]='+str(i[1]) for i in correspondenceMissive])+'}')
print('\r\n\r\nOutfit details')
print('{{'+'}, {'.join([','.join([str(round(i[4],2)),str(i[0]),str(i[1]),str(i[2]),str(i[3])]) for i in optimalFitsMissive])+'}}')
