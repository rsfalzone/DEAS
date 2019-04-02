import pandas as pd
from gurobipy import *
from DEASmodel import DEASModel

def linExpr2Str(linExpr):
    string = ""
    for i in range(linExpr.size()):
        if i > 0:
            if linExpr.getCoeff(i) > 0:
                string += " + "
            elif linExpr.getCoeff(i) < 0:
                string += " - "
        if abs(linExpr.getCoeff(i)) > 0:
            string += "*".join([str(abs(linExpr.getCoeff(i))), linExpr.getVar(i).VarName])
    if linExpr.getConstant() >= 0:
        string += " + " + str(abs(linExpr.getConstant()))
    else:
        string += " - " + str(abs(linExpr.getConstant()))
    try:
        string += " = " + str(linExpr.getValue())
    except:
        pass
    return string

def main():
    deas_xl = "DEAS_Equipment.xlsx"
    priority_list = ["CHAIRS", "TABLES"]

    # deas_xl = "EquipmentInventory.xlsx"
    # deas_xl = "EquipmentInventoryTest2.xlsx"

    # priority_list = ["8 X 30 TABLES", "6 X 30 TABLES", "8 X 18 TABLES", "6 X 18 TABLES", "66 ROUND TABLES", "HIGH BOYS", "30 COCKTAIL ROUNDS",
    #     "MEETING ROOM CHAIRS", "PODIUMS", "STAGE SKIRT DOLLIES", "TABLE SKIRT DOLLIES", "MEETING ROOM CHAIR DOLLIES",
    #     "66 ROUND TABLE DOLLIES", "FOLDING CHAIR DOLLIES (V STACK)", "FOLDING CHAIR DOLLIES (SQUARE STACK)", "HIGH BOY DOLLIES",
    #     "LONG TABLE DOLLIES", "SHORT TABLE DOLLIES", "STAND UP TABLE DOLLIES", "16RISERS 6 X 8", "24RISERS 6 X 8", "32RISERS 6 X 8", "(3) STEP UNIT WITH RAIL",
    #     "(3) STEP UNIT WITHOUT RAIL", "(2) STEP UNIT WITH RAIL", "(2) STEP UNIT WITHOUT RAIL","SETS OF STAGE STEPS", "16RISERS 6 X 8", "24RISERS 6 X 8", "30 STAND-UP ROUNDS"]

## NOT NEEDED AFTER TRANSFOR IS UPDATED
    xl_data = pd.read_excel(deas_xl,
        sheet_name=["Commodities", "Storage Rooms", "Movement Arcs", "Storage Room Arcs", "Event Room Arcs", "Utility Arcs"])

    xl = pd.ExcelFile(deas_xl)
    xl_data["Cost Data"] = xl.parse("Cost Data", header=None)
    rows = xl_data["Cost Data"].values.tolist()
    cost_dict = {}
    for rowIndex in range (1, len(rows)):
        for columnIndex in range (1, (rowIndex + 1)):
            cost_dict[(rows[rowIndex][0], rows[0][columnIndex])] = rows[rowIndex][columnIndex]
            cost_dict[(rows[0][columnIndex], rows[rowIndex][0])] = rows[rowIndex][columnIndex]



###############################################################################
# Gurobi Model
#
###############################################################################
# Adding Variables

    m = Model("m")
    m.setParam( 'OutputFlag', False )


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

###############################################################################
    time_echelons = sorted(time_echelons)
    rooms = e_rooms + s_rooms
    capped_nodes = [(s, t, "b") for s in s_rooms for t in time_echelons[1:-1]]

    s_room_caps = {}
    for row in xl_data["Storage Rooms"].values.tolist():
        s_room_caps[row[0]] = row[3]

    commodity_vols = {}
    for row in xl_data["Commodities"].values.tolist():
        commodity_vols[row[0]] = row[2]
    for c in [x for x in commodity_vols]:
        if c not in commodities:
            del commodity_vols[c]

###############################################################################
# Flow Balance Constraints

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
    m.write("model.lp")

##############################################################################
# Lagrangian Penalty

    cap_constrs = {}
    for s in capped_nodes:
        used_vol_s = LinExpr()
        for commodity in commodity_vols: ## NOT NEEDED?
            for arc in arc_vars["Storage Room Arcs"]:
                tail, head, com = arc
                if head == s and com == commodity:
                    used_vol_s.add(arc_vars["Storage Room Arcs"][arc], commodity_vols[com])
        used_vol_s.add(-s_room_caps[s[0]])
        cap_constrs[s] = used_vol_s

    m.write("model.lp")

    lr = DEASModel(m, iterations=10, relaxedConstrs=cap_constrs)
    output = lr.subgradientAscent()
    print(output)
#
# Gurobi Model
###############################################################################
## PRINTS INFO RELATED TO THE FINAL STATE OF MODEL (no greedy Swap)
    # if m.status == GRB.Status.OPTIMAL:
    #     print()
    #     print("GUROBI MODEL OUTPUT:")
    #     print('Penalized Objective Value: %g' % m.objVal)
    #     print("Real Objective Value: %g" % unrelaxed_obj.getValue())
    #     print("Iterations of Subgradient Ascent: {}".format(iterations))
    #     print("Movement Arcs:")
    #     for var in arc_vars["Movement Arcs"]:
    #         if arc_vars["Movement Arcs"][var].X > 0:
    #             print("{:<60s}| {:>8.0f}".format(str(var), arc_vars["Movement Arcs"][var].X))
    #     print("\nStorage Room Arcs:")
    #     for var in arc_vars["Storage Room Arcs"]:
    #         if arc_vars["Storage Room Arcs"][var].X > 0:
    #             print("{:<60s}| {:>8.0f}".format(str(var), arc_vars["Storage Room Arcs"][var].X))
    #     print('\nAx-b:')
    #     for s in cap_constrs:
    #         print(str(s) + ": " + str(cap_constrs[s].getValue()))
    # else:
    #     print('No solution;', m.status)
## PRINTS INFO RELATED TO THE FINAL STATE OF MODEL (no greedy Swap)

    print("\a")

if __name__ == "__main__":
    main()