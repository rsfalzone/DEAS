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
    (data_frame_dict, cost_dict, priority_list, echelon_dict, event_room_list, item_dict, requirement_rows, total_inventory_dict, storage_cap_dict) = Transform.sup()
    # print(data_frame_dict)
    # df = data_frame_dict["event"]
    # print(df.to_string())

    se_start = echelon_dict[1]
    se_end = echelon_dict[2]

    outerSolution = MCNF.sup1(data_frame_dict, cost_dict, priority_list)
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

    (data_frame_dict, cost_dict, echelon_dict, event_room_list, item_dict, requirement_rows, total_inventory_dict, storage_cap_dict) = Transform.innerMCNF(se_start, se_end, start_state, end_state, event_room_list, item_dict, cost_dict, requirement_rows, total_inventory_dict, storage_cap_dict)
    innerSolution = MCNF.sup1(data_frame_dict, cost_dict, priority_list)
    solution = innerSolution

    sorted_inner_arcs = sorted(solution, key=lambda k: k[0][1])

    i = 0
    j = 0
    while sorted_outer_arcs[i][0][1] == 0:
        outer_initializing_arc = sorted_outer_arcs[i]
        inventory, o_intermediary, com = outer_initializing_arc
        while sorted_inner_arcs[j][0][1] == 0:
            inner_initializing_arc = sorted_inner_arcs[i]
            i_intermediary, destination, i_com = inner_initializing_arc
            if o_intermediary == i_intermediary and com == i_com:
                solution[inventory, destination, com] = solution[inner_initializing_arc]
                del solution[inner_initializing_arc]
            j +=1
        i += 1


    print()
    print("To Excel")
    Transform.excelOutputWriter(solution, echelon_dict)

    log_str += diagnosticStr("\nDynamic Equipment Allocation System ended")
    log(log_str)
    print("\a")

if __name__ == "__main__":
    main()