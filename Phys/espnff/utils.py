import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde
from scipy.signal import argrelmin

#____________________
def square_matrix(X):
  '''Squares a matrix'''

  result = np.zeros(shape=(len(X), len(X[0])))

  # iterate through rows of X
  for i in range(len(X)):
    # iterate through columns of X
    for j in range(len(X[0])):
      # iterate through rows of X
      for k in range(len(X)):
        result[i][j] += X[i][k] * X[k][j]
        
  return result


#_____________________
def weigh_matrix(X, w):
  '''multiplies matrix by weight'''
  
  result = np.zeros(shape=(len(X), len(X[0])))

  for i in range(len(X)):
    # iterate through columns
    for j in range(len(X[0])):
      result[i][j] = X[i][j] * w

  return result


#____________________
def add_matrix(X, Y):
  '''Adds two matrices'''

  result = np.zeros(shape=(len(X), len(X[0])))

  for i in range(len(X)):
    # iterate through columns
    for j in range(len(X[0])):
      result[i][j] = X[i][j] + Y[i][j]

  return result


#________________________
def two_step_dominance(X, teams):
  '''Calculates result of two step dominance formula, with weights specified'''
  
  w_sq = 0.25 # weigh squared matrix
  w_l  = 0.75 # weigh linear matrix
  
  sq   = weigh_matrix( square_matrix(X), w_sq )
  l    = weigh_matrix( X, w_l )
  
  matrix = add_matrix( sq, l)
 
  for row,team in zip(matrix,teams):
    r_sum = sum(row)
    team.dom_rank = r_sum

  # normalize avg to 1.
  dom_list = [x.dom_rank for x in teams]
  avg_dom = float(sum(dom_list))/len(dom_list)

  for t in teams:
    t.dom_rank = t.dom_rank * 1./avg_dom


#_______________________________________
def power_points(teams, week):
  '''Returns list of power points      
     weigh dominance matrix rank, 
           lsq rank
           colley rank
           avg score, 
           min+max,
           sos,
           streak,
           luck'''
  
  for team in teams:
    dom       = float(team.dom_rank)
    lsq       = float(team.lsq_rank)
    colley    = float(team.colley_rank)
    sos       = float(team.sos)
    luck      = 1./float(team.luck)
    streak    = float(team.streak)*int(team.streak_sgn)
    avg_score = sum(team.scores[:week]) / float(week)
    min_max   = 0.5*float(min(team.scores[:week])) + 0.5*float(max(team.scores[:week]))
    
    # Only winning streaks longer than 1 game count
    streak = 0.25*streak if streak > 1 else 0.
    consistency = float(min_max)/avg_score

    #power =  0.35*lsq + 0.22*dom + 0.1*colley +  0.10*sos + 0.10*luck + 0.08*consistency + 0.05*streak
    power =   0.21*dom + 0.18*lsq + 0.18*colley + 0.15*team.awp  + 0.10*sos + 0.08*luck + 0.05*consistency + 0.05*streak
    
    team.power_rank = 100*np.tanh(power/0.5)
  

#________________________________________________
def get_tiers(teams, week, bw = 0.1, show=False):
  '''Set the tiers based on overall ranking, 
     optionally send bandwidth '''
  
  # store rankings locally 
  r = []	
  for t in teams:
    r.append(t.power_rank) 

  # Calculate Kernal Density Estimation
  #x_grid = np.linspace(min(r),max(r),len(r))
  x_grid = np.linspace(min(r)-10.,max(r)+10.,len(r)*10)
  #x_grid = np.linspace(0,100,10*len(r))
  kde = gaussian_kde(r,bw_method=bw)
   
  # Make plot
  f2 = plt.figure(figsize=(10,6))
  plt.plot(x_grid,kde(x_grid))
  if show == True:
    plt.show()
  # create directory if it doesn't exist yet
  out_name = 'output/Week%s/tiers.png'%week
  os.makedirs(os.path.dirname(out_name), exist_ok=True)
  f2.savefig(out_name)
  plt.close()

  # Find minima to define tiers (spaced at least +/- 6 apart)
  minima = x_grid[ argrelmin( kde(x_grid),order=6 )[0] ]
  s_min = sorted(minima, reverse=True)
  tier = 1
  for t in teams:
    # lowest tier
    if tier > len(s_min):
      tier += 0
    # if rank below current minima, create new tier
    elif t.power_rank < s_min[tier-1]: 
      tier += 1
    # save tier
    t.tier = tier


#________________________________________
def save_ranks(teams, week, getPrev=False):
  '''Saves rankings to file
     optionally read previous rankings'''
  
  teams_sorted = sorted(teams, key=lambda x: x.power_rank, reverse=True)
  
  # Save Power rankings teamId:rank 
  new_name = 'output/week%s/ranks_power.txt'%(week)
  os.makedirs(os.path.dirname(new_name), exist_ok=True)
  f_new = open(new_name,'w')
  # sorted by power rankings
  for i,t in enumerate(teams_sorted):
    f_new.write('%s:%s\n'%(t.teamId,i+1))
  f_new.close()

  # Save espn overall rankings teamId:rank 
  teams_sorted_overall = sorted(teams, key=lambda x: (x.wins, x.pointsFor), reverse=True)
  new_name = 'output/week%s/ranks_overall.txt'%(week)
  os.makedirs(os.path.dirname(new_name), exist_ok=True)
  f_new = open(new_name,'w')
  # sorted by espn overall rankings
  for i,t in enumerate(teams_sorted_overall):
    f_new.write('%s:%s\n'%(t.teamId,i+1))
    t.rank_overall = (i+1)
  f_new.close()

  # Compare to previous rankings
  if getPrev == False:
    return
  
  # Get Previous power rankings 
  old_name = 'output/week%s/ranks_power.txt'%(week-1)
  os.makedirs(os.path.dirname(old_name), exist_ok=True)
  f_old = open(old_name,'r')
  for line in f_old:
    team_rank = (line.strip()).split(':')
    t_id = team_rank[0]
    t_rk = team_rank[1]
    # sorted by this weeks power rankings
    for t in teams_sorted:
      if int(t.teamId) == int(t_id):
        t.prev_rank = t_rk
  f_old.close()
  
  # Get Previous overall rankings 
  old_name = 'output/week%s/ranks_overall.txt'%(week-1)
  os.makedirs(os.path.dirname(old_name), exist_ok=True)
  f_old = open(old_name,'r')
  for line in f_old:
    team_rank = (line.strip()).split(':')
    t_id = team_rank[0]
    t_rk = team_rank[1]
    # sorted by this weeks overall
    for t in teams_sorted_overall:
      if int(t.teamId) == int(t_id):
        t.prev_rank_overall = t_rk
  f_old.close()


