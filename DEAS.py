import pandas as pd
import Transform
import MCNF

indent = "    "
deas_xl = "DEAS_Equipment.xlsx"

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
    for df in ['movement', 'storage', 'event', 'utility']:
        # print(data_frame_dict[df].to_string())
        Transform.excelWriter(data_frame_dict[df], df, deas_xl)

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


    arcs_to_add = {}
    for outer_arc in sorted_outer_arcs:
        if outer_arc[0][1] == 0:
            inventory_room = outer_arc[0][0]
            outer_intermediary_room = outer_arc[1][0]
            outer_com = outer_arc[2]
            outer_val = outerSolution[outer_arc]
            for inner_arc in sorted_inner_arcs:
                if inner_arc[0][1] == 0:
                    inner_com = inner_arc[2]
                    if outer_com == inner_com:
                        inner_intermediary_room = inner_arc[0][0]
                        if outer_intermediary_room == inner_intermediary_room:
                            destination_room = inner_arc[1][0]
                            inner_val = innerSolution[inner_arc]
                            if ((inventory_room, 0, "b"), (destination_room, 0, "a"), outer_com) in arcs_to_add:
                                arcs_to_add[((inventory_room, 0, "b"), (destination_room, 0, "a"), outer_com)] += min(outer_val, inner_val)
                            else:
                                arcs_to_add[((inventory_room, 0, "b"), (destination_room, 0, "a"), outer_com)] = min(outer_val, inner_val)

    print("add")
    for x in arcs_to_add:
        if arcs_to_add[x] > 0:
            print(str(x) + ": " +str(arcs_to_add[x]))

    arcs_to_rem = []
    for inner_arc in sorted_inner_arcs:
        if inner_arc[0][1] == 0:
            arcs_to_rem.append(inner_arc)
    print("del")
    print(arcs_to_rem)

    for x in arcs_to_rem:
        del solution[x]

    for x in arcs_to_add:
        solution[x] = arcs_to_add[x]



    print()
    print("SOLN")
    for x in sorted(sorted(sorted(solution, key=lambda k: k[1][0]), key=lambda k: k[0][0]), key=lambda k: k[0][1]):
        if solution[x] > 0:
            print(str(x) + ": " + str(solution[x]))


    print()
    print("To Excel")
    Transform.excelOutputWriter(solution, echelon_dict)

    log_str += diagnosticStr("\nDynamic Equipment Allocation System ended")
    log(log_str)
    print("\a")

if __name__ == "__main__":
    main()