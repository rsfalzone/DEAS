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
    (data_frame_dict, cost_dict, priority_list, echelon_dict) = Transform.sup()
    print(data_frame_dict)


    outerSolution = MCNF.sup1(data_frame_dict, cost_dict, priority_list)
    solution = outerSolution

    start_state = {}
    end_state = {}
    for x in sorted(solution, key=lambda k: k[0][1]):
        if x[0][1] == 0:
            start_state[x] = solution[x]
        elif x[0][1] == 1:
            end_state[x] = solution[x]

    utility = {}
    for arc in start_state:
        _, (room, _, _), com = arc
        if (("s", 0, "a"), (room, 0, "b"), com) in utility:
            utility[(("s", 0, "a"), (room, 0, "b"), com)] += start_state[arc]
        else:
            utility[(("s", 0, "a"), (room, 0, "b"), com)] = start_state[arc]


    LAST_TIME_ECHELON = "LAST ECHELON FROM INNER"
    mvnt = {}
    for arc in end_state:
        tail, head, com = arc
        room, _, _ = head
        if ((room, "Second to " +LAST_TIME_ECHELON, "b"), ("t", LAST_TIME_ECHELON , "a"), com) in mvnt:
            mvnt[((room, "Second to " +LAST_TIME_ECHELON, "b"), ("t", LAST_TIME_ECHELON, "a"), com)] += end_state[arc]
        else:
            mvnt[((room, "Second to " +LAST_TIME_ECHELON, "b"), ("t", LAST_TIME_ECHELON, "a"), com)] = end_state[arc]


    print()
    print("Utility")
    for x in utility:
        print(str(x) + ": " + str(utility[x]))

    print()
    print("MVNT")
    for x in mvnt:
        print(str(x) + ": " + str(mvnt[x]))


    print()
    print("To Excel")
    Transform.excelOutputWriter(solution, echelon_dict)

    log_str += diagnosticStr("\nDynamic Equipment Allocation System ended")
    log(log_str)
    print("\a")

if __name__ == "__main__":
    main()