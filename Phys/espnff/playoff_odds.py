import numpy as np
from scipy.stats import norm

#_____________________________
def calc_playoffs(teams, week):
  '''Calculates playoff odds for each team
     Change reg_season to number of weeks
     Change spots to number of spots available (1 division)'''
  
  # See how many teams left:
  reg_season  = 13
  n_divisions = 4
  n_spots       = 6
  new_teams   = [] # 0: owner, 1: teamId 2: scores, 3: wins, 4: schedule, 5: gaus, 6: division id

  # Store wins and fit params
  # Sort teams by current standings
  sorted_teams = sorted(teams, key=lambda x: (x.wins,sum(x.scores[:week])), reverse= True )
  for t in sorted_teams:
    # Save relevant information in a smaller teams list
    temp_new = []
    temp_new.append(t.owner)
    temp_new.append(t.teamName) 
    temp_new.append(t.scores)   # list of scores for season
    temp_new.append(t.wins)     # number of wins
    temp_new.append(t.schedule) # list of opponent team names
    temp_new.append(norm.fit(t.scores[:week])) # fit gaus to team scores
    temp_new.append(t.divisionId) # division id
    new_teams.append(temp_new)
  
  # Simulate the rest of the season 
  n_games   = 1000000  # number of simulated games per week
  n_weeks   = reg_season - week
  wins      = []
  pointsFor = []
  # Save current wins and points For 
  for i,t in enumerate(new_teams):
    wins.append( np.tile(t[3], n_games) )
    pointsFor.append( np.tile(sum(t[2][:week]), n_games) )

  # Simulate rest of season
  for w in range(n_weeks):
    scores = simulate( new_teams, n_games)
    # Calculate which games each team wins
    for i,t in enumerate(new_teams):
      team_wins      = np.tile(0,n_games)
      team_pointsFor = np.tile(0,n_games)
      # Iterate through each simulated game for team i
      for g,s in enumerate(scores[i]):
        team_pointsFor[g] += s 
        # Iterate through other teams to find opponent
        for j,op in enumerate(new_teams):
          if op[1] == t[4][week+w].teamName:
            team_wins[g] += 1 if s > scores[j][g] else 0
            
      # Append list of simulated total points for, and total wins      
      pointsFor[i] += team_pointsFor
      wins[i]      += team_wins

  # Print mean wins and pointsFor for end of season
  for w,p,t in zip(wins, pointsFor, new_teams):
    print('%s wins: %.3f pointsFor: %.3f'%(t[0],np.mean(w),np.mean(p)))
  
  # With list of simulated number of wins, points for, find how
  # many times each team makes the playoffs
  calc_odds(new_teams, wins, pointsFor, n_games, n_divisions, n_spots)
  return


#_______________________________________
def simulate( new_teams, n_games):
  '''Simulate scores for each team, for n_games'''
  
  scores = []
  # For each team, generate a score, from their points distribution function
  for t in new_teams:
    scores.append(np.random.normal(t[5][0], t[5][1], n_games))
  
  return scores  


#______________________________________________________________________
def calc_odds(new_teams, wins, pointsFor, n_games, n_divisions, n_spots):
  '''Find fraction of seasons where each team makes playoffs'''

  top_div     = np.zeros(len(new_teams))
  wildcard    = np.zeros(len(new_teams))
  playoffs    = np.zeros(len(new_teams))
  div_winner  = [[-1]*n_games for i in range(n_divisions) ]
  
  # Find division winners
  for i_t in range(len(new_teams)):
    for g in range(len(wins[i_t])):
      # Find div winners
      t_div = new_teams[i_t][6]
      if div_winner[t_div][g] < 0:
        div_winner[t_div][g] = i_t
      elif wins[i_t][g] > wins[div_winner[t_div][g]][g]:
        div_winner[t_div][g] = i_t
      elif wins[i_t][g] == wins[div_winner[t_div][g]][g] and pointsFor[i_t][g] > pointsFor[div_winner[t_div][g]][g]:
        div_winner[t_div][g] = i_t

  # Find wild cards 
  for i_t in range(len(new_teams)):
    # Loop through each simulated game
    for g in range(len(wins[i_t])):
      teams_beat    = 0  # in wildcard standings
      g_div_winners = [] # div winners for this simulation
      for d in range(n_divisions):
        g_div_winners.append(div_winner[d][g])
      # Wins division, so made playoffs
      if i_t in g_div_winners:
        playoffs[i_t] += 1 # make playoff
        top_div[i_t]  += 1 # win division
      else:
        # Loop through other teams 
        for j_t in range(len(new_teams)):
          if i_t == j_t or j_t in g_div_winners: 
            continue # skip self and division winners
          else:
            # More wins than team_j
            if wins[i_t][g] > wins[j_t][g]:
              teams_beat += 1
            # Same wins, but win points tie breaker against team_j
            elif wins[i_t][g] == wins[j_t][g] and pointsFor[i_t][g] > pointsFor[j_t][g]:
              teams_beat += 1
        # Have to beat at least 6 teams to be in the playoffs      
        if teams_beat >= (len(new_teams)-n_spots):
          playoffs[i_t] += 1 # made playoffs
          wildcard[i_t] += 1 # made wildcard

  # Print each teams odds
  print('\nPlayoff Odds')
  for t_p,t,t_d,t_w in zip(playoffs, new_teams, top_div, wildcard):
    print('%20s\tOverall: %8.3f%%\tDivision Winner: %8.3f%%\tWildcard: %8.3f%%'%(t[0], 100.*t_p/n_games, 100.*t_d/n_games, 100.*t_w/n_games))








