
import csv
import re
import datetime
import pandas as pd
from openpyxl import load_workbook

excel_filename = "DEAS_Equipment.xlsx"
# excel_filename = "EquipmentInventory.xlsx"

def currentStateReader():

    #Read in current inventory levels for storage

    xl = pd.ExcelFile(excel_filename)
    inventory_df = xl.parse("Inventory by Room")
    inventory_rows = inventory_df.values.tolist()

    inventory_dict = {}
    for row in inventory_rows:
        inventory_dict[(row[0], row[1])] = float(row[2])

    total_inventory_dict = {}
    for (room, commodity) in inventory_dict.keys():
        if commodity in total_inventory_dict:
            total_inventory_dict[commodity] += inventory_dict[(room, commodity)]
        else:
            total_inventory_dict[commodity] = inventory_dict[(room, commodity)]

    xl = pd.ExcelFile(excel_filename)
    storage_df = xl.parse("Storage Rooms")
    storage_rows = storage_df.values.tolist()

    storage_cap_dict = {}
    for row in storage_rows:
        storage_cap_dict[row[0]] = float(row[3])

    #Read in active room requirements
    #Notes:
    #   Echelons are based on set up start times

    xl = pd.ExcelFile(excel_filename)
    requirement_df = xl.parse("Event Requirements")
    requirement_rows = requirement_df.values.tolist()

    event_dict = {}
    echelon_dict = {}
    echelon_dict_reverse = {}
    event_room_list = []
    item_list = []
    item_dict = {}
    priority_dict = {}
    requirement_dict = {}
    for row in requirement_rows:
        # if row[2] not in echelon_dict.values():
        #     echelon_dict[len(echelon_dict) + 1] = row[2]
        #     echelon_dict_reverse[row[2]] = len(echelon_dict_reverse) + 1
        if row[1] not in event_room_list:
            event_room_list.append(row[1])
        if row[6] not in item_list:
            item_list.append(row[6])
        if row[0] not in event_dict.keys():
            event_dict[row[0]] = ([row[2]], [row[5]])
        else:
            event_dict[row[0]][0].append(row[2])
            event_dict[row[0]][1].append(row[5])

        

    event_times_dict = {}
    print("Event dict:")
    print(event_dict)
    for event in event_dict:
        earliest_setup = sorted(event_dict[event][0])[0]
        latest_end = sorted(event_dict[event][1])[-1]
        event_times_dict[event] = (earliest_setup, latest_end)

    sorted_events = sorted(event_times_dict, key=lambda k: event_times_dict[k][0])
    print("\nsorted events:")
    print(sorted_events)

    super_event_dict = {}
    i = 0
    while i < (len(sorted_events) - 1):
        event = sorted_events[i]
        next_event = sorted_events[i + 1]
        if event_times_dict[event][1] < event_times_dict[next_event][0]:
            super_event_dict[event] = event_times_dict[event]
            i += 1
        else:
            conglomerate_name = event + ' and ' + next_event
            super_event_dict[conglomerate_name] = (event_times_dict[event][0], max(event_times_dict[next_event][0], event_times_dict[next_event][1]))
            i += 2


    print("\nsuper event dict:")
    print(super_event_dict)
    event_requirement_dict = {}
    sorted_super_events = sorted(super_event_dict, key=lambda k: super_event_dict[k][0])
    for i in range(len(sorted_super_events)):
        echelon_dict[i] = super_event_dict[sorted_super_events[i]][0]
        echelon_dict_reverse[super_event_dict[sorted_super_events[i]][0]] = i
        event_requirement_dict[sorted_super_events[i]] = []

    print('\nreq rows:')
    print(requirement_rows)

    for i in range(len(sorted_super_events)):
        if i != len(sorted_super_events) - 1:  
            print('\n')
            print(sorted_super_events[i])
            for row in requirement_rows:
                print('\n')
                print(row)
                print(echelon_dict[i], echelon_dict[i + 1])
                if row[2] >= echelon_dict[i] and row[2] < echelon_dict[i + 1]:
                    event_requirement_dict[sorted_super_events[i]].append(row)
                    print("added")
        else:
            for row in requirement_rows:
                if row[2] >= echelon_dict[i]:
                    event_requirement_dict[sorted_super_events[i]].append(row)
                    print('added')

    print("event requirement dict:")
    print(event_requirement_dict)

    print("Echelon Dict:")
    print(echelon_dict)

    for event in event_requirement_dict:
        for requirement in event_requirement_dict[event]:
            event_start = super_event_dict[event][0]
            event_end = super_event_dict[event][1]
            if (requirement[1], echelon_dict_reverse[event_start]) not in requirement_dict:
                requirement_dict[(requirement[1], echelon_dict_reverse[event_start])] = []
            requirement_dict[(requirement[1], echelon_dict_reverse[event_start])].append((requirement[6], requirement[7]))

    print("\nrequirement dict:")
    print(requirement_dict)

    new_requirement_dict = {}
    for (room, echelon) in requirement_dict:
        commodity_list = []
        new_requirement_dict[(room, echelon)] = []
        for req in requirement_dict[(room, echelon)]:
            if req[0] not in commodity_list:
                commodity_list.append(req[0])
        for commodity in commodity_list:
            commodity_max = 0
            for req in requirement_dict[(room, echelon)]:
                if req[0] == commodity:
                    if req[1] > commodity_max:
                        commodity_max = req[1]
            new_requirement_dict[(room, echelon)].append([commodity, commodity_max])

    requirement_dict = new_requirement_dict

    print('\nNew req dict:')
    print(new_requirement_dict)


    # for row in requirement_rows:
    #     if (row[1], echelon_dict_reverse[row[2]]) not in requirement_dict:
    #         requirement_dict[(row[1], echelon_dict_reverse[row[2]])] = []
    #     requirement_dict[(row[1], echelon_dict_reverse[row[2]])].append((row[6], row[7]))

    xl = pd.ExcelFile(excel_filename)
    items_df = xl.parse("Commodities")
    items_rows = items_df.values.tolist()

    for row in items_rows:
        if any(row):
            if row[0] in item_list:
                item_dict[row[0]] = (float(row[1]), float(row[2]))
                priority_dict[row[0]] = int(row[3])


    priority_list = sorted(priority_dict, key=lambda k: priority_dict[k])

    return(inventory_dict, echelon_dict, event_room_list, item_dict, requirement_dict, total_inventory_dict, storage_cap_dict, priority_list, super_event_dict)

