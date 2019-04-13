import csv

filename = "output.csv"

def getData(solution):
    echelons = {}
    for x in solution:
        if solution[x] > 0:
            i, j, com = x
            roomi, ti, di = i
            roomj, tj, dj = j
            if roomi[0] == "S":
                if ti > 0:
                    if ti in echelons:
                        if roomi in echelons[ti]:
                            if com in echelons[ti][roomi]:
                                echelons[ti][roomi][com] += solution[x]
                            else:
                                echelons[ti][roomi][com] = solution[x]
                        else:
                            echelons[ti][roomi] = {com: solution[x]}
                    else:
                        echelons[ti] = {roomi:{com: solution[x]}}
    return echelons

def CSVwriter(d):
    with open(filename, newline="") as f:
        write.writerow(['Echelon', 'Storage Room', 'Commodity', 'Quantity'])
        writer = csv.writer(f)
        for t in d:
            for r in d[t]:
                for c in d[t][r]:
                    writer.writerow([t,r,c,d[t][r][c]])

def sup2(solution):
    d = getData(solution)
    CSVwriter(d)

