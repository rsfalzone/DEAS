import pandas as pd
import Transform
import MCNF

indent = "    "
deas_xl = "DEAS.xlsx"

def log(string, filename="log.txt"):
    with open(filename, "w") as f:
        f.write(string)

def diagnosticStr(string):
    print(string)
    return string + "\n"


def main():
    log_str = diagnosticStr("Dynamic Equipment Allocation System started")

    print("Creating Arcs")
    (data_frame_dict, cost_dict, priority_list, echelon_dict, event_room_list, item_dict, requirement_rows, total_inventory_dict, storage_cap_dict, inventory_dict) = Transform.sup()
    # print(data_frame_dict)
    # df = data_frame_dict["event"]
    #
    # for df in ['movement', 'storage', 'event', 'utility']:
    #     # print(data_frame_dict[df].to_string())
    #     Transform.excelWriter(data_frame_dict[df], df, deas_xl)

    se_start = echelon_dict[1]
    se_end = echelon_dict[2]

    outerSolution, outer_set_up = MCNF.sup1(data_frame_dict, cost_dict, priority_list)
    solution = outerSolution
    sorted_outer_arcs = sorted(solution, key=lambda k: k[0][1])


    start_state = {}
    end_state = {}
    for tail, head, com in sorted_outer_arcs:
        echelon = tail[1]
        if echelon == 0:
            room = head[0]
            if room in start_state:
                if com in start_state[room]:
                    start_state[room][com] += solution[(tail, head, com)]
                else:
                    start_state[room][com] = solution[(tail, head, com)]
            else:
                start_state[room] = {com:solution[(tail, head, com)]}
        elif echelon == 1:
            room = head[0]
            if room in end_state:
                if com in end_state[room]:
                    end_state[room][com] += solution[(tail, head, com)]
                else:
                    end_state[room][com] = solution[(tail, head, com)]
            else:
                end_state[room] = {com:solution[(tail, head, com)]}
    print("start")
    print(start_state)
    print("endd")
    print(end_state)

    (data_frame_dict, cost_dict, echelon_dict, event_room_list, item_dict, requirement_rows, total_inventory_dict, storage_cap_dict) = Transform.innerMCNF(se_start, se_end, start_state, end_state, event_room_list, item_dict, cost_dict, requirement_rows, total_inventory_dict, storage_cap_dict, inventory_dict)
    for df in ['movement', 'storage', 'event', 'utility']:
        # print(data_frame_dict[df].to_string())
        Transform.excelWriter(data_frame_dict[df], df, deas_xl)
    innerSolution, inner_set_up = MCNF.sup1(data_frame_dict, cost_dict, priority_list)
    solution = innerSolution

    sorted_inner_arcs = sorted(solution, key=lambda k: k[0][1])

    print("outer")
    for x in sorted_outer_arcs:
        if x[0][1] == 0:
            if outerSolution[x] > 0:
                print(str(x) + ": " + str(outerSolution[x]))
    print("inner")
    for x in sorted_inner_arcs:
        if x[0][1] == 0:
            if innerSolution[x] > 0:
                print(str(x) + ": " + str(innerSolution[x]))

    arcs_to_rem =[]
    arcs_to_add = {}
    greens = {}
    for outer_arc in sorted_outer_arcs:
        i, j, com = outer_arc
        if i[1] == 0 and j[1] == 1:
            if outerSolution[outer_arc] > 0:
                if com in greens:
                    if j[0] in greens[com]:
                        greens[com][j[0]].append(outer_arc)
                    else:
                        greens[com][j[0]] = [outer_arc]
                else:
                    greens[com] = {j[0] : [outer_arc]}
    print("greens")
    print(greens)
    for com in greens:
        # js = list(greens[com])
        js = {j : sum([outerSolution[green] for green in greens[com][j]]) for j in greens[com]}
        print("js")
        print(js)
        # sum([solution[green][j] for green in greens[com]])
        blues = {}
        for j in js:
            inner_start = (j, 0, "b")
            for inner_arc in sorted_inner_arcs:
                if inner_arc[2] == com:
                    if inner_arc[0] == inner_start:
                        if innerSolution[inner_arc] > 0:
                            if j in blues:
                                blues[j].append(inner_arc)
                            else:
                                blues[j] = [inner_arc]
        print("BLUES")
        print(blues)
        tree_cost = {}
        for j in js:
            for green in greens[com][j]:
                for blue in blues[j]:
                    cost = cost_dict[(green[0][0], blue[1][0])]
                    tree_cost[(green[0][0],j,blue[1][0])]= (cost, min(outerSolution[green], innerSolution[blue]))
        sorted_tree_cost = sorted(tree_cost, key=lambda k:tree_cost[k][0])
        print(sorted_tree_cost)

        i = 0
        while sum(js.values()) > 0:
            pinkarc = sorted_tree_cost[i]
            flow = min(tree_cost[pinkarc][1], js[pinkarc[1]])
            js[pinkarc[1]] -= flow
            i_node = (pinkarc[0], 0, "b")
            j_node = (pinkarc[2], 1, "a")
            arcs_to_add[(i_node, j_node, com)] = flow
            i += 1

        print(arcs_to_add)

    for x in innerSolution:
        if x[0][1] == 0 and x[0][2] == "b":
            if x not in arcs_to_rem:
                arcs_to_rem.append(x)

    for x in arcs_to_rem:
        del solution[x]

    for x in arcs_to_add:
        solution[x] = arcs_to_add[x]



    # print()
    # print("SOLN")
    # for x in sorted(sorted(sorted(solution, key=lambda k: k[1][0]), key=lambda k: k[0][0]), key=lambda k: k[0][1]):
    #     if solution[x] > 0:
    #         print(str(x) + ": " + str(solution[x]))


    print()
    print("To Excel")
    Transform.excelOutputWriter(solution, echelon_dict)

    log_str += diagnosticStr("\nDynamic Equipment Allocation System ended")
    log(log_str)
    print("\a")

if __name__ == "__main__":
    main()