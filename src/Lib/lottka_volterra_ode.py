#!/usr/bin/env python3 
"""
This file contains an ODE solver for the Lottka-Volterra
reaction system

         F + R -> 2R   [k1]
         R + W -> 2W   [k2]
         W     -> nil  [k3]
"""

# we import scipy for the ODE solver 
# and numpy for the convenient linear ranges
from scipy.integrate import odeint
import numpy as np


##################################################################
# initial conditions and variables
##################################################################

# initial conditions
k1 = 20        
k2 = 3.0      
k3 = 20 
R0 = 5       # initial concentration of rabbits (e.g. rabbits per
             # square mile)
W0 = 5       # initial concentration of wolfs


# info about integration interval
start = 0
end   = 10.0
step  = 1e-4


###################################################################
# helper functions
###################################################################

# NOTE: y = [F(t),W(t)]
# hence y[0] = F(t) and y[1] = W(t)
def tri_mol_equilibrium(y,t):
    """ 
    This function describes the ODE system for the
    Lottka-Volterra
    """

    dF = k1 * y[0] - k2 * y[0] * y[1]
    dW = k1 * y[0] * y[1] - k3 * y[1]

    return [dF,dW]



def open_output_files():
    """
    This function opens the output files and returns file
    handles to each.
    """

    outfile_A = open("R.dat","w")
    outfile_B = open("W.dat","w")

    return [outfile_A, outfile_B]



def write_data_to_output(fileHandles, data):
    """
    This function writes all data to the output files.
    """

    counter = 0
    for timepoint in data:
        for item in range(0,len(fileHandles)):
            fileHandles[item].write("%f %f\n" % ((step * counter), 
                                                 (timepoint[item])))
        counter += 1



def close_output_files(fileHandles):
    """
    This function closes all output files.
    """

    for i in range(0,len(fileHandles)):
        fileHandles[i].close()



#######################################################################
# start of main simulation
#######################################################################

def main():

    # The below call to odeint does the main work; it integrates 
    # our ode with odeint (pretty powerful, uses
    # netlib's odepack, can handle both stiff and non-stiff
    # ODE's).
    # The simplest way to call odeint is to provide the 
    # function defining the ODE, a (vector) of initial
    # conditions, and a list of timepoint at which the results
    # are supposed to be evaluated. We use numpy's arange object 
    # which creates a list of the form (start,end,step).
    # We could of course also just type (0,1e-6,2e-6,3e-6,...,0.001)
    # or whatever.
    result = odeint(tri_mol_equilibrium, [R0,W0], np.arange(start,end,step))

    # save the results
    fileHandles = open_output_files()
    write_data_to_output(fileHandles, result)
    close_output_files(fileHandles)



# entry point for execution
if __name__ == "__main__":
    main()