def costDataReader():
    xl = pd.ExcelFile(excel_filename)
    df = xl.parse("Cost Data", header=None)
    rows = df.values.tolist()
    cost_dict = {}
    for rowIndex in range (1, len(rows)):
        for columnIndex in range (1, (rowIndex + 1)):
            cost_dict[(rows[rowIndex][0], rows[0][columnIndex])] = rows[rowIndex][columnIndex]
            cost_dict[(rows[0][columnIndex], rows[rowIndex][0])] = rows[rowIndex][columnIndex]
    return cost_dict

def constructor(echelon_dict, eventRoomList, item_dict, costDict, requirementDict, inventory_dict, total_inventory_dict, storage_cap_dict):

    #Creates 4 sets of arcs:
    #   movement_arc_dict       All b to a, room to room movement arcs (decisions)
    #   storage_cap_arc_dict    All a to b storage arcs (decisions)
    #   event_req_arc_dict      All a to b event requirement arcs (givens)
    #   utility_arc_dict        All arcs originating at the s node or between t nodes (givens)

    storageRoomList = list(storage_cap_dict.keys())
    allRoomList = eventRoomList + storageRoomList
    #print(allRoomList)
    movement_arc_dict = {}
    storage_cap_arc_dict = {}
    event_req_arc_dict = {}
    utility_arc_dict = {}
    itemList = list(item_dict.keys())

    print(allRoomList)

    #Create general set of arcs for all time echelons other than the first and
    #last

    for echelon in echelon_dict:
        for roomI in allRoomList:
            for roomJ in allRoomList:
                for ab in ["a", "b"]:
                    if ab == "a":
                        if roomI == roomJ:
                            if (roomI, echelon) in requirementDict:
                                for requirement in requirementDict[(roomI, echelon)]:
                                    item, qty = requirement[0], requirement[1]
                                    event_req_arc_dict[((roomI, echelon, "a"),(roomJ, echelon, "b"), item)] = (qty, qty, 0)
                            if roomI in storageRoomList:
                                for item in itemList:
                                    ub = int(storage_cap_dict[roomI] / item_dict[item][0]) ## MIGHT CHANGE WITH COMMODITY PAGE (UNITS/PARCEL)
                                    storage_cap_arc_dict[((roomI, echelon, "a"),(roomJ, echelon, "b"), item)] = (0, ub, 0)
                    if ab == "b":
                        if echelon != len(echelon_dict.keys()):
                            for item in itemList:
                                movement_arc_dict[((roomI, echelon, "b"), (roomJ, echelon + 1, "a"), item)] = (0, 100000000, costDict[(roomI, roomJ)])

    #Create set of arcs for inital starting conditions from s node to each room

    for room in allRoomList:
        for item in itemList:
            movement_arc_dict[((room, (len(echelon_dict.keys())), "b"), ("t", (len(echelon_dict.keys()) + 1), "a"), item)] = (0, 1000000000, 0)
            if room in storageRoomList:
                utility_arc_dict[(("s", 0, "a"), (room, 0, "b"), item)] = (inventory_dict[(room, item)], inventory_dict[(room, item)], 0)
            else:
                utility_arc_dict[(("s", 0, "a"), (room, 0, "b"), item)] = (0, 0, 0)

    #Create set of movement arcs for the first movement period

    for roomI in allRoomList:
        for roomJ in allRoomList:
            for item in itemList:
                movement_arc_dict[((roomI, 0, "b"), (roomJ, 1, "a"), item)] = (0, 100000000, costDict[(roomI, roomJ)])

    rooms = len(allRoomList)
    for item in itemList:
        utility_arc_dict[(("t", (len(echelon_dict.keys()) + 1), "a"), ("t", (len(echelon_dict.keys()) + 1), "b"), item)] = (total_inventory_dict[item], total_inventory_dict[item], 0)

    return movement_arc_dict, storage_cap_arc_dict, event_req_arc_dict, utility_arc_dict, allRoomList

