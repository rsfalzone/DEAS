import pandas as pd
from gurobipy import *
from LagrangianRelaxation import LagrangianRelaxation
from openpyxl import load_workbook

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


# def greedy_swap(cost_dict, arc_vars, cap_constrs, model_cost, priority_list):
    # print("greedy_swap")
    # original_cost = model_cost

    # movement_arcs_dict = {}
    # for x in arc_vars["Movement Arcs"]:
    #     movement_arcs_dict[x] = arc_vars["Movement Arcs"][x].X

    # under_cap = {}
    # over_cap = {}
    # for node in cap_constrs:
    #     if node[0] != "t":
    #         axb = cap_constrs[node].getValue()
    #         if axb < 0:
    #             if node[1] in under_cap:
    #                 under_cap[node[1]][(node[0], node[1], "a")] =  axb
    #             else:
    #                 under_cap[node[1]] = {(node[0], node[1], "a") :  axb}
    #         elif axb > 0:
    #             if node[1] in over_cap:
    #                 over_cap[node[1]][(node[0], node[1], "a")] =  axb
    #             else:
    #                 over_cap[node[1]] = {(node[0], node[1], "a") :  axb}



    # time_echelons = {} ## TODO: Rename?
    # for time in over_cap:
    #     time_echelons[time] = sorted(over_cap[time], key=lambda k: over_cap[time][k], reverse=True)
    # # print(time_echelons)
    #     # Sort:
    #     #     reverse = True
    #     #       - descending
    #     #     key = lambda (argument : expression)
    #     #       - Iterate over_cap[time].keys() to sort
    #     #            for k in over_cap[time].keys():
    #     #                k -> over_cap[time][k]

    # with open("log_file.txt","w") as f:
    #     f.write("\nINPUT:\n")
    #     f.write("MCNF Cost: "+ str(original_cost)+ "\n")
    #     f.write("Remaining over nodes:\n")
    #     for time in  over_cap:
    #         for over_node in  over_cap[time]:
    #             f.write(": ".join([str(over_node), str(over_cap[time][over_node])])+ "\n")
    #     for time in  over_cap:
    #         for over_node in  over_cap[time]:
    #             for x in movement_arcs_dict:
    #                 if movement_arcs_dict[x] >0:
    #                     if x[1] == over_node:
    #                         f.write(str(x) + ": " + str(movement_arcs_dict[x]) + "\n")

    #     f.write("Starting under nodes:\n")
    #     for time in under_cap:
    #         for under_node in  under_cap[time]:
    #             f.write(": ".join([str(under_node), str(under_cap[time][under_node])])+ "\n")


    #     for time in sorted(list(time_echelons))[:-1]:
    #         for over_node in time_echelons[time]:
    #             # f.write("__________________________________\n")
    #             # f.write("Over Node: " + str(over_node) + "\n")
    #             # f.write("----------------------------------\n")
    #             # print("__________________________________")
    #             # print("Over Node: " + str(over_node))

    #             blue_arc_dict = {}
    #             green_arc_dict = {}
    #             for arc in movement_arcs_dict:
    #                 tail, head, commodity = arc
    #                 if tail == (over_node[0], over_node[1], 'b'):
    #                     if movement_arcs_dict[arc] > 0:
    #                         if commodity in green_arc_dict:
    #                             green_arc_dict[commodity].append(arc)
    #                         else:
    #                             green_arc_dict[commodity] = [arc]
    #                 if head == over_node:
    #                     if movement_arcs_dict[arc] > 0:
    #                         if commodity in blue_arc_dict:
    #                             blue_arc_dict[commodity].append(arc)
    #                         else:
    #                             blue_arc_dict[commodity] = [arc]

    #             # print(green_arc_dict)
    #             # print(blue_arc_dict)

    #             for commodity in priority_list:
    #                 # f.write("\n")
    #                 # f.write("Now moving " + str(commodity) + "\n")
    #                 # print("Now moving " + str(commodity))

    #                 red_arc_dict = {}
    #                 orange_arc_dict = {}
    #                 if commodity in blue_arc_dict:
    #                     for blue_arc in blue_arc_dict[commodity]:
    #                         for under_node in under_cap[time]:
    #                             origin_node = blue_arc[0]
    #                             cost = cost_dict[(origin_node[0], under_node[0])] - cost_dict[(origin_node[0], over_node[0])]
    #                             red_arc_dict[(origin_node, under_node, commodity)] = cost
    #                             # cost to add red_arc to current under_node and remove blue arc to over_node
    #                             # All within a single commodity type!
    #                 if commodity in green_arc_dict:
    #                     for green_arc in green_arc_dict[commodity]:
    #                         for under_node in under_cap[time]:
    #                             destination_node = green_arc[1]
    #                             cost = cost_dict[(under_node[0], destination_node[0])] - cost_dict[(over_node[0], destination_node[0])]
    #                             orange_arc_dict[((under_node[0], time, 'b'), destination_node, commodity)] = cost

    #                 # print(red_arc_dict)
    #                 # print(orange_arc_dict)
    #                 insertion_dict = {}
    #                 for red in red_arc_dict:
    #                     for orange in orange_arc_dict:
    #                         insertion_dict[(red, orange)] = red_arc_dict[red] + orange_arc_dict[orange]

    #                 # below func gives [(key_with_lowest_value), (key_with_second_lowest_value), ...]
    #                 sorted_insertion_list = sorted(insertion_dict, key=lambda k: insertion_dict[k])
    #                 for red_arc, orange_arc in sorted_insertion_list:
    #                     # f.write("__________________________________\n")
    #                     # f.write("Red Arc: " +str(red_arc) + "\n")
    #                     origin_node = red_arc[0]
    #                     under_node = red_arc[1]
    #                     destination_node = orange_arc[1]

    #                     blue_arc = (origin_node, over_node, commodity)
    #                     green_arc = ((over_node[0], over_node[1], 'b'), destination_node, commodity)
    #                     # print(movement_arcs_dict[blue_arc])
    #                     # print(movement_arcs_dict[green_arc])
    #                     if (over_node in over_cap[time]) and (movement_arcs_dict[blue_arc] > 0) and (movement_arcs_dict[green_arc] > 0):
    #                         if under_node in under_cap[time]:
    #                             # f.write("----------------------------------\n")
    #                             # f.write("Rerouting " +str(commodity) + " from " + str(origin_node) + "\n")
    #                             # f.write("Now checking " + str(under_node) + "\n")
    #                             a = abs(over_cap[time][over_node]) # Volume over capacity still to move from over_node
    #                             b = abs(under_cap[time][under_node]) # Spare capacity in under_node
    #                             c = abs(movement_arcs_dict[blue_arc]) # Volume available to move from origin_node
    #                             d = abs(movement_arcs_dict[green_arc]) # Volume available to move to destination_node
    #                             swap_count = min(a, b, c, d)
    #                             # f.write("    Volume to move from over_node     | "+ str(a) + "\n")
    #                             # f.write("    Space available in under_node     | "+ str(b) + "\n")
    #                             # f.write("    Num of commodity from origin_node | "+ str(c) + "\n")
    #                             # f.write("    Num of commodity to destination_node | "+ str(d) + "\n")
    #                             if swap_count > 0:
    #                                 # print("Moved " + str(swap_count) + " from " + str(over_node[0]) + " to " + str(under_node[0]) + " in t = " + str(over_node[1]))
    #                                 # f.write("Moved " + str(swap_count) + " from " + str(over_node[0]) + " to " + str(under_node[0]) + " in t = " + str(over_node[1]) + "\n")
    #                                 over_cap[time][over_node] -= swap_count
    #                                 under_cap[time][under_node] += swap_count

    #                                 movement_arcs_dict[blue_arc] -= swap_count
    #                                 movement_arcs_dict[red_arc] += swap_count
    #                                 movement_arcs_dict[green_arc] -= swap_count
    #                                 movement_arcs_dict[orange_arc] += swap_count

    #                                 model_cost += insertion_dict[(red_arc, orange_arc)] * swap_count

    #                                 # if movement_arcs_dict[(origin_node, over_node, commodity)] == 0:
    #                                 #     print(str(commodity) + " from " + str(origin_node) + " is now depleted. Move to next Blue Arc.")
    #                                 #     f.write(str(commodity) + " from " + str(origin_node) + " is now depleted. Move to next Blue Arc."+ "\n")
    #                                 if under_cap[time][under_node] == 0:
    #                                     # print(str(under_node) + " is now full")
    #                                     # f.write(str(under_node) + " is now full" + "\n")
    #                                     del under_cap[time][under_node]

    #                                 # print("Amount remaining: " + str(over_cap[time][over_node]))
    #                                 # f.write("Amount remaining: " + str(over_cap[time][over_node]) + "\n")

    #                             # f.write("----------------------------------\n")
    #                         if over_cap[time][over_node] == 0:
    #                             del over_cap[time][over_node]
    #                     # else:
    #                     #     f.write("    Num of commodity from origin_node: " + str(movement_arcs_dict[blue_arc]) + "\n")

    #                     #     if over_node in over_cap[time]:
    #                     #         f.write("    Volume to move from over_node: " + str(over_cap[time][over_node]) + "\n")
    #                     #     else:
    #                     #         f.write(str(over_node) + " not in over_cap[time]" + "\n")

    #                     #     if under_node in under_cap[time]:
    #                     #         f.write("    Space available in under_node: " + str(under_cap[time][under_node]) + "\n")
    #                     #     else:
    #                     #         f.write(str(under_node) + " not in under_cap[time]" + "\n")
    #     if any(time_echelons):
    #         time = sorted(list(time_echelons))[-1]
    #         for over_node in time_echelons[time]:
    #                 # f.write("__________________________________\n")
    #                 # f.write("Over Node: " + str(over_node) + "\n")
    #                 # f.write("----------------------------------\n")
    #                 print("__________________________________")
    #                 print("Over Node: " + str(over_node))

    #                 blue_arc_dict = {}
    #                 for arc in movement_arcs_dict:
    #                     tail, head, commodity = arc
    #                     if head == over_node:
    #                         if movement_arcs_dict[arc] > 0:
    #                             if commodity in blue_arc_dict:
    #                                 blue_arc_dict[commodity].append(arc)
    #                             else:
    #                                 blue_arc_dict[commodity] = [arc]

    #                 for commodity in priority_list:
    #                     # f.write("\n")
    #                     # f.write("Now moving " + str(commodity) + "\n")
    #                     print("Now moving " + str(commodity))

    #                     red_arc_dict = {}
    #                     if commodity in blue_arc_dict:
    #                         for blue_arc in blue_arc_dict[commodity]:
    #                             for under_node in under_cap[time]:
    #                                 origin_node = blue_arc[0]
    #                                 cost = cost_dict[(origin_node[0], under_node[0])] - cost_dict[(origin_node[0], over_node[0])]
    #                                 red_arc_dict[(origin_node, under_node, commodity)] = cost
    #                                 # cost to add red_arc to current under_node and remove blue arc to over_node
    #                                 # All within a single commodity type!

    #                     insertion_dict = red_arc_dict

    #                     # below func gives [(key_with_lowest_value), (key_with_second_lowest_value), ...]
    #                     sorted_insertion_list = sorted(insertion_dict, key=lambda k: insertion_dict[k])
    #                     for red_arc in sorted_insertion_list:
    #                         # if insertion_dict[red_arc] < 0:
    #                             # print(str(red_arc) + ":  " + str(insertion_dict[red_arc]) + "\n")
    #                         # f.write("__________________________________\n")
    #                         # f.write("Red Arc: " +str(red_arc) + "\n")
    #                         origin_node = red_arc[0]
    #                         under_node = red_arc[1]

    #                         blue_arc = (origin_node, over_node, commodity)

    #                         if (over_node in over_cap[time]) and (movement_arcs_dict[blue_arc] > 0):
    #                             if under_node in under_cap[time]:
    #                                 # f.write("----------------------------------\n")
    #                                 # f.write("Rerouting " +str(commodity) + " from " + str(origin_node) + "\n")
    #                                 # f.write("Now checking " + str(under_node) + "\n")
    #                                 a = abs(over_cap[time][over_node]) # Volume over capacity still to move from over_node
    #                                 b = abs(under_cap[time][under_node]) # Spare capacity in under_node
    #                                 c = abs(movement_arcs_dict[blue_arc]) # Volume available to move from origin_node
    #                                 swap_count = min(a, b, c)
    #                                 # f.write("    Volume to move from over_node     | "+ str(a) + "\n")
    #                                 # f.write("    Space available in under_node     | "+ str(b) + "\n")
    #                                 # f.write("    Num of commodity from origin_node | "+ str(c) + "\n")
    #                                 # f.write("    Num of commodity to destination_node | "+ str(d) + "\n")
    #                                 if swap_count > 0:

    #                                     # f.write("Moved " + str(swap_count) + " from " + str(over_node[0]) + " to " + str(under_node[0]) + " in t = " + str(over_node[1]) + "\n")
    #                                     over_cap[time][over_node] -= swap_count
    #                                     under_cap[time][under_node] += swap_count

    #                                     movement_arcs_dict[blue_arc] -= swap_count
    #                                     movement_arcs_dict[red_arc] += swap_count

    #                                     model_cost += insertion_dict[red_arc] * swap_count
    #                                     print("Moved " + str(swap_count) + " from " + str(over_node[0]) + " to " + str(under_node[0]) + " in t = " + str(over_node[1]) + " at a cost of " + str(insertion_dict[red_arc] * swap_count))

    #                                     # if movement_arcs_dict[(origin_node, over_node, commodity)] == 0:
    #                                     #     print(str(commodity) + " from " + str(origin_node) + " is now depleted. Move to next Blue Arc.")
    #                                     #     f.write(str(commodity) + " from " + str(origin_node) + " is now depleted. Move to next Blue Arc."+ "\n")
    #                                     if under_cap[time][under_node] == 0:
    #                                         # print(str(under_node) + " is now full")
    #                                         # f.write(str(under_node) + " is now full" + "\n")
    #                                         del under_cap[time][under_node]

    #                                     # print("Amount remaining: " + str(over_cap[time][over_node]))
    #                                     # f.write("Amount remaining: " + str(over_cap[time][over_node]) + "\n")

    #                                 # f.write("----------------------------------\n")
    #                             if over_cap[time][over_node] == 0:
    #                                 del over_cap[time][over_node]
    #     f.write("\nOUTPUT:\n")
    #     f.write("MCNF Cost: "+ str(original_cost)+ "\n")
    #     f.write("Updated Cost: "+ str(model_cost)+ "\n")
    #     f.write("Diff in Cost: "+ str(model_cost - original_cost)+ "\n")
    #     f.write("Remaining over nodes:\n")
    #     for time in  over_cap:
    #         for over_node in  over_cap[time]:
    #             f.write(": ".join([str(over_node), str(over_cap[time][over_node])])+ "\n")
    #     for time in  over_cap:
    #         for over_node in  over_cap[time]:
    #             for x in movement_arcs_dict:
    #                 if movement_arcs_dict[x] >0:
    #                     if x[1] == over_node:
    #                         f.write(str(x) + ": " + str(movement_arcs_dict[x]) + "\n")

    #     f.write("Remaining under nodes:\n")
    #     for time in under_cap:
    #         for under_node in  under_cap[time]:
    #             f.write(": ".join([str(under_node), str(under_cap[time][under_node])])+ "\n")
        # for time in under_cap:
        #     for under_node in  under_cap[time]:
        #         for x in movement_arcs_dict:
        #             if x[1] == under_node:
        #                 f.write(str(x) + ": " + str(movement_arcs_dict[x]) + "\n")

    # deas_xl = "DEAS_Equipment.xlsx"
    # priority_list = ["CHAIRS", "TABLES"]

    # deas_xl = "EquipmentInventory.xlsx"
    # deas_xl = "EquipmentInventoryTest2.xlsx"

    # priority_list = ["8 X 30 TABLES", "6 X 30 TABLES", "8 X 18 TABLES", "6 X 18 TABLES", "66 ROUND TABLES", "HIGH BOYS", "30 COCKTAIL ROUNDS",
    #     "MEETING ROOM CHAIRS", "PODIUMS", "STAGE SKIRT DOLLIES", "TABLE SKIRT DOLLIES", "MEETING ROOM CHAIR DOLLIES",
    #     "66 ROUND TABLE DOLLIES", "FOLDING CHAIR DOLLIES (V STACK)", "FOLDING CHAIR DOLLIES (SQUARE STACK)", "HIGH BOY DOLLIES",
    #     "LONG TABLE DOLLIES", "SHORT TABLE DOLLIES", "STAND UP TABLE DOLLIES", "16RISERS 6 X 8", "24RISERS 6 X 8", "32RISERS 6 X 8", "(3) STEP UNIT WITH RAIL",
    #     "(3) STEP UNIT WITHOUT RAIL", "(2) STEP UNIT WITH RAIL", "(2) STEP UNIT WITHOUT RAIL","SETS OF STAGE STEPS", "16RISERS 6 X 8", "24RISERS 6 X 8", "30 STAND-UP ROUNDS"]

