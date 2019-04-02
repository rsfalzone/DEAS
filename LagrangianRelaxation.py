import math
import gurobipy

class LangrangianRelaxation():
    def __init__(self, m, iterations=1000, relaxedConstrs=None):
        self.m = m
        self.unrelaxed_obj = m.getObjective()
        self.iterations=iterations
        if relaxedConstrs != None:
            self.relaxedConstrs = relaxedConstrs
            self.lagrangeMults = {key: 0 for key in relaxedConstrs}

    def updateObj():
        penalty = LinExpr()
        for c in self.relaxedConstrs:
            penalty.add(self.relaxedConstrs[c], self.lagrangeMults[c])

        self.objective = LinExpr()
        self.objective.add(self.unrelaxed_obj)
        self.objective.add(penalty)
        return self.objective

    def norm(vector):
        sum = 0
        for x in vector:
            sum += x**2
        return math.sqrt(sum)

    def subgradientAscent():
        i = 1
        self.m.optimize()
        if m.status == GRB.Status.OPTIMAL:
            while i < iterations:
                stepsize = math.sqrt(1/i)
                currLagrangeMults = {}  # Lagrange Mults for the current iteration
                dLagrangeMults = []     # Rate of change vector for Lagrange mults
                for c in self.relaxedConstrs:
                    steepest_ascent = self.relaxedConstrs[c].getValue()
                    currLagrangeMults[c] = self.lagrangeMults[c] + max(stepsize * steepest_ascent, 0)
                    dLagrangeMults.append((currLagrangeMults[c] - self.lagrangeMults[c]) / i)
                if norm(opt_check_vector) > 0 :
                    self.lagrangeMults = currLagrangeMults
                    objective = updateObj(m, unrelaxed_obj, cap_constrs, self.lagrangeMults)
                    self.m.setObjective(objective, GRB.MINIMIZE) # PARAMETER: Gurobi Sense
                    self.m.optimize()
                    ### Add Greedy Algorithm
                    i += 1
                else:
                    iterations = i
                return iterations
        else:
            return m.status
