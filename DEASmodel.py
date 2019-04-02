from LagrangianRelaxation import LagrangianRelaxation

class DEASModel(LagrangianRelaxation):
    def __init__(self, m, iterations=1000, relaxedConstrs=None, commodityPriority=None, costs= None):
        super().__init__(m, iterations, relaxedConstrs)
        self.commodityPriority = commodityPriority
        self.costs = costs

    def greedyAlgorithm(self):
        print("Greedy Swap in subclass")
        self.m.update()
        if any(self.relaxedConstrs) and (self.lagrangeMults.keys() == self.relaxedConstrs.keys()):
            if self.commodityPriority and self.costs:
                print("inputs exist, Ready to start")


#     movement_arcs = {}
#     for x in arc_vars["Movement Arcs"]:
#         movement_arcs[x] = arc_vars["Movement Arcs"][x].X

#     under_cap = {}
#     over_cap = {}
#     for node in cap_constrs:
#         if node[0] != "t":
#             axb = cap_constrs[node].getValue()
#             if axb < 0:
#                 if node[1] in under_cap:
#                     under_cap[node[1]][(node[0], node[1], "a")] =  axb
#                 else:
#                     under_cap[node[1]] = {(node[0], node[1], "a") :  axb}
#             elif axb > 0:
#                 if node[1] in over_cap:
#                     over_cap[node[1]][(node[0], node[1], "a")] =  axb
#                 else:
#                     over_cap[node[1]] = {(node[0], node[1], "a") :  axb}





# def greedy_swap(cost_dict, movement_arcs, under_cap, over_cap, model_cost, priority_list):
#     original_cost = model_cost

#     with open("log_file.txt","w") as f:
#         time_echelons = {} ## TODO: Rename?
#         for time in over_cap:
#             time_echelons[time] = sorted(over_cap[time], key=lambda k: over_cap[time][k], reverse=True)

#             for time in sorted(list(time_echelons))[:-1]:
#                 for over_node in time_echelons[time]:
#                     blue_arc_dict = {}
#                     green_arc_dict = {}
#                     for arc in movement_arcs:
#                         tail, head, commodity = arc
#                         if tail == (over_node[0], over_node[1], 'b'):
#                             if movement_arcs[arc] > 0:
#                                 if commodity in green_arc_dict:
#                                     green_arc_dict[commodity].append(arc)
#                                 else:
#                                     green_arc_dict[commodity] = [arc]
#                         if head == over_node:
#                             if movement_arcs[arc] > 0:
#                                 if commodity in blue_arc_dict:
#                                     blue_arc_dict[commodity].append(arc)
#                                 else:
#                                     blue_arc_dict[commodity] = [arc]

#                     for commodity in priority_list:
#                         red_arc_dict = {}
#                         if commodity in blue_arc_dict:
#                             for blue_arc in blue_arc_dict[commodity]:
#                                 for under_node in under_cap[time]:
#                                     origin_node = blue_arc[0]
#                                     cost = cost_dict[(origin_node[0], under_node[0])] - cost_dict[(origin_node[0], over_node[0])]
#                                     red_arc_dict[(origin_node, under_node, commodity)] = cost

#                         orange_arc_dict = {}
#                         if commodity in green_arc_dict:
#                             for green_arc in green_arc_dict[commodity]:
#                                 for under_node in under_cap[time]:
#                                     destination_node = green_arc[1]
#                                     cost = cost_dict[(under_node[0], destination_node[0])] - cost_dict[(over_node[0], destination_node[0])]
#                                     orange_arc_dict[((under_node[0], time, 'b'), destination_node, commodity)] = cost

#                         insertion_dict = {}
#                         for red in red_arc_dict:
#                             for orange in orange_arc_dict:
#                                 insertion_dict[(red, orange)] = red_arc_dict[red] + orange_arc_dict[orange]

#                         sorted_insertion_list = sorted(insertion_dict, key=lambda k: insertion_dict[k])
#                         for red_arc, orange_arc in sorted_insertion_list:
#                             origin_node = red_arc[0]
#                             under_node = red_arc[1]
#                             destination_node = orange_arc[1]

#                             blue_arc = (origin_node, over_node, commodity)
#                             green_arc = ((over_node[0], over_node[1], 'b'), destination_node, commodity)

