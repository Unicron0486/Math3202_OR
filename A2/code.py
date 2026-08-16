from math import floor

import gurobipy as gp
import Ancestral2 as dta

Tasks = dta.Tasks
Days = dta.Days
Skills = dta.Skills

J = dta.J
I = dta.I
D = dta.T
S = dta.S

e = dta.Staff
k = [Tasks[j]['skill'] for j in J]
t = [Tasks[j]['duration'] for j in J]
p = [Tasks[j]['staff'] for j in J]
a = [Tasks[j]['title'] for j in J]
M = 36
Md = 10
b = 7

m = gp.Model()

# Variables
# bin var of who works on what
X = {(j,i): m.addVar(vtype=gp.GRB.BINARY) for j in J for i in I}

# Binary var if staff member i has a day off on day d
W = {(i,d): m.addVar(vtype=gp.GRB.BINARY) for i in I for d in D}

# Bin var if they had training to improve skill s
Y = {(i,s): m.addVar(vtype=gp.GRB.BINARY) for i in I for s in S}

# Tracker for hours worked by staff member i
T = [{} for i in I]
for i in I:
    T[i] = gp.quicksum(X[j,i] * t[j] for j in J)

# Track skill level used for job j
L = [{} for j in J]
for j in J:
    # L[j] = gp.quicksum(X[j,i] * Staff[i][k[j]] + (Y[i,k[j]] * b) for i in I)
    L[j] = gp.quicksum(X[j,i] * e[i][k[j]] for i in I)

# Tracks hours worked each day
H = {(i,d): 0 for i in I for d in D}
for i in I:
    for d in D:
        H[i,d] = gp.quicksum(X[j,i] * t[j] for j in J if Tasks[j]['day'] == d)

night_ops = [j for j in J if Tasks[j]['title'] == 'Nightly telescope operation']

m.setObjective(gp.quicksum(L[j] for j in J), gp.GRB.MAXIMIZE)
    
# Comm 6
for j in J:
    # No. staff required for tasks is met
    m.addConstr(gp.quicksum(X[j,i] for i in I) == p[j])
    # non zero constraint
    m.addConstr(L[j] >= 0)

for i in I:
    # work hours is <= 36 per staff and no less than zero
    m.addConstr(T[i] <= M)
    m.addConstr(T[i] >= 0)
 
# Comm 7
for j in J:
    # logic and
    m.addConstr(X[j,3] + X[j,8] <= 1)
    m.addConstr(X[j,6] + X[j,7] <= 1)
    m.addConstr(X[j,3] + X[j,12] <= 1)
    m.addConstr(X[j,10] + X[j,8] <= 1)

# Comm 8
for d in D: 
    for i in I:
    # work hours is <= 10 per day
        m.addConstr(H[i,d] <= Md * W[i, d])

for i in I:
    #technicians have at least 2 days off
    m.addConstr(gp.quicksum(W[i,d] for d in D) <= 5)

# Comm 9
# if doing nightime op, do not work that day.
for d in D:
    for i in I:
        for n in night_ops:
            for j in J:
                if Tasks[j]['day'] == Tasks[n]['day'] and j != n:
                    m.addConstr(X[j,i] + X[n,i] <= 1)

# Comm 10
m.addConstr(gp.quicksum(gp.quicksum(Y[i, s] for s in S) for i in I) == 5)
for i in I:
    m.addConstr(gp.quicksum(Y[i, s] for s in S) <= 1)

m.optimize()

#printing
print("Optimal skill score: ", m.objVal)

#######
# Used to print the rosters
#######

# for d in D:
#     count = 0
#     print(Days[d])
#     for j in J:
#         if Tasks[j]['day'] == d:
#             count += 1
#             xs = [i for i in I if X[j, i].x == 1]
#             print(Tasks[j]['title'], "has technicians ", xs)
#     print(count)
#     print("\n")





######
# Can ignore - were used to chack conditions
######

# for i in I:
#     for s in S:
#         if Y[i, s].x:
#             print("Worker ", i, "skill ", s, "is ", Y[i, s].x)
# for i in I:
#     for d in D:
#         print(i, d, W[i,d])

# for i in I:
#     for d in D:
#         print("Staff member ", i, " works on day ", d, " for ", H[i,d].getValue(), " hours", W[i,d].x, " hours on")
# for i in I:
#     for d in D:
#         print("Staff member ", i, " works on day ", d, " for ", H[i,d].getValue(), " hours")
# for i in I:
#     print("Staff member ", i, " works on:")
#     for j in J:
#         if X[j,i].x > 0.5:
#             print("  - ", Tasks[j]['title'], " (", t[j], " hours, skill score: ", Staff[i][k[j]], ")")
#     print("Total hours: ", T[i].getValue())
# total = 0
# N = [0 for j in J]
# for j in J:
#     for i in I:
#         if X[j][i]:
#             N[j] += 1
#     total += L[j]
#     print(Tasks[j]['title'], ":", L[j], ",", N[j])
# # print("Total skill score: ", total)

# for i in I:
#     print(i, T[i])