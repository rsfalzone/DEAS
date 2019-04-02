import math
from gurobipy import *

def norm(vector):
    sum = 0
    for x in vector:
        sum += x**2
    return math.sqrt(sum)

class LagrangianRelaxation(object):
    def __init__(self, m, iterations=1000, relaxedConstrs=None):
        self.m = m
        self.mSense = m.ModelSense
        self.unrelaxedObj = m.getObjective()
        self.iterations=iterations
        if relaxedConstrs != None:
            self.relaxedConstrs = relaxedConstrs
            self.lagrangeMults = {key: 0 for key in relaxedConstrs}


    def updateObj(self):
        penalty = LinExpr()
        for c in self.relaxedConstrs:
            penalty.add(self.relaxedConstrs[c], self.lagrangeMults[c])

        self.objective = LinExpr()
        self.objective.add(self.unrelaxedObj)
        self.objective.add(penalty)
        return self.objective

    def greedyAlgorithm(self):
        print("In class")

    def printOutput(self):
        print("Results of Subgradient")
    # if m.status == GRB.Status.OPTIMAL:
    #     print()
    #     print("GUROBI MODEL OUTPUT:")
    #     print('Penalized Objective Value: %g' % m.objVal)
    #     print("Real Objective Value: %g" % unrelaxed_obj.getValue())
    #     print("Iterations of Subgradient Ascent: {}".format(iterations))
    #     print("Movement Arcs:")
    #     for var in arc_vars["Movement Arcs"]:
    #         if arc_vars["Movement Arcs"][var].X > 0:
    #             print("{:<60s}| {:>8.0f}".format(str(var), arc_vars["Movement Arcs"][var].X))
    #     print("\nStorage Room Arcs:")
    #     for var in arc_vars["Storage Room Arcs"]:
    #         if arc_vars["Storage Room Arcs"][var].X > 0:
    #             print("{:<60s}| {:>8.0f}".format(str(var), arc_vars["Storage Room Arcs"][var].X))
    #     print('\nAx-b:')
    #     for s in cap_constrs:
    #         print(str(s) + ": " + str(cap_constrs[s].getValue()))
    # else:
    #     print('No solution;', m.status)

    def subgradientAscent(self):
        self.m.optimize()
        if self.m.status == GRB.Status.OPTIMAL:
            if any(self.relaxedConstrs) and (self.lagrangeMults.keys() == self.relaxedConstrs.keys()):
                i = 1
                while i < self.iterations:
                    stepsize = math.sqrt(1/i)
                    currLagrangeMults = {}  # Lagrange mults for the current iteration
                    dLagrangeMults = []     # Rate of change vector for Lagrange mults
                    for c in self.relaxedConstrs:
                        steepestAscent = self.relaxedConstrs[c].getValue()
                        currLagrangeMults[c] = self.lagrangeMults[c] + max(stepsize * steepestAscent, 0)
                        dLagrangeMults.append((currLagrangeMults[c] - self.lagrangeMults[c]) / i)
                    if norm(dLagrangeMults) > 0 :
                        self.lagrangeMults = currLagrangeMults
                        self.updateObj()
                        self.m.optimize()
                        self.greedyAlgorithm()
                        i += 1
                    else:
                        self.iterations = i
                self.printOutput()
                return self.iterations
            else:
                # No relaxed constraints to penalize
                # Or mismatch between multipliers and constraints
                self.printOutput()
                return m.status
        else:
            return m.status
