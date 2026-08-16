import gurobipy as gp

detections = gp.Model("NEO Detections")

telescope = ["AU1","CL1", "SA1", "AU2", "CL2", "HI1"]
belts = ["Main", "NEO"]
days = ["Mon", "Tues", "Wed", "Thur", "Fri", "Sat", "Sun"]

T = range(len(telescope))
B = range(len(belts))
D = range(7)

e = [.99, .97, .99, .40, .43, .36]
n = [3.3, 3.8, 3.9, 3.4, 3.6, 3.8, 4.7]
h = [4.8, 5.5, 6.4, 4.7, 5.3, 5.4, 6.0]
r = [2.2, 3.4]
p = 500
c = 25

X = [{} for t in T]
Y = [{} for t in T]

processed = [{} for d in D]
stored = [{} for d in D]

    
for d in D:
    #comms 2 turned Y into matrix
    stored[d] = detections.addVar()
    processed[d] = detections.addVar()
    for t in T:
        X[t][d] = detections.addVar()
        Y[t][d] = detections.addVar()



# Objective
#detections.setObjective(gp.quicksum(gp.quicksum(e[t]*((r[1] * X[d]) + (r[0] * (Y[d] - X[d]))) for d in D) for t in T), gp.GRB.MAXIMIZE)

# detections.setObjective(gp.quicksum(gp.quicksum(e[t]*(r[1] * (X[t][d] + spare[t][d][0])) + e[t]*(r[0] * (Y[t][d] + spare[t][d][1])) for d in D) for t in T), gp.GRB.MAXIMIZE)
detections.setObjective(gp.quicksum(gp.quicksum(e[t]*(r[1] * (X[t][d])) + e[t]*(r[0] * (Y[t][d])) for d in D) for t in T), gp.GRB.MAXIMIZE)


#comm 1 constraints
# for d in D:
#     for t in T:
#         detections.addConstr(X[t][d] <= n[d])
#         detections.addConstr(Y[t][d] <= h[d] - X[t][d])

for d in D:
    p = 0
    for t in T:
        detections.addConstr(X[t][d] <= n[d])
        detections.addConstr(X[t][d] >= 0)
        # detections.addConstr(X[t][d] + Y[t][d] <= h[d])
        #comms 2 added Y matrix and constraints for each telescope
        if t == 2 or t == 4:
            # p += Y[t][d] #+ spare[t][d][1]
            detections.addConstr(Y[t][d] <= h[d])
            #Dont forget this specification (was added in comms 3)
            detections.addConstr(Y[t][d] >= X[t][d])
            # detections.addConstr(Y[t][d] + X[t][d] <= 2*h[d])
        else:
            # p += X[t][d] + Y[t][d]# + spare[t][d][0] + spare[t][d][1]
            detections.addConstr(Y[t][d] <= (h[d] - X[t][d]))
        detections.addConstr(Y[t][d] >= 0)

    
#Comms 4
for t in T:
    # detections.addConstr(gp.quicksum(X[t][d] + Y[t][d] + spare[t][d + 1][0] + spare[t][d + 1][1] for d in D) >= 10)
    detections.addConstr(gp.quicksum(X[t][d] + Y[t][d] for d in D) >= 10)


for d in D:
    observed = 0
    for t in T:
        if t == 2 or t == 4:
            observed += Y[t][d]
        else:
            observed += X[t][d] + Y[t][d]

    #comms 3
    # detections.addConstr(processed[d] == observed)
    # detections.addConstr(processed[d] <= 20)

    #comms 5
    detections.addConstr(stored[d] == observed - processed[d])

    detections.addConstr(stored[d] <= observed)
    detections.addConstr(stored[d] <= 20)
    detections.addConstr(stored[d] >= 0)

    if d > 0:
        detections.addConstr(processed[d] + stored[d-1] <= 20)
    else:
        detections.addConstr(processed[d] <= 20)



detections.optimize()

print(detections.ObjVal)

for t in T:
    print(telescope[t])
    for d in D:
        print("Day:", d, "NEO Y:", X[t][d].x, "Main Y:", round(Y[t][d].x,2))
        
# for d in D:
#     print("Day:", d)
#     total_time = 0
#     for t in T:
#         if t == 2 or t == 4:
#             total_time += Y[t][d].x
#             if d > 0:
#                 total_time += spare[t][d][1].x
#         else:
#             total_time += X[t][d].x + Y[t][d].x
#             if d > 0:
#                 total_time += spare[t][d][0].x + spare[t][d][1].x
#     print("Total Y:", total_time)

# print()
# # for d in D:
# #     # if d > 0:
# #         spare_sum = 0
# #         proc_time = 0
# #         for t in T:
# #             proc_time += X[t][d].x + Y[t][d].x + spare[t][d][0].x + spare[t][d][1].x
# #             for b in B:
# #                 spare_sum += spare[t][d][b].x
# #         cond1 = spare_sum <= 20 #spare store < 500gb a day
# #         cond2 = proc_time <= 20 #processed < 500 gb a day
# #         if not cond1 or not cond2:
# #                 print("ERROR ", d, cond1, cond2)

# # print("Total Detections:", detections.ObjVal)

# # for d in D:
# #     if d > 0:
# #         for t in T:
# #             cond3 = spare[t][d][0].x + X[t][d-1].x < n[d-1] #what is spare is not included in previous day
# #             cond4 = spare[t][d][1].x + Y[t][d-1].x < h[d-1]#what is spare is not included in previous day
# #             if not cond3 or not cond4:
# #                 print("ERROR ", t, d)


# for d in D:
#     if d > 0:
#         for t in T:
#             print(telescope[t])
#             print(d, t, b, '(', spare[t][d][0].x, ',', spare[t][d][1].x, ')')
#         print()
            






