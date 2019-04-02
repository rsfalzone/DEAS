import math
from gurobipy import *

def norm(vector):
    sum = 0
    for x in vector:
        sum += x**2
    return math.sqrt(sum)

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


class LagrangianRelaxation(object):
    def __init__(self, m, iterations=1000, relaxedConstrs=None, commodityPriority=None, cost_dict=None, arc_vars=None):
        self.m = m
        self.mSense = m.ModelSense
        self.unrelaxedObj = m.getObjective()
        self.iterations=iterations
        if relaxedConstrs != None:
            self.relaxedConstrs = relaxedConstrs
            self.lagrangeMults = {key: 0 for key in relaxedConstrs}
        self.commodityPriority = commodityPriority
        self.cost_dict = cost_dict
        self.arc_vars = arc_vars


    def updateObj(self):
        penalty = LinExpr()
        for c in self.relaxedConstrs:
            penalty.add(self.relaxedConstrs[c], self.lagrangeMults[c])

        self.objective = LinExpr()
        self.objective.add(self.unrelaxedObj)
        self.objective.add(penalty)
        return self.objective

    def greedyAlgorithm(self, iteration):
        print("greedy_swap")
        original_cost = self.unrelaxedObj.getValue()
        model_cost = original_cost

        movement_arcs_dict = {}
        for x in self.arc_vars["Movement Arcs"]:
            movement_arcs_dict[x] = self.arc_vars["Movement Arcs"][x].X

        under_cap = {}
        over_cap = {}
        for node in self.relaxedConstrs:
            if node[0] != "t":
                axb = self.relaxedConstrs[node].getValue()
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

        time_echelons = {} ## TODO: Rename?
        for time in over_cap:
            time_echelons[time] = sorted(over_cap[time], key=lambda k: over_cap[time][k], reverse=True)
        # print(time_echelons)
            # Sort:
            #     reverse = True
            #       - descending
            #     key = lambda (argument : expression)
            #       - Iterate over_cap[time].keys() to sort
            #            for k in over_cap[time].keys():
            #                k -> over_cap[time][k]

        with open(str(iteration).join(["log_file", ".txt"]),"w") as f:
            f.write("\nINPUT:\n")
            f.write("MCNF Cost: "+ str(original_cost)+ "\n")
            f.write("Remaining over nodes:\n")
            for time in  over_cap:
                for over_node in  over_cap[time]:
                    f.write(": ".join([str(over_node), str(over_cap[time][over_node])])+ "\n")
            for time in  over_cap:
                for over_node in  over_cap[time]:
                    for x in movement_arcs_dict:
                        if movement_arcs_dict[x] >0:
                            if x[1] == over_node:
                                f.write(str(x) + ": " + str(movement_arcs_dict[x]) + "\n")

            f.write("Starting under nodes:\n")
            for time in under_cap:
                for under_node in  under_cap[time]:
                    f.write(": ".join([str(under_node), str(under_cap[time][under_node])])+ "\n")


            for time in sorted(list(time_echelons))[:-1]:
                for over_node in time_echelons[time]:
                    # f.write("__________________________________\n")
                    # f.write("Over Node: " + str(over_node) + "\n")
                    # f.write("----------------------------------\n")
                    # print("__________________________________")
                    # print("Over Node: " + str(over_node))

                    blue_arc_dict = {}
                    green_arc_dict = {}
                    for arc in movement_arcs_dict:
                        tail, head, commodity = arc
                        if tail == (over_node[0], over_node[1], 'b'):
                            if movement_arcs_dict[arc] > 0:
                                if commodity in green_arc_dict:
                                    green_arc_dict[commodity].append(arc)
                                else:
                                    green_arc_dict[commodity] = [arc]
                        if head == over_node:
                            if movement_arcs_dict[arc] > 0:
                                if commodity in blue_arc_dict:
                                    blue_arc_dict[commodity].append(arc)
                                else:
                                    blue_arc_dict[commodity] = [arc]

                    # print(green_arc_dict)
                    # print(blue_arc_dict)

                    for commodity in self.commodityPriority:
                        # f.write("\n")
                        # f.write("Now moving " + str(commodity) + "\n")
                        # print("Now moving " + str(commodity))

                        red_arc_dict = {}
                        orange_arc_dict = {}
                        if commodity in blue_arc_dict:
                            for blue_arc in blue_arc_dict[commodity]:
                                for under_node in under_cap[time]:
                                    origin_node = blue_arc[0]
                                    cost = self.cost_dict[(origin_node[0], under_node[0])] - self.cost_dict[(origin_node[0], over_node[0])]
                                    red_arc_dict[(origin_node, under_node, commodity)] = cost
                                    # cost to add red_arc to current under_node and remove blue arc to over_node
                                    # All within a single commodity type!
                        if commodity in green_arc_dict:
                            for green_arc in green_arc_dict[commodity]:
                                for under_node in under_cap[time]:
                                    destination_node = green_arc[1]
                                    cost = self.cost_dict[(under_node[0], destination_node[0])] - self.cost_dict[(over_node[0], destination_node[0])]
                                    orange_arc_dict[((under_node[0], time, 'b'), destination_node, commodity)] = cost

                        # print(red_arc_dict)
                        # print(orange_arc_dict)
                        insertion_dict = {}
                        for red in red_arc_dict:
                            for orange in orange_arc_dict:
                                insertion_dict[(red, orange)] = red_arc_dict[red] + orange_arc_dict[orange]

                        # below func gives [(key_with_lowest_value), (key_with_second_lowest_value), ...]
                        sorted_insertion_list = sorted(insertion_dict, key=lambda k: insertion_dict[k])
                        for red_arc, orange_arc in sorted_insertion_list:
                            # f.write("__________________________________\n")
                            # f.write("Red Arc: " +str(red_arc) + "\n")
                            origin_node = red_arc[0]
                            under_node = red_arc[1]
                            destination_node = orange_arc[1]

                            blue_arc = (origin_node, over_node, commodity)
                            green_arc = ((over_node[0], over_node[1], 'b'), destination_node, commodity)
                            # print(movement_arcs_dict[blue_arc])
                            # print(movement_arcs_dict[green_arc])
                            if (over_node in over_cap[time]) and (movement_arcs_dict[blue_arc] > 0) and (movement_arcs_dict[green_arc] > 0):
                                if under_node in under_cap[time]:
                                    # f.write("----------------------------------\n")
                                    # f.write("Rerouting " +str(commodity) + " from " + str(origin_node) + "\n")
                                    # f.write("Now checking " + str(under_node) + "\n")
                                    a = abs(over_cap[time][over_node]) # Volume over capacity still to move from over_node
                                    b = abs(under_cap[time][under_node]) # Spare capacity in under_node
                                    c = abs(movement_arcs_dict[blue_arc]) # Volume available to move from origin_node
                                    d = abs(movement_arcs_dict[green_arc]) # Volume available to move to destination_node
                                    swap_count = min(a, b, c, d)
                                    # f.write("    Volume to move from over_node     | "+ str(a) + "\n")
                                    # f.write("    Space available in under_node     | "+ str(b) + "\n")
                                    # f.write("    Num of commodity from origin_node | "+ str(c) + "\n")
                                    # f.write("    Num of commodity to destination_node | "+ str(d) + "\n")
                                    if swap_count > 0:
                                        # print("Moved " + str(swap_count) + " from " + str(over_node[0]) + " to " + str(under_node[0]) + " in t = " + str(over_node[1]))
                                        # f.write("Moved " + str(swap_count) + " from " + str(over_node[0]) + " to " + str(under_node[0]) + " in t = " + str(over_node[1]) + "\n")
                                        over_cap[time][over_node] -= swap_count
                                        under_cap[time][under_node] += swap_count

                                        movement_arcs_dict[blue_arc] -= swap_count
                                        movement_arcs_dict[red_arc] += swap_count
                                        movement_arcs_dict[green_arc] -= swap_count
                                        movement_arcs_dict[orange_arc] += swap_count

                                        model_cost += insertion_dict[(red_arc, orange_arc)] * swap_count

                                        # if movement_arcs_dict[(origin_node, over_node, commodity)] == 0:
                                        #     print(str(commodity) + " from " + str(origin_node) + " is now depleted. Move to next Blue Arc.")
                                        #     f.write(str(commodity) + " from " + str(origin_node) + " is now depleted. Move to next Blue Arc."+ "\n")
                                        if under_cap[time][under_node] == 0:
                                            # print(str(under_node) + " is now full")
                                            # f.write(str(under_node) + " is now full" + "\n")
                                            del under_cap[time][under_node]

                                        # print("Amount remaining: " + str(over_cap[time][over_node]))
                                        # f.write("Amount remaining: " + str(over_cap[time][over_node]) + "\n")

                                    # f.write("----------------------------------\n")
                                if over_cap[time][over_node] == 0:
                                    del over_cap[time][over_node]
                            # else:
                            #     f.write("    Num of commodity from origin_node: " + str(movement_arcs_dict[blue_arc]) + "\n")

                            #     if over_node in over_cap[time]:
                            #         f.write("    Volume to move from over_node: " + str(over_cap[time][over_node]) + "\n")
                            #     else:
                            #         f.write(str(over_node) + " not in over_cap[time]" + "\n")

                            #     if under_node in under_cap[time]:
                            #         f.write("    Space available in under_node: " + str(under_cap[time][under_node]) + "\n")
                            #     else:
                            #         f.write(str(under_node) + " not in under_cap[time]" + "\n")
            if any(time_echelons):
                time = sorted(list(time_echelons))[-1]
                for over_node in time_echelons[time]:
                        # f.write("__________________________________\n")
                        # f.write("Over Node: " + str(over_node) + "\n")
                        # f.write("----------------------------------\n")
                        print("__________________________________")
                        print("Over Node: " + str(over_node))

                        blue_arc_dict = {}
                        for arc in movement_arcs_dict:
                            tail, head, commodity = arc
                            if head == over_node:
                                if movement_arcs_dict[arc] > 0:
                                    if commodity in blue_arc_dict:
                                        blue_arc_dict[commodity].append(arc)
                                    else:
                                        blue_arc_dict[commodity] = [arc]

                        for commodity in self.commodityPriority:
                            # f.write("\n")
                            # f.write("Now moving " + str(commodity) + "\n")
                            print("Now moving " + str(commodity))

                            red_arc_dict = {}
                            if commodity in blue_arc_dict:
                                for blue_arc in blue_arc_dict[commodity]:
                                    for under_node in under_cap[time]:
                                        origin_node = blue_arc[0]
                                        cost = self.cost_dict[(origin_node[0], under_node[0])] - self.cost_dict[(origin_node[0], over_node[0])]
                                        red_arc_dict[(origin_node, under_node, commodity)] = cost
                                        # cost to add red_arc to current under_node and remove blue arc to over_node
                                        # All within a single commodity type!

                            insertion_dict = red_arc_dict

                            # below func gives [(key_with_lowest_value), (key_with_second_lowest_value), ...]
                            sorted_insertion_list = sorted(insertion_dict, key=lambda k: insertion_dict[k])
                            for red_arc in sorted_insertion_list:
                                # if insertion_dict[red_arc] < 0:
                                    # print(str(red_arc) + ":  " + str(insertion_dict[red_arc]) + "\n")
                                # f.write("__________________________________\n")
                                # f.write("Red Arc: " +str(red_arc) + "\n")
                                origin_node = red_arc[0]
                                under_node = red_arc[1]

                                blue_arc = (origin_node, over_node, commodity)

                                if (over_node in over_cap[time]) and (movement_arcs_dict[blue_arc] > 0):
                                    if under_node in under_cap[time]:
                                        # f.write("----------------------------------\n")
                                        # f.write("Rerouting " +str(commodity) + " from " + str(origin_node) + "\n")
                                        # f.write("Now checking " + str(under_node) + "\n")
                                        a = abs(over_cap[time][over_node]) # Volume over capacity still to move from over_node
                                        b = abs(under_cap[time][under_node]) # Spare capacity in under_node
                                        c = abs(movement_arcs_dict[blue_arc]) # Volume available to move from origin_node
                                        swap_count = min(a, b, c)
                                        # f.write("    Volume to move from over_node     | "+ str(a) + "\n")
                                        # f.write("    Space available in under_node     | "+ str(b) + "\n")
                                        # f.write("    Num of commodity from origin_node | "+ str(c) + "\n")
                                        # f.write("    Num of commodity to destination_node | "+ str(d) + "\n")
                                        if swap_count > 0:

                                            # f.write("Moved " + str(swap_count) + " from " + str(over_node[0]) + " to " + str(under_node[0]) + " in t = " + str(over_node[1]) + "\n")
                                            over_cap[time][over_node] -= swap_count
                                            under_cap[time][under_node] += swap_count

                                            movement_arcs_dict[blue_arc] -= swap_count
                                            movement_arcs_dict[red_arc] += swap_count

                                            model_cost += insertion_dict[red_arc] * swap_count
                                            print("Moved " + str(swap_count) + " from " + str(over_node[0]) + " to " + str(under_node[0]) + " in t = " + str(over_node[1]) + " at a cost of " + str(insertion_dict[red_arc] * swap_count))

                                            # if movement_arcs_dict[(origin_node, over_node, commodity)] == 0:
                                            #     print(str(commodity) + " from " + str(origin_node) + " is now depleted. Move to next Blue Arc.")
                                            #     f.write(str(commodity) + " from " + str(origin_node) + " is now depleted. Move to next Blue Arc."+ "\n")
                                            if under_cap[time][under_node] == 0:
                                                # print(str(under_node) + " is now full")
                                                # f.write(str(under_node) + " is now full" + "\n")
                                                del under_cap[time][under_node]

                                            # print("Amount remaining: " + str(over_cap[time][over_node]))
                                            # f.write("Amount remaining: " + str(over_cap[time][over_node]) + "\n")

                                        # f.write("----------------------------------\n")
                                    if over_cap[time][over_node] == 0:
                                        del over_cap[time][over_node]
            f.write("\nOUTPUT:\n")
            f.write("MCNF Cost: "+ str(original_cost)+ "\n")
            f.write("Updated Cost: "+ str(model_cost)+ "\n")
            f.write("Diff in Cost: "+ str(model_cost - original_cost)+ "\n")
            f.write("Remaining over nodes:\n")
            for time in  over_cap:
                for over_node in  over_cap[time]:
                    f.write(": ".join([str(over_node), str(over_cap[time][over_node])])+ "\n")
            for time in  over_cap:
                for over_node in  over_cap[time]:
                    for x in movement_arcs_dict:
                        if movement_arcs_dict[x] >0:
                            if x[1] == over_node:
                                f.write(str(x) + ": " + str(movement_arcs_dict[x]) + "\n")

            f.write("Remaining under nodes:\n")
            for time in under_cap:
                for under_node in  under_cap[time]:
                    f.write(": ".join([str(under_node), str(under_cap[time][under_node])])+ "\n")
        return model_cost


    def printOutput(self, i):
        print("Results of Subgradient")
        if self.m.status == GRB.Status.OPTIMAL:
            print()
            print("GUROBI MODEL OUTPUT:")
            print('Penalized Objective Value: %g' % self.m.objVal)
            print("Real Objective Value: %g" % self.unrelaxedObj.getValue())
            print("Iterations of Subgradient Ascent: {}".format(i))
            print("Movement Arcs:")
            for var in self.arc_vars["Movement Arcs"]:
                if self.arc_vars["Movement Arcs"][var].X > 0:
                    print("{:<60s}| {:>8.0f}".format(str(var), self.arc_vars["Movement Arcs"][var].X))
            print("\nStorage Room Arcs:")
            for var in self.arc_vars["Storage Room Arcs"]:
                if self.arc_vars["Storage Room Arcs"][var].X > 0:
                    print("{:<60s}| {:>8.0f}".format(str(var), self.arc_vars["Storage Room Arcs"][var].X))
            print('\nAx-b:')
            for s in self.relaxedConstrs:
                print(str(s) + ": " + str(self.relaxedConstrs[s].getValue()))
        else:
            print('No solution;', self.m.status)

    def subgradientAscent(self):
        updated_costs = []
        diff_in_cost = []
        self.m.optimize()
        if self.m.status == GRB.Status.OPTIMAL:
            if any(self.relaxedConstrs) and (self.lagrangeMults.keys() == self.relaxedConstrs.keys()):
                i = 1
                while i < self.iterations:
                    stepsize = math.sqrt(1/i)
                    currLagrangeMults = {}  # Lagrange mults for the current iteration
                    dLagrangeMults = []     # Rate of change vector for Lagrange mults
                    for c in self.relaxedConstrs:
                        steepestAscent = self.relaxedConstrs[c].getValue()
                        currLagrangeMults[c] = self.lagrangeMults[c] + max(stepsize * steepestAscent, 0)
                        dLagrangeMults.append((currLagrangeMults[c] - self.lagrangeMults[c]) / i)
                    if norm(dLagrangeMults) > 0 :
                        self.lagrangeMults = currLagrangeMults
                        self.updateObj()
                        print(linExpr2Str(self.m.getObjective()))
                        print(linExpr2Str(self.unrelaxedObj))
                        self.m.optimize()
                        # cost_w_greedy = self.greedyAlgorithm(i)
                        # updated_costs.append(cost_w_greedy)
                        # diff_in_cost.append()
                        self.printOutput(i)
                        i += 1
                    else:
                        self.iterations = i
                print(updated_costs)
                # print(diff_in_cost)
                return self.iterations
            else:
                # No relaxed constraints to penalize
                # Or mismatch between multipliers and constraints
                self.printOutput()
                return m.status
        else:
            return m.status