## NOT NEEDED AFTER TRANSFOR IS UPDATED
    # xl_data = pd.read_excel(deas_xl,
    #     sheet_name=["Commodities", "Storage Rooms", "Movement Arcs", "Storage Room Arcs", "Event Room Arcs", "Utility Arcs"])

    # xl = pd.ExcelFile(deas_xl)
    # xl_data["Cost Data"] = xl.parse("Cost Data", header=None)
    # rows = xl_data["Cost Data"].values.tolist()
    # cost_dict = {}
    # for rowIndex in range (1, len(rows)):
    #     for columnIndex in range (1, (rowIndex + 1)):
    #         cost_dict[(rows[rowIndex][0], rows[0][columnIndex])] = rows[rowIndex][columnIndex]
    #         cost_dict[(rows[0][columnIndex], rows[rowIndex][0])] = rows[rowIndex][columnIndex]



def sup1(xl_data, cost_dict, priority_list):
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
    for arc_sheet in ['movement','storage', 'event', 'utility']:
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
    print("vars made")
###############################################################################
    time_echelons = sorted(time_echelons)
    rooms = e_rooms + s_rooms
    capped_nodes = [(s, t, "b") for s in s_rooms for t in time_echelons[1:-1]]

    s_room_caps = xl_data["storage_rooms"]
    # s_room_caps = {}
    # for row in xl_data["Storage Rooms"].values.tolist():
    #     s_room_caps[row[0]] = row[3]

    commodity_vols = xl_data["commodities"]
    # commodity_vols = {}
    # for row in xl_data["Commodities"].values.tolist():
    #     commodity_vols[row[0]] = row[2]
    # for c in [x[1] for x in commodity_vols]:
    #     if c not in commodities:
    #         del commodity_vols[c]

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
    print("fb constraints made")
