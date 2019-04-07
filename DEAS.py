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
    # print(data_frame_dict)
    df = data_frame_dict["event"]
    print(df.to_string())


    outerSolution = MCNF.sup1(data_frame_dict, cost_dict, priority_list)
    solution = outerSolution

    start_state = {}
    end_state = {}
    for tail, head, com in sorted(solution, key=lambda k: k[0][1]):
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

    print()
    print("To Excel")
    Transform.excelOutputWriter(solution, echelon_dict)

    log_str += diagnosticStr("\nDynamic Equipment Allocation System ended")
    log(log_str)
    print("\a")

if __name__ == "__main__":
    main()