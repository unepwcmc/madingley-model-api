# -*- coding: utf-8 -*-
"""
Created on Tue Feb 18 22:06:38 2020

@author: MikeHa
"""
import numpy as np
import math
import random

##
# ncell = Integer number of grid cells
# herbivore_masses = vector of real numbers for the bodymasses of herbivores
# carnivore_masses = vector of real numbers for the bodymasses of carnivores
##

BMS = np.exp(np.arange(math.log(0.1),math.log(1000),0.08)).tolist()
#bms = [0.1,0.2,0.5,1,2,5,10,12,15,20,30,40,50,60,70,80,90,100]

cell_area = 1000
ncells = 3*3

def ReturnInitialGrid():
  herbivore_biomasses = [[]]
  herbivore_abundances = [[]]
  carnivore_biomasses = [[]]
  carnivore_abundances = [[]]
  primary_producer_biomass = None

  bodymasses = BMS
  
  herbivore_biomasses = [[GetInitialBiomass(m,len(bodymasses)) for m in bodymasses] for c in range(ncells)] 
  herbivore_abundances = [[herbivore_biomasses[c][m]/bodymasses[m] for m in range(len(bodymasses))] for c in range(ncells)]
  
  carnivore_biomasses = [[GetInitialBiomass(m,len(bodymasses)) for m in bodymasses] for c in range(ncells)] 
  carnivore_abundances = [[carnivore_biomasses[c][m]/bodymasses[m] for m in range(len(bodymasses))] for c in range(ncells)]

  primary_producer_biomass = [0 for c in range(ncells)]

  return {
    'herbivore_biomasses': herbivore_biomasses,
    'herbivore_abundances': herbivore_abundances,
    'carnivore_biomasses': carnivore_biomasses,
    'carnivore_abundances': carnivore_abundances,
    'primary_producer_biomass': primary_producer_biomass
  }

def GetInitialBiomass(m,nm):
  return (3300 / nm) * 30 * np.random.normal(loc = 0.5,scale = 0.01)*math.pow(0.6, (math.log10(m*0.01))) * (cell_area)

