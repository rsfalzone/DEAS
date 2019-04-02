import pandas as pd
import Transform

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

    data_frame_dict = Transform.sup()
    print(data_frame_dict)

    # MCNF.Main()

    # output crap

    # xl_data = pd.read_excel(deas_xl, sheet_name=None)
    # log_str += diagnosticStr(1*indent + deas_xl + ":")
    # for sheet in xl_data:
    #     log_str += diagnosticStr("\n" + sheet + ":")
    #     for row in xl_data[sheet].values.tolist():
    #         log_str += diagnosticStr(str(row))

    log_str += diagnosticStr("\nDynamic Equipment Allocation System ended")
    log(log_str)
    print("\a")

if __name__ == "__main__":
    main()