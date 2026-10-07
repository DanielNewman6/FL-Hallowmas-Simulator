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

def array(in_list):
    return my_array((4,), buffer=numpy.array(in_list),offset=0,dtype=numpy.int_)

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

def pavilion(items,absinthe=True):
    if absinthe:
        actionPDF = pdf([(5,Fraction('0.33')),(1,Fraction('0.33')),(7,Fraction('0.34'))]).menaceBonus(items)
    else:
        actionPDF = pdf([(5,Fraction('0.33')),(1,Fraction(67*10,100*13)),(7,Fraction(67*3,100*13))]).menaceBonus(items)
    masqueradeSpace = [actionPDF]
    while masqueradeSpace[-1].atMost(27) > Fraction(1,1000000000):
        masqueradeSpace.append(masqueradeSpace[-1]+actionPDF)
    endings = [1-j.atMost(27) for j in masqueradeSpace]
    avgLength = 0
    for i in range(1,len(endings)):
        avgLength += (i+1)*(endings[i]-endings[i-1])
    avgLength += 1*endings[0]
    return [round(float(28/(avgLength+3)),3), round(float(avgLength+2),3)]

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

'''
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
for j in [True, False]:
    for i in sorted(list(set([i[2] for i in possibilitiesMask]))):
        print('items '+str(i)+' absinthe '+str(j)+' '+str(pavilion(i,absinthe=j)))

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

def sum2(iterable):
    if isinstance(iterable[0], str): return iterable
    else: return sum(iterable)

#just nightmares+wounds
possibilitiesHunger = [tuple([sum2(i) for i in zip(*j)]) for j in itertools.product([(0,1,0,'no_wings no_diminished '),(1,2,1,'wings no_diminished '),(0,1,1,'no_wings diminished '),(1,2,2,'wings diminished ')],
                                                                                    [(0,1,0,'sporing ')],
                                                                                    [(0,0,0,'N/A ')],
                                                                                    [(0,0,0,'nothing '),(0,1,0,'reptile '), (0,0,1,'guiltgift ')],
                                                                                    [(0,0,0,'nothing '),(0,2,0,'law-glass '),(0,1,0,'vakeclaw '),(0,0,1,'mark/liturgy ')],
                                                                                    [(0,0,0,'N/A ')],
                                                                                    [(0,1,0,'albatross '),(0,0,2,'woesel ')],
                                                                                    [(0,0,0,'nothing '),(1,0,0,'rantipoles ')],
                                                                                    [(0,0,0,'nothing '),(0,1,0,'midnight/elephant '),(0,0,1,'relic ')],
                                                                                    [(0,0,0,'nothing '),(0,1,0,'chess_set ')])]
#just nightmares+scandal
possibilitiesHungerDuchess = [tuple([sum2(i) for i in zip(*j)]) for j in itertools.product([(0,1,0,'no_wings N/A '),(1,2,1,'wings N/A ')],
                                                                                           [(1,0,0,'modish '),(0,1,0,'sporing ')],
                                                                                           [(1,0,0,'barrel ')],
                                                                                           [(1,0,0,'necktie '), (0,1,0,'reptile ')],
                                                                                           [(1,0,0,'census '),(0,2,0,'law-glass '),(0,1,0,'vakeclaw ')],
                                                                                           [(1,0,0,'stockings ')],
                                                                                           [(0,0,2,'woesel ')],
                                                                                           [(0,0,0,'nothing '),(1,0,0,'rantipoles ')],
                                                                                           [(0,0,0,'nothing '),(1,0,0,'newt '),(0,1,0,'midnight/elephant ')],
                                                                                           [(0,0,0,'nothing '),(0,1,0,'chess_set ')])]
#just nightmares
possibilitiesHungerUnderclay = [tuple([sum2(i) for i in zip(*j)]) for j in itertools.product([(0,1,0,'no_wings N/A '),(1,2,1,'wings N/A ')],
                                                                                             [(0,1,0,'sporing ')],
                                                                                             [(0,0,0,'N/A ')],
                                                                                             [(0,0,0,'N/A ')],
                                                                                             [(0,0,0,'nothing '),(0,2,0,'law-glass '),(0,1,0,'vakeclaw ')],
                                                                                             [(0,0,0,'N/A ')],
                                                                                             [(0,0,2,'woesel ')],
                                                                                             [(0,0,0,'N/A ')],
                                                                                             [(0,0,0,'nothing '),(0,1,0,'midnight/elephant ')],
                                                                                             [(0,0,0,'nothing '),(0,1,0,'chess_set ')])]

print('\r\nSo hungry - Duchess')
for iVals, iGroup in itertools.groupby(sorted([(i[1],i[2],i[3]) for i in possibilitiesHunger]), lambda x: (x[0],x[1])):
    for jVals, jGroup in itertools.groupby(sorted([(i[1],i[0],i[3]) for i in possibilitiesHungerDuchess]), lambda x: (x[0],x[1])):
        SoHPerAction=hungry(iVals[0],iVals[1],jVals[0],jVals[1],method='Duchess')[0]
        iGroup=list(iGroup)
        jGroup=list(jGroup)
        for iFit in iGroup:
            for jFit in jGroup:
                if iFit[2][0]==jFit[2][0]: print(''.join(iFit[2])+''.join(jFit[2])+' nightmares '+str(iVals[0])+' wounds '+str(iVals[1])+' fill nightmares '+str(jVals[0])+' fill scandal '+str(jVals[1])+' Duchess '+str(SoHPerAction))

print('\r\nSo hungry - Console')
for iVals, iGroup in itertools.groupby(sorted([(i[1],i[2],i[3]) for i in possibilitiesHunger]), lambda x: (x[0],x[1])):
    for jVals, jGroup in itertools.groupby(sorted([(i[1],i[0],i[3]) for i in possibilitiesHungerUnderclay]), lambda x: (x[0],x[1])):
        SoHPerAction=hungry(iVals[0],iVals[1],jVals[0],0,method='Underclay')[0]
        iGroup=list(iGroup)
        jGroup=list(jGroup)
        for iFit in iGroup:
            for jFit in jGroup:
                if iFit[2][0]==jFit[2][0]: print(''.join(iFit[2])+''.join(jFit[2])+' nightmares '+str(iVals[0])+' wounds '+str(iVals[1])+' fill nightmares '+str(jVals[0])+' fill scandal '+str(jVals[1])+' Underclay '+str(SoHPerAction))


#(suspicion, nightmares, wounds, name)
#burdens: [(0,1,0,'no_wings no_diminished '),(1,2,1,'wings no_diminished '),(2,1,1,'no_wings diminished '),(3,2,2,'wings diminished ')]
#hats: [(0,1,0,'sporing '), (1,0,0,'pirate ')]
#adornments: [(0,1,0,'reptile '), (0,0,1,'guiltgift ')]
#weapon: [(0,2,0,'law-glass '),(1,1,0,'vakeclaw '),(0,0,1,'mark/liturgy ')]
#luggage: [(1,0,0,'six-by-two '),(0,1,0,'chess_set ')]
#companion: [(0,1,0,'albatross '),(0,0,2,'woesel '),(1,0,0,'polymath ')]
#homeComfort: [(0,0,0,'nothing '),(0,1,0,'midnight/elephant '),(0,0,1,'relic ')]

#just suspicion
possibilitiesSend = [tuple([sum2(i) for i in zip(*j)]) for j in itertools.product([(0,1,0,'no_wings no_diminished '),(1,2,1,'wings no_diminished '),(2,1,1,'no_wings diminished '),(3,2,2,'wings diminished ')],
                                                                                  [(1,0,0,'pirate ')],
                                                                                  [(0,0,0,'nothing '),(1,1,0,'vakeclaw ')],
                                                                                  [(0,0,0,'nothing '),(1,0,0,'six-by-two ')],
                                                                                  [(0,0,0,'nothing '),(1,0,0,'polymath ')])]
#just wounds+nightmares
possibilitiesRead = [tuple([sum2(i) for i in zip(*j)]) for j in itertools.product([(0,1,0,'no_wings no_diminished '),(1,2,1,'wings no_diminished '),(2,1,1,'no_wings diminished '),(3,2,2,'wings diminished ')],
                                                                                  [(0,1,0,'sporing ')],
                                                                                  [(0,0,0,'nothing '),(0,1,0,'reptile '),(0,0,1,'guiltgift ')]
                                                                                  [(0,0,0,'nothing '),(0,2,0,'law-glass '),(1,1,0,'vakeclaw '),(0,0,1,'mark/liturgy ')],
                                                                                  [(0,1,0,'albatross '),(0,0,2,'woesel ')],
                                                                                  [(0,0,0,'nothing '),(0,1,0,'midnight/elephant '),(0,0,1,'relic ')])]
#just nightmares
possibilitiesFill = [tuple([sum2(i) for i in zip(*j)]) for j in itertools.product([(0,1,0,'no_wings N/A '),(1,2,1,'wings N/A ')],
                                                                                  [(0,1,0,'sporing ')],
                                                                                  [(0,0,0,'nothing '),(0,1,0,'reptile ')],
                                                                                  [(0,0,0,'nothing '),(0,2,0,'law-glass '),(1,1,0,'vakeclaw ')],
                                                                                  [(0,0,0,'nothing '),(0,1,0,'chess_set ')],
                                                                                  [(0,0,2,'woesel ')],
                                                                                  [(0,0,0,'nothing '),(0,1,0,'midnight/elephant ')])]

print('\r\nDiscordant missive')
for iVals, iGroup in itertools.groupby(sorted([(i[0],i[3]) for i in possibilitiesSend]), lambda x: x[0]):
    #print(iVals)
    for jVals, jGroup in itertools.groupby(sorted([(i[1],i[2],i[3]) for i in possibilitiesRead]), lambda x: (x[0],x[1])):
        #print(jVals)
        for kVals, kGroup in itertools.groupby(sorted([(i[1],i[3]) for i in possibilitiesFill]), lambda x: x[0]):
            #print(kVals)
            SoHPerAction=missive(jVals[0],iVals,jVals[1],kVals)
            iGroup = list(iGroup)
            jGroup = list(jGroup)
            kGroup = list(kGroup)
            for iFit in iGroup:
                #print(iFit)
                for jFit in jGroup:
                    #print(jFit)
                    for kFit in kGroup:
                        #print(kFit)
                        if iFit[1][0]==jFit[2][0] and jFit[2][0]==kFit[1][0]: print(''.join(iFit[1])+''.join(jFit[2])+'suspicion '+str(iVals)+' nightmares '+str(jVals[0])+' wounds '+str(jVals[1])+' fillnightmares '+str(kVals)+' '+str(SoHPerAction))
