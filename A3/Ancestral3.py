from itertools import combinations
from itertools import permutations
S = range(9)
P = range(20)

# The state is a 9-tuple where each element is
# -1 = lost, 0 = fragile, 1 = restored
# GenerateOutcomes returns a list of tuples with a probability
# in position 0 and a state as a tuple in position 1
def GenerateOutcomes(State, LossProb):
    ans = []
    tempSites = [j for j in S if State[j]==0]
    n = len(tempSites)
    for i in range(n+1):
        for tlist in combinations(tempSites, i):
            p = 1.0
            slist = list(State)
            for j in range(n):
                if tempSites[j] in tlist:
                    p *= LossProb[tempSites[j]]
                    slist[tempSites[j]] = -1
                else:
                    p *= 1-LossProb[tempSites[j]]
            ans.append((p, tuple(slist)))
    return ans

# example
outcomes = GenerateOutcomes((1,0,0,-1,-1,0,1,1,-1), [0.2 for j in S])


# Data
L = [
	[2, 3],
	[4],
	[2, 16],
	[4, 12, 14, 19],
	[0, 9, 10, 11],
	[1],
	[6, 13, 17, 18],
	[5, 15, 19],
	[1, 6, 7, 8, 13]
]

N = [
    [3],
    [5],
    [3, 7],
    [0, 2, 4, 8],
    [3, 5],
    [1, 4],
    [7],
    [2, 6, 8],
    [3, 7]
]

initial_state = (0, 0, 0, 0, 0, 0, 0, 0, 0)
schedual = [8, 6, 4, 3, 7, 2, 0, 5, 1]

_outcomes = {}

def count_species(x):
    saved_species = [0 for i in P]
    for i in S:
        if x[i] == 1:
            for species in L[i]:
                saved_species[species] = 1
    return saved_species


#comm 12
def Ex(x) :
    fragile = [i for i in S if x[i] == 0]
    if fragile == []:
            result = count_species(x)
            return result

    else:
        sched = [i for i in schedual if i in fragile]
        x = list(x)
        x[sched[0]] = 1
        
        x = tuple(x)

        if x not in _outcomes:
            _outcomes[x] = GenerateOutcomes(x, [0.2 for j in S])
        outcomes = _outcomes[x]
        
        expected_species = [0 for i in P]

        for prob, state in outcomes:
            next = Ex(state)
            for species in P:
                expected_species[species] += prob * next[species]

        return expected_species

print("Com 12 solution")

new_sched = Ex(initial_state)
print(sum(new_sched))
for i in P:
    new_sched[i] = round(new_sched[i], 2)
print(new_sched)

#comm 13
_Ex = {}
def com13(x):
    
    if x in _Ex:
        return _Ex[x]
    
    fragile = [i for i in S if x[i] == 0]
    
    # Base case
    if fragile == []:
        ans = count_species(x)
        _Ex[x] = (ans, [])
        return (ans, [])

    
    # else
    best_sched = []
    expected = [0 for i in P]
    for a in fragile:
        copy_x = list(x)
        copy_x[a] = 1
        copy_x = tuple(copy_x)

        outcomes = GenerateOutcomes(copy_x, [0.2 for j in S])

        best = 0
        full_sched = []
            
        expected_species = [0 for i in P]

        for prob,state in outcomes:
            ex, sch = com13(state)
            best += prob * sum(ex)
            for species in P:
                expected_species[species] += prob * ex[species]

            if full_sched == []:
                full_sched = sch

        if best > sum(expected):
            expected = expected_species
            best_sched = [a] + full_sched

    _Ex[x] = (expected, best_sched)
    return (expected, best_sched)
print("\nCom 13 solution")
new_sched = com13(initial_state)
print(sum(new_sched[0]))
for i in P:
    new_sched[0][i] = round(new_sched[0][i], 2)
print(new_sched)

#comm 14
def probabilities(x):
    prob = [0.2 for j in S]
    idx = 0
    for C in x:
        if C == -1:
            for n in N[idx]:
                prob[n] = prob[n] + 0.05
        idx += 1
    return prob


