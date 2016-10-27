# coding=utf-8
import numpy as np
from scipy.linalg import solve

#_________________________
def get_colley_rank(teams, week, printM=False):
  '''Calculates rating using Colley matrix'''
  # C_ij = -n_ij  (number of games team i played team j
  # C_ii = 2 + n_i (total games team i played)
  # b_i  = 1 + 0.5(w_i - l_i) (can introduce weights as well)
  
  C = [] # array N_teams x N_teams
  b = [] # vector with weighted record

  # define matrix with ascending teamId..easier to debug
  teams_sorted = sorted(teams, key=lambda x: x.teamId, reverse=False)
  for team in teams_sorted:
    row_i = []
    for j in range(len(teams_sorted)):
      # how many games team i played
      if j == int(team.teamId)-1:
        row_i.append(2 + week)
      # how many games team i played team j
      else:
        n_ij = 0
        for opponent in team.schedule[:week]:
          if int(opponent.teamId)-1 == j:
            n_ij += 1
        row_i.append( -n_ij )
    C.append(row_i)
    b.append(1+0.5*(int(team.wins)-int(team.losses))) # add weight? 
  
  # solve matrix 
  res = solve(C,b)
  if printM:
    print_colley(C,b,res)
  for i,team in enumerate(teams_sorted):
    team.colley_rank = res[i]


#______________________
def print_colley(C,b,res):
  '''Print the Colley matrix'''
  
  print('\nColley matrix: \nC r = b') 
  for i,r in enumerate(C):
    s = ''
    for x in r:
      s += '%s  '%x
    s += '\t%s\t'%res[i]
    if i == 5:
      s += '='
    print("%s\t%s"%(s,b[i]))