def arcDictWriter(arcDict, filename):
    #Writes to csv file
    arcList = []
    for arc in arcDict.keys():
        arcList.append([arc[0][0], arc[0][1], arc[0][2], arc[1][0], arc[1][1],
            arc[1][2], arc[2], arcDict[arc][0], arcDict[arc][1], arcDict[arc][2]])
    with open(filename, "w") as f:
        writer = csv.writer(f)
        writer.writerow(["Xi", "Yi", "Zi", "Xj", "Yj", "Zj", "Item", "Lij", "Uij", "Cij"])
        writer.writerows(arcList)

def excelWriter(arcDict, sheet_name):
    '''Writes arc dictionaries to the excel file. Not in use.'''

    print("Writing " + sheet_name)
    arcList = []
    arcList.append(["Xi", "Yi", "Zi", "Xj", "Yj", "Zj", "Item", "Lij", "Uij", "Cij"])
    for arc in arcDict.keys():
        arcList.append([arc[0][0], arc[0][1], arc[0][2], arc[1][0], arc[1][1],
            arc[1][2], arc[2], arcDict[arc][0], arcDict[arc][1], arcDict[arc][2]])

    book = load_workbook(excel_filename)
    df = pd.DataFrame(arcList)
    writer = pd.ExcelWriter(excel_filename, engine='openpyxl')
    writer.book = book
    writer.sheets = dict((ws.title, ws) for ws in book.worksheets)
    df.to_excel(writer, sheet_name=sheet_name, index=False, index_label=False, header=False)
    writer.save()

def dataFramer(arcDict):
    arcList = []
    for arc in arcDict.keys():
        arcList.append([arc[0][0], arc[0][1], arc[0][2], arc[1][0], arc[1][1],
            arc[1][2], arc[2], arcDict[arc][0], arcDict[arc][1], arcDict[arc][2]])

    df = pd.DataFrame(arcList, columns=["Xi", "Yi", "Zi", "Xj", "Yj", "Zj", "Item", "Lij", "Uij", "Cij"])
    return df

def excelOutputWriter(solution, echelon_dict):
    arcList = []
    arcList.append(["Time", "From Room", "To Room", "Commodity", "Amount"])
    for x in sorted(sorted(sorted(solution, key=lambda k: k[1][0]), key=lambda k: k[0][0]), key=lambda k: k[0][1]): ## Sort First by time, then by room???
        tail, head, commodity = x
        if head[0] != "t":
            if solution[x] > 0:
                if tail[0] != head[0]:
                    print(str(x) + ": " + str(solution[x]))
                    arcList.append([echelon_dict[(tail[1] + 1)], tail[0], head[0], commodity, solution[x]])

    book = load_workbook(excel_filename)
    df = pd.DataFrame(arcList)
    writer = pd.ExcelWriter(excel_filename, engine='openpyxl')
    writer.book = book
    writer.sheets = dict((ws.title, ws) for ws in book.worksheets)
    df.to_excel(writer, sheet_name="Schedule", index=False, index_label=False, header=False)
    writer.save()


def main(args):
    #sup()
    currentStateReader()
def sup():

    cost_dict = costDataReader()
    (inventory_dict, echelon_dict, event_room_list, item_dict, requirement_dict, total_inventory_dict, storage_cap_dict, priority_list, super_event_dict) = currentStateReader()
    movement_arc_dict, storage_cap_arc_dict, event_req_arc_dict, utility_arc_dict, allRoomList = constructor(echelon_dict, event_room_list, item_dict, cost_dict, requirement_dict, inventory_dict, total_inventory_dict, storage_cap_dict)
    # excelWriter(movement_arc_dict, "Movement Arcs")
    # excelWriter(storage_cap_arc_dict, "Storage Room Arcs")
    # excelWriter(event_req_arc_dict, "Event Room Arcs")
    # excelWriter(utility_arc_dict, "Utility Arcs")
    movement_arc_df = dataFramer(movement_arc_dict)
    storage_cap_arc_df = dataFramer(storage_cap_arc_dict)
    event_req_arc_df = dataFramer(event_req_arc_dict)
    utility_arc_df = dataFramer(utility_arc_dict)
    df_dict = {'movement': movement_arc_df, 'storage': storage_cap_arc_df, 'event': event_req_arc_df, 'utility': utility_arc_df, 'storage_rooms': storage_cap_dict, 'commodities': item_dict}
    print("\a")

    return(df_dict, cost_dict, priority_list, echelon_dict)

if __name__ == '__main__':
    import sys
    main(sys.argv)

