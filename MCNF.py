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

## PULL FROM EXCEL vv
    time_echelons = [0,1,2,3]

    # rooms = [r_type + r_num for r_type in ["E", "S"] for r_num in ["1", "2"]]
    e_rooms = ["E" + r_num for r_num in ["1", "2"]]
    s_rooms = ["S" + r_num for r_num in ["1", "2"]]
    rooms = e_rooms + s_rooms

    s_room_caps = {}
    for s in s_rooms:
        if s[1] == "1":
            s_room_caps[s] = 50
        else:
            s_room_caps[s] = 70

    capped_nodes = [(s, t, "b") for s in s_rooms for t in time_echelons[1:-1]]

    # commodities1 = ["CHAIRS", "TABLES"]
    commodity_vols = {"CHAIRS": 1, "TABLES": 4}

    fb_nodes = [(r, t, d) for r in rooms for t in time_echelons[:-1] for d in ["a", "b"] if not (t == 0 and d == "a")]
    fb_nodes += [("t", time_echelons[-1], "a")]
    nodes = fb_nodes + [("s", 0, "a")] + [("t", time_echelons[-1],"b")]
## PULL FROM EXCEL ^^

    m = Model("m")
    arc_vars = {}
    name_format = "(({}, {}, {}), ({}, {}, {}), {})"
    for arc_sheet in ["Movement Arcs", "Storage Room Arcs", "Event Room Arcs", "Utility Arcs"]:
        print(arc_sheet)
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

    m.optimize()
    print('\nAx-b:')
    for s in cap_constrs:
        print(str(s) + ": " + str(cap_constrs[s].getValue()))

    if m.status == GRB.Status.OPTIMAL:
        print('\nObjective Value: %g' % m.objVal)
        print("Movement Arcs:")
        for var in arc_vars["Movement Arcs"]:
            if arc_vars["Movement Arcs"][var].X > 0:
                print("{:<45s}| {:>6.0f}".format(str(var), arc_vars["Movement Arcs"][var].X))
        print("\nStorage Room Arcs:")
        for var in arc_vars["Storage Room Arcs"]:
            if arc_vars["Storage Room Arcs"][var].X > 0:
                print("{:<45s}| {:>6.0f}".format(str(var), arc_vars["Storage Room Arcs"][var].X))
    else:
        print('No solution;', m.status)

if __name__ == "__main__":
    main()