#!/usr/bin/env python3
from espnff import League
from espnff import Radar as R
from espnff import colley as C
from espnff import lsq_rank as lr
from espnff import str_sched as ss
from espnff import Web as W
from espnff.utils import power_points,get_tiers,save_ranks
from espnff import power_plot as P
from espnff import playoff_odds as po

#________________________
if __name__ == "__main__":
  
  league_name = "Gypsymen Fantasy"
  league_id   = 292301
  year        = 2016
  week        = 12
  
  # Retrieve league info 
  l = League(league_id, year) 
  teams = sorted(l.teams, key=lambda x: x.teamId, reverse=False) 
  
  # Recalculate wins etc
  ss.calc_wins_losses(teams, week)
  
 # po.calc_playoffs(teams, week)
 # exit()

  # Get dominace rankings  
  l.calc_dom(week)
  
  # Calculate rankings by least squares
  lr.get_lsq_rank(teams, week, show=False)

  # Calculate Colley rankings 
  C.get_colley_rank(teams, week, printM=False)
  
  # Calculate SOS
  ss.calc_sos(teams, week)
  
  # Calculate Luck index
  ss.calc_luck(teams, week) 
 
  # Calculate final power ranking
  power_points(teams, week)

  # Calculate change from previous week
  save_ranks(teams, week, getPrev=True)

  # Get tiers
  r_sorted = sorted(teams, key=lambda x: x.power_rank, reverse = True)
  get_tiers(r_sorted, week, bw = 0.09, show=False)
  
  # Print out results (sorted by lsq) 
  print('\n\n%20s  #\tPower\tLSQ\t2SD\tColley\tSOS\tAWP\tLuck\tTier\tChange'%('Name'))
  for i,t in enumerate(r_sorted):
    print('%20s  %d\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%d\t%d'%
          (t.owner, i, float(t.power_rank), float(t.lsq_rank), float(t.dom_rank),  
           float(t.colley_rank), float(t.sos),float(t.awp),float(t.luck),int(t.tier),int(t.prev_rank)-(i+1)))
  
  # Make power rankings plot
  P.make_power_plot(teams,week)
  
  # Make website template
  W.make_web(teams, week, league_id, league_name)
  
  # Make radar plots
  for t in teams:
    #if 'Meff' in t.owner:
    #  t._dump_info()
    R.make_radar(t, week)