#                             if (over_node in over_cap[time]) and (movement_arcs[blue_arc] > 0) and (movement_arcs[green_arc] > 0):
#                                 if under_node in under_cap[time]:
#                                     a = abs(over_cap[time][over_node]) # Volume over capacity still to move from over_node
#                                     b = abs(under_cap[time][under_node]) # Spare capacity in under_node
#                                     c = abs(movement_arcs[blue_arc]) # Volume available to move from origin_node
#                                     d = abs(movement_arcs[green_arc]) # Volume available to move to destination_node
#                                     swap_count = min(a, b, c, d)
#                                     if swap_count > 0:
#                                         over_cap[time][over_node] -= swap_count
#                                         under_cap[time][under_node] += swap_count

#                                         movement_arcs[blue_arc] -= swap_count
#                                         movement_arcs[red_arc] += swap_count
#                                         movement_arcs[green_arc] -= swap_count
#                                         movement_arcs[orange_arc] += swap_count

#                                         model_cost += insertion_dict[(red_arc, orange_arc)] * swap_count

#                                         if under_cap[time][under_node] == 0:
#                                             del under_cap[time][under_node]

#                                 if over_cap[time][over_node] == 0:
#                                     del over_cap[time][over_node]

#             if any(time_echelons):
#                 time = sorted(list(time_echelons))[-1]
#                 for over_node in time_echelons[time]:
#                         blue_arc_dict = {}
#                         for arc in movement_arcs:
#                             tail, head, commodity = arc
#                             if head == over_node:
#                                 if movement_arcs[arc] > 0:
#                                     if commodity in blue_arc_dict:
#                                         blue_arc_dict[commodity].append(arc)
#                                     else:
#                                         blue_arc_dict[commodity] = [arc]

#                         for commodity in priority_list:
#                             red_arc_dict = {}
#                             if commodity in blue_arc_dict:
#                                 for blue_arc in blue_arc_dict[commodity]:
#                                     for under_node in under_cap[time]:
#                                         origin_node = blue_arc[0]
#                                         cost = cost_dict[(origin_node[0], under_node[0])] - cost_dict[(origin_node[0], over_node[0])]
#                                         red_arc_dict[(origin_node, under_node, commodity)] = cost

#                             insertion_dict = red_arc_dict
#                             sorted_insertion_list = sorted(insertion_dict, key=lambda k: insertion_dict[k])
#                             for red_arc in sorted_insertion_list:
#                                 origin_node = red_arc[0]
#                                 under_node = red_arc[1]

#                                 blue_arc = (origin_node, over_node, commodity)

#                                 if (over_node in over_cap[time]) and (movement_arcs[blue_arc] > 0):
#                                     if under_node in under_cap[time]:
#                                         a = abs(over_cap[time][over_node]) # Volume over capacity still to move from over_node
#                                         b = abs(under_cap[time][under_node]) # Spare capacity in under_node
#                                         c = abs(movement_arcs[blue_arc]) # Volume available to move from origin_node
#                                         swap_count = min(a, b, c)
#                                         if swap_count > 0:
#                                             over_cap[time][over_node] -= swap_count
#                                             under_cap[time][under_node] += swap_count

#                                             movement_arcs[blue_arc] -= swap_count
#                                             movement_arcs[red_arc] += swap_count

#                                             model_cost += insertion_dict[red_arc] * swap_count

#                                             if under_cap[time][under_node] == 0:
#                                                 del under_cap[time][under_node]

#                                     if over_cap[time][over_node] == 0:
#                                         del over_cap[time][over_node]

#             f.write("\nOUTPUT:\n")
#             f.write("MCNF Cost: " + str(original_cost)+ "\n")
#             f.write("Updated Cost: " + str(model_cost)+ "\n")
#             f.write("Diff in Cost: " + str(model_cost - original_cost)+ "\n")

#             f.write("Remaining over nodes:\n")
#             for time in  over_cap:
#                 for over_node in  over_cap[time]:
#                     f.write(": ".join([str(over_node), str(over_cap[time][over_node])])+ "\n")

#             f.write("Remaining under nodes:\n")
#             for time in under_cap:
#                 for under_node in  under_cap[time]:
#                     f.write(": ".join([str(under_node), str(under_cap[time][under_node])])+ "\n")
