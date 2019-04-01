import pandas as pd
from gurobipy import *

def main():
    deas_xl = "DEAS_Equipment.xlsx"
    xl_data = pd.read_excel(deas_xl,
        sheet_name=[
        "Commodities", "Storage Rooms", "Cost Data",
        "Movement Arcs", "Storage Room Arcs",
        "Event Room Arcs", "Utility Arcs"
        ])



    m = Model("m")
    arc_vars = {}
    time_echelons = []
    e_rooms = []
    s_rooms = []
    commodities = []
    name_format = "(({}, {}, {}), ({}, {}, {}), {})"
    for arc_sheet in ["Movement Arcs", "Storage Room Arcs", "Event Room Arcs", "Utility Arcs"]:
        time_echelons += [t for t in xl_data[arc_sheet].Yi.unique() if t not in time_echelons]
        time_echelons += [t for t in xl_data[arc_sheet].Yj.unique() if t not in time_echelons]
        e_rooms += [r for r in xl_data[arc_sheet].Xi.unique() if r[0] != "S" and r != "t" and r not in e_rooms]
        s_rooms += [r for r in xl_data[arc_sheet].Xi.unique() if r[0] == "S" and r != "t" and r not in s_rooms]
        e_rooms += [r for r in xl_data[arc_sheet].Xj.unique() if r[0] != "S" and r != "t" and r not in e_rooms]
        s_rooms += [r for r in xl_data[arc_sheet].Xj.unique() if r[0] == "S" and r != "t" and r not in s_rooms]
        commodities += [c for c in xl_data[arc_sheet].Item.unique() if c not in commodities]
        arc_data = xl_data[arc_sheet].values.tolist()
        if len(arc_data) > 1:
            arcs = [((arc[0], arc[1], arc[2]), (arc[3], arc[4], arc[5]), arc[6]) for arc in arc_data]
            lbs = [arc[7] for arc in arc_data]
            ubs = [arc[8] for arc in arc_data]
            costs = [arc[9] for arc in arc_data]
            names = [name_format.format(*arc[0:7]).replace(" ", "_") for arc in arc_data]

            arc_vars[arc_sheet] = m.addVars(arcs, lb=lbs, ub=ubs, obj=costs, name=names)
        else:
            arc = arc_data[0]
            arc_var = m.addVar(lb=arc[7], ub=arc[8], obj=arc[9], name=name_format.format(*arc[0:7]).replace(" ", "_"))
            arc_vars[arc_sheet] = tupledict({((arc[0], arc[1], arc[2]), (arc[3], arc[4], arc[5]), arc[6]):arc_var})
    m.update()

    # print(time_echelons)
    # print(e_rooms)
    # print(s_rooms)
    # print(commodities)
    # time_echelons = [0,1,2]
    # e_rooms = ['C 205', 'C 101', 'C 102', 'C 103', 'C 104', 'C 105', 'C 106', 'C 107', 'C 108', 'C 110', 'C 112', 'C 114', 'C 201', 'C 202', 'C 123', 'C 301', 'C 302', 'GEORGIA BALLROOM', 'C 109', 'C 203', 'C 204', 'C 206', 'C 207', 'C 208', 'C 210', 'C 211']
    # s_rooms = ["S1", "S2", "S3"]
    # rooms = [r_type + r_num for r_type in ["E", "S"] for r_num in ["1", "2"]]
    # e_rooms = ["E" + r_num for r_num in ["1", "2"]]
    # s_rooms = ["S" + r_num for r_num in ["1", "2"]]
    rooms = e_rooms + s_rooms

    s_room_caps = {}
    for row in xl_data["Storage Rooms"].values.tolist():
        s_room_caps[row[0]] = row[1]
    # print(s_room_caps)

    # for s in s_rooms:
    #     if s[1] == "1":
    #         s_room_caps[s] = 50
    #     else:
    #         s_room_caps[s] = 70

    capped_nodes = [(s, t, "b") for s in s_rooms for t in time_echelons[1:-1]]




    # commodities1 = ["CHAIRS", "TABLES"]
    # commodity_vols = {"CHAIRS": 1, "TABLES": 4}



    commodity_vols = {}
    for row in xl_data["Commodities"].values.tolist():
        commodity_vols[row[0]] = row[2]
    # commodities = ['8 X 30 TABLES', '6 X 30 TABLES', '8 X 18 TABLES', '6 X 18 TABLES', '66 ROUND TABLES', '30 COCKTAIL ROUNDS', 'MEETING ROOM CHAIRS', 'PODIUMS', '16RISERS 6 X 8', '24RISERS 6 X 8', 'SETS OF STAGE STEPS', '30 STAND-UP ROUNDS']
    # for x in commodities:
    #     commodity_vols[x] = 1

    for c in [x for x in commodity_vols]:
        if c not in commodities:
            del commodity_vols[c]

    fb_nodes = [(r, t, d) for r in rooms for t in time_echelons[:-1] for d in ["a", "b"] if not (t == 0 and d == "a")]
    fb_nodes += [("t", time_echelons[-1], "a")]
    nodes = fb_nodes + [("s", 0, "a")] + [("t", time_echelons[-1],"b")]



    for node in fb_nodes:
        for commodity in commodity_vols:
            LHS = LinExpr()
            RHS = LinExpr()
            for arc_type in arc_vars:
                for tail, head, com in arc_vars[arc_type]:
                    if com == commodity:
                        if head == node:
                            LHS.add(arc_vars[arc_type][(tail, head, com)])
                        elif tail == node:
                            RHS.add(arc_vars[arc_type][(tail, head, com)])
            m.addConstr(LHS, sense=GRB.EQUAL, rhs=RHS, name=str((node, commodity)).replace(" ", "_"))
    m.update()

    unrelaxed_obj = m.getObjective()


    cap_constrs = {}
    lagrange_mults = {}
    for s in capped_nodes:
        used_vol_s = LinExpr()
        for commodity in commodity_vols: ## NOT NEEDED?
            for arc in arc_vars["Storage Room Arcs"]:
                tail, head, com = arc
                if head == s and com == commodity:
                    used_vol_s.add(arc_vars["Storage Room Arcs"][arc], commodity_vols[com])
        used_vol_s.add(-s_room_caps[s[0]])
        cap_constrs[s] = used_vol_s
        lagrange_mults[s] = 0


    objective = LinExpr()
    penalty = LinExpr()
    for s in cap_constrs:
        penalty.add(cap_constrs[s], lagrange_mults[s])
    objective.add(unrelaxed_obj)
    objective.add(penalty)
    m.setObjective(objective, GRB.MINIMIZE)

    m.write("model.lp")





    i = 1
    print("\nIteration: {}".format(i))
    print("lagrange_mults")
    print(lagrange_mults)
    print()
    m.optimize()

    movement_arcs = {}
    for x in arc_vars["Movement Arcs"]:
        movement_arcs[x] = arc_vars["Movement Arcs"][x].X

    under_cap = {}
    over_cap = {}
    for node in cap_constrs:
        if node[0] != "t":
            axb = cap_constrs[node].getValue()
            if axb < 0:
                if node[1] in under_cap:
                    under_cap[node[1]][(node[0], node[1], "a")] =  axb
                else:
                    under_cap[node[1]] = {(node[0], node[1], "a") :  axb}
            elif axb > 0:
                if node[1] in over_cap:
                    over_cap[node[1]][(node[0], node[1], "a")] =  axb
                else:
                    over_cap[node[1]] = {(node[0], node[1], "a") :  axb}
    print(under_cap)
    print(over_cap)

    print('\nAx-b:')
    for s in cap_constrs:
        print(str(s) + ": " + str(cap_constrs[s].getValue()))

    # iterations = 300
    # while i < iterations:
    #     stepsize = math.sqrt(1/i)
    #     updated_lagrange_mults = {}
    #     opt_check_vector = []
    #     for s in lagrange_mults:
    #         steepest_ascent = cap_constrs[s].getValue()
    #         updated_lagrange_mults[s] = lagrange_mults[s] + max(stepsize * steepest_ascent, 0)
    #         opt_check_vector.append((updated_lagrange_mults[s] - lagrange_mults[s])/i)

    #     sum = 0
    #     for x in opt_check_vector:
    #         sum += x**2
    #     norm = math.sqrt(sum)

    #     print(norm)
    #     print(norm >0 )
    #     if norm > 0 :
    #         lagrange_mults = updated_lagrange_mults
    #         objective = LinExpr()
    #         penalty = LinExpr()
    #         for s in cap_constrs:
    #             penalty.add(cap_constrs[s], lagrange_mults[s])
    #         objective.add(unrelaxed_obj)
    #         objective.add(penalty)
    #         m.setObjective(objective, GRB.MINIMIZE)

    #         i += 1
    #         print("\nIteration: {}".format(i))
    #         print("lagrange_mults")
    #         print(lagrange_mults)
    #         print()
    #         m.optimize()
    #         print("Real Objective Value: %g" % unrelaxed_obj.getValue())
    #         print('\nAx-b:')
    #         for s in cap_constrs:
    #             print(str(s) + ": " + str(cap_constrs[s].getValue()))
    #         print("\nStorage Room Arcs:")
    #         for var in arc_vars["Storage Room Arcs"]:
    #             if arc_vars["Storage Room Arcs"][var].X > 0:
    #                 print("{:<45s}| {:>6.0f}".format(str(var), arc_vars["Storage Room Arcs"][var].X))
    #     else:
    #         i = iterations

    if m.status == GRB.Status.OPTIMAL:
        print('\nPenalized Objective Value: %g' % m.objVal)
        print("Real Objective Value: %g" % unrelaxed_obj.getValue())
        print("Movement Arcs:")
        for var in arc_vars["Movement Arcs"]:
            if arc_vars["Movement Arcs"][var].X > 0:
                print("{:<60s}| {:>8.0f}".format(str(var), arc_vars["Movement Arcs"][var].X))
        print("\nStorage Room Arcs:")
        for var in arc_vars["Storage Room Arcs"]:
            if arc_vars["Storage Room Arcs"][var].X > 0:
                print("{:<60s}| {:>8.0f}".format(str(var), arc_vars["Storage Room Arcs"][var].X))
        print('\nAx-b:')
        for s in cap_constrs:
            print(str(s) + ": " + str(cap_constrs[s].getValue()))
    else:
        print('No solution;', m.status)
    print("\a")

if __name__ == "__main__":
    main()