##############################################################################
# Lagrangian Penalty

    cap_constrs = {}
    for s in capped_nodes:
        used_vol_s = LinExpr()
        for commodity in commodity_vols: ## NOT NEEDED?
            for arc in arc_vars['storage']: #"Storage Room Arcs"]:
                tail, head, com = arc
                if head == s and com == commodity:
                    # used_vol_s.add(arc_vars["Storage Room Arcs"][arc], commodity_vols[com])
                    used_vol_s.add(arc_vars['storage'][arc], commodity_vols[com][1])
        used_vol_s.add(-s_room_caps[s[0]])
        cap_constrs[s] = used_vol_s

    m.write("model.lp")

    # print(cap_constrs)
    print("Relaxed COnstrs made")
    lr = LagrangianRelaxation(m, iterations=100, relaxedConstrs=cap_constrs, commodityPriority=priority_list, cost_dict=cost_dict, arc_vars=arc_vars)
    iterations, output, setup_arcs = lr.subgradientAscent()
    # print(iterations)
    solution = output[sorted(output)[0]]

    return solution, setup_arcs




    # arcList = []
    # arcList.append(["Time", "From Room", "To Room", "Commodity", "Amount"])
    # for x in sorted(sorted(sorted(solution, key=lambda k: k[1][0]), key=lambda k: k[0][0]), key=lambda k: k[0][1]): ## Sort First by time, then by room???
    #     tail, head, commodity = x
    #     if head[0] != "t":
    #         if solution[x] > 0:
    #             # if tail[0] != head[0]:
    #             print(str(x) + ": " + str(solution[x]))
    #             arcList.append([tail[1], tail[0], head[0], commodity, solution[x]])

    # book = load_workbook(deas_xl)
    # df = pd.DataFrame(arcList)
    # writer = pd.ExcelWriter(deas_xl, engine='openpyxl')
    # writer.book = book
    # writer.sheets = dict((ws.title, ws) for ws in book.worksheets)
    # df.to_excel(writer, sheet_name="Schedule", index=False, index_label=False, header=False)
    # writer.save()



    # greedy_swap(cost_dict, arc_vars, cap_constrs, lr.m.objVal, priority_list)
    # print(output)
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

    output = sup1(xl_data, cost_dict, priority_list)
    print(output)
    print("\a")

if __name__ == "__main__":
    main()