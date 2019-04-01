import pandas as pd

def main():
    deas_xl = "DEAS_Equipment.xlsx"
    xl_data = pd.read_excel(deas_xl,
        sheet_name=[
        "Commodities", "Storage Rooms", "Cost Data",
        "Movement Arcs", "Storage Room Arcs",
        "Event Room Arcs", "Utility Arcs"
        ])
    for sheet in xl_data:
        print(sheet + ":")
        for row in xl_data[sheet].values.tolist():
            print(str(row))

if __name__ == "__main__":
    main()