_Ex2 = {}
def com14(x):
    
    if x in _Ex2:
        return _Ex2[x]
    
    fragile = [i for i in S if x[i] == 0]
    
    # Base case
    if fragile == []:
        ans = count_species(x)
        _Ex2[x] = (ans, [])
        return (ans, [])

    
    # else
    best_sched = []
    expected = [0 for i in P]
    for a in fragile:
        copy_x = list(x)
        copy_x[a] = 1
        copy_x = tuple(copy_x)

        outcomes = GenerateOutcomes(copy_x, probabilities(copy_x))

        best = 0
        full_sched = []

        expected_species = [0 for i in P]

        for prob,state in outcomes:
            ex, sch = com14(state)
            best += prob * sum(ex)
            for species in P:
                expected_species[species] += prob * ex[species]

            if full_sched == []:
                full_sched = sch

        if best > sum(expected):
            expected = expected_species
            best_sched = [a] + full_sched

    _Ex2[x] = (expected, best_sched)
    return (expected, best_sched)

print("\nCom 14 solution")
new_sched = com14(initial_state)
print(sum(new_sched[0]))
for i in P:
    new_sched[0][i] = round(new_sched[0][i], 2)
print(new_sched)

#comm 15
# The community has identified that the four species 0, 8, 16 and 19 are the most culturally important. 
# Instead of maximising the expected number of species we save, 
# what should we do if we wanted to maximise the probability of saving all of these species?

# We want to save sites 4, 8, 2, 7 or 3
# we want to maximise the probability of saving these sites
# first apporach save them first?
# try dynamic though. take max probability of saving the 4 species at each step instead of expected number of species saved.

needed = [0, 8, 16, 19]
def survives(x):
    saved_species = [0 for i in range(20)]
    count = 0
    for i in S:
        if x[i] == 1:
            for species in L[i]:
                    saved_species[species] = 1
    for species in needed:
        if saved_species[species] == 0:
            return False  
    return True


_Pbs = {}
def com15(x):
    if x in _Pbs:
        return _Pbs[x]
    
    fragile = [i for i in S if x[i] == 0]
    
    # Base case
    if fragile == []:
        if survives(x):
            _Pbs[x] = (1, [])
            return (1, [])
        
        _Pbs[x] = (0, [])
        return(0, [])
        
        

    
    # else
    best_sched = []
    best_prob = 0
    for a in fragile:
        copy_x = list(x)
        copy_x[a] = 1
        copy_x = tuple(copy_x)

        outcomes = GenerateOutcomes(copy_x, probabilities(copy_x))

        best = 0
        sched = []
        best_temp = 0

        for y in outcomes:
            prob, sch = com15(y[1])
            
            # 
            best += y[0]*prob

            if prob > best_temp:
                best_temp = prob
                sched = list(sch)

        # skew to favour full scheduals
        best += 0.00000001 * len(sched)

        if best > best_prob:
            best_prob = best
            best_sched = [a] + sched

    _Pbs[x] = (best_prob, best_sched)
    return (best_prob, best_sched)


print("\nCom 15 solution")
new_sched = com15(initial_state)
print(new_sched)
# print(sum(new_sched[0]))

# For client report comaprison purposes
def ExAlt(x) :
    fragile = [i for i in S if x[i] == 0]
    if fragile == []:
            result = count_species(x)
            return result

    else:
        sched = [i for i in schedual if i in fragile]
        x = list(x)
        x[sched[0]] = 1
        
        x = tuple(x)

        if x not in _outcomes:
            _outcomes[x] = GenerateOutcomes(x, probabilities(x))
        outcomes = _outcomes[x]
        
        expected_species = [0 for i in P]

        for prob,state in outcomes:
            next = ExAlt(state)
            for species in P:
                expected_species[species] += prob * next[species]

        return expected_species
    
print("More")
schedual = new_sched[1]
other = ExAlt(initial_state)
print(sum(other))

for i in P:
    other[i] = round(other[i], 2)
print(other)

print("\nOr if using 8 site optimisation")
schedual = [2, 8, 4, 3, 0, 5, 6, 7, 1]
other = ExAlt(initial_state)
print(sum(other))

for i in P:
    other[i] = round(other[i], 2)
print(other)