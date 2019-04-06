import csv

SROOMS = ["SA0","SA1C","SA1DD","SA3C","SA3D","SA3G","SA3M","SA4A","SA4B",
        "SB2-1","SB2-2","SB2-3","SB2-4","SB2-5","SB2-6","SB3-1","SB3-10",
        "SB3-11","SB3-12","SB3-13","SB3-2","SB3-3","SB3-4","SB3-5","SB3-6",
        "SB3-7","SB3-8","SB3-9","SB4-1","SB4-10","SB4-2","SB4-3","SB4-4",
        "SB4-5","SB4-6","SB4-7","SB4-8","SB4-9","SB5-1","SB5-2","SC1-1",
        "SC2-2","SC2-3","SC2-4","SC2-5","SC3-1","SC3-2","SC3-3","SC3-4",
        "SC3-5","SC3-6","SC3-7","SC2-1"]
with open('StartingStateBryanv2 - Starting State.csv', newline='') as fin:
    reader = csv.reader(fin)
    with open("Inventories.csv", "w", newline='') as fout:
        writer = csv.writer(fout)
        header = next(reader)
        with open("Commodities.csv", "w", newline="") as fout2:
            writer2 = csv.writer(fout2)
            writer2.writerow(["Commodity","Units/Parcel","Volume/Parcel","Priority"])
            for i in range(1,len(header)):
                writer2.writerow([header[i],1,1,i])
        for row in reader:
            if row[0][0] not in ["S", "T"]:
                for i in range(1,len(header)):
                    writer.writerow([row[0], header[i], row[i]])
        for r in SROOMS:
            for i in range(1,len(header)):
                writer.writerow([r, header[i], 0])

