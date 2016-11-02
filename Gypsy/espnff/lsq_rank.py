import os
from scipy.optimize import lsq_linear
from matplotlib import pylab as pl
import numpy as np

#_____________________
def calc_Rg(S_h, S_a):
  '''Returns R_g given home and away scores '''

  B_w    = 40.#40
  B_r    = 40.#40
  dS_max = 20.#20

  dS_ha = float(S_h - S_a)
  dS_t  = dS_max*np.tanh(dS_ha/(3.*dS_max))
  S_w   = S_h if dS_ha > 0 else S_a
  p_m   = 1   if dS_ha > 0 else -1

  R_g   = p_m*B_w + dS_t + B_r*(dS_ha/S_w) 
  return R_g


#____________________________
def calc_Ng_list(teams, week):
  '''Returns vector of games with home and away team id
     and home and away scores:
     ( home_id away_id home_score away_score) '''
  
  teams_sorted = sorted(teams, key=lambda x: x.teamId, reverse=False)
  N_g = []
  
  for w in range(week):
    for t in teams_sorted:
      if t.home_away[w] == 0:
        opp = t.schedule[w]
        score = t.scores[w]
        opp_score = opp.scores[w]
        N_g.append([t.teamId, opp.teamId, score, opp_score])
  
  return N_g


#_____________________________
def calc_sig_g(prev_rank,N_g):
  '''Returns Sigma_g for each game given previous iterations rankings'''
  
  beta_w  = 2.2
  alpha_w = (max(prev_rank) - min(prev_rank))/np.log(beta_w*beta_w) 
  
  sig_g = []
  for g in N_g:
    h_g = g[0]-1 # home teamId
    a_g = g[1]-1 # away teamId
    w_g = np.exp( -np.fabs(prev_rank[h_g]-prev_rank[a_g])/alpha_w )
    sig_g.append(1./np.sqrt(w_g))
  
  return sig_g



#_________________________________________________
def rank_pass(teams, week, passN=0, prev_rank=[] ):
  '''Returns list of rankings  using linear chi2
    for pass 0, set passN = 0, all weights are 1
    for all others, set passN = n and send prev_rank '''
  
  teams_sorted = sorted(teams, key=lambda x: x.teamId, reverse=False)
  
  A   = []  # g x t array (games x teams)
  b   = []  # g list of game results R_g
  N_g = calc_Ng_list(teams, week)  # list of games with home/away ids

  # error of game measurement w = 1/sig^2
  if passN == 0:
    sig_g = np.ones(len(N_g)) # equal weight first iteration
  else:
    sig_g = calc_sig_g(prev_rank, N_g) 
  
  # Loop over games & home/away team ids
  for g, h_a in enumerate(N_g):
    row_g = [] # row for game g in A matrix
    # loop over teams
    for team in teams_sorted:
      if team.teamId == h_a[0]:
        r_tg = 1./sig_g[g] # home team
      elif team.teamId == h_a[1]:
        r_tg = -1./sig_g[g] #away
      else:
        r_tg = 0 #not in game
      row_g.append(r_tg)
    # add row to A matrix
    R_g = calc_Rg(h_a[2],h_a[3]) # send( score_home, score_away)
    b.append(R_g/sig_g[g])
    A.append(row_g)
  
  rank = lsq_linear(A,b,bounds=(30,130))#,lsq_solver='exact')

  if rank.success == False:
    print('WARNING:\t%s'%rank.message)
  
  for i,r in enumerate(rank.x):
    teams_sorted[i].lsq_rank = r 

  return rank.x


#________________________________________
def get_lsq_rank(teams, week, show=False):
  '''Main function to calculate and plot lsq ranking'''

  rank_p = []
  
  # Pass 0 has weight = 1
  rank_p.append( rank_pass(teams,week,passN=0) )
  
  # Iterate with previous ranks as input, recalculate weight
  for p in range(0,100):
    rank_p.append( rank_pass(teams, week, passN=p, prev_rank=rank_p[p-1]))
  
  # plot result of iterations
  plot_save_rank(rank_p, teams, week, show=False)


#______________________
def plot_save_rank(rank_p,teams,week,show=False):
  '''Plot the ranking iterations for each team'''

  # Plot iterations
  fig = pl.figure(figsize=(10,6))
  t_ranks = []
  x = np.linspace(0,len(rank_p)-1, len(rank_p))
  for t in range(len(teams)):
    temp =[]
    for p in rank_p:
      temp.append(p[t])
    t_ranks.append(temp)
    pl.plot(x,t_ranks[t])

  # Save plot
  if show == True:
    pl.show()

  # make dir if it doesn't exist already
  out_name = 'output/week%s/lsq_iter_rankings.png'%week
  os.makedirs(os.path.dirname(out_name), exist_ok=True)
  fig.savefig(out_name)
  pl.close()

  # Average last 70 elements to get final rank
  for i,t in enumerate(t_ranks):
    mean = sum(t[70:])/float(len(t[70:]))
    teams[i].lsq_rank = np.tanh( mean/75.) # save the rank again (100 approximately is 1.)

