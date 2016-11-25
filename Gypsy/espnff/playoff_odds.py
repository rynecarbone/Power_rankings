import numpy as np
from scipy.stats import norm

#_____________________________
def calc_playoffs(teams, week):
  '''Calculates playoff odds for each team
     Change reg_season to number of weeks
     Change spots to number of spots available (1 division)'''
  
  # See how many teams left:
  reg_season = 12
  spots      = 4
  eliminated = []
  in_hunt    = []
  team_wins  = []
  new_teams  = [] # 0: owner, 1: teamId 2: scores, 3: wins, 4: schedule, 5: gaus

  # Store wins and fit params
  # Sort teams by current standings
  sorted_teams = sorted(teams, key=lambda x: (x.wins,sum(x.scores[:week])), reverse= True )
  for t in sorted_teams:
    team_wins.append(t.wins) # for determining who is eliminated
    # Save relevant information in a smaller teams list
    temp_new = []
    temp_new.append(t.owner)
    temp_new.append(t.teamName) 
    temp_new.append(t.scores)   # list of scores for season
    temp_new.append(t.wins)     # number of wins
    temp_new.append(t.schedule) # list of opponent team names
    temp_new.append(norm.fit(t.scores[:week])) # fit gaus to team scores
    new_teams.append(temp_new)
  
  # Find who is eliminated (too many games back)
  for t in new_teams:
    if (team_wins[spots-1]-t[3]) > (reg_season-week):
      eliminated.append(t)
    else:
      in_hunt.append(t)

  # Print who is eliminated, who is in
  print('\nEliminated:')
  for e in eliminated: print(e[0])
  print('\nIn the hunt')
  for h in in_hunt:    print(h[0])
  
  # Simulate the rest of the season 
  n_games   = 1000000  # number of simulated games
  scores    = simulate( new_teams, n_games, week)

  # Calculate how many times each team makes playoffs
  wins      = []
  pointsFor = []
  for i,t in enumerate(new_teams):
    team_wins      = []
    team_pointsFor = []
    # Iterate through each simulated game
    for g,s in enumerate(scores[i]):
      team_pointsFor.append( sum(t[2])+s )
      # Iterate through other teams to find opponent
      for j,op in enumerate(new_teams):
        if op[1] == t[4][week].teamName:
          t_win = 1 if s > scores[j][g] else 0
          team_wins.append(t[3]+t_win)
    # Append list of simulated, total points for, and total wins      
    pointsFor.append(team_pointsFor)
    wins.append(team_wins)

  # With list of simulated number of wins, points for, find how
  # many times each team makes the playoffs
  calc_odds(new_teams, wins, pointsFor, n_games)
  return


#_______________________________________
def simulate( new_teams, n_games, week ):
  '''Simulate scores for each team, for n_games'''
  
  scores = []
  # For each team, generate a score, from their points distribution function
  for t in new_teams:
    scores.append(np.random.normal(t[5][0], t[5][1], n_games))
  
  return scores  


#_________________________________________________
def calc_odds(new_teams, wins, pointsFor, n_games):
  '''Find fraction of seasons where each team makes playoffs'''

  playoffs = np.zeros(len(new_teams))

  # Loop through each team 
  for i_t in range(len(new_teams)):
    # Loop through each simulated game
    for g in range(len(wins[i_t])):
      teams_beat = 0 # in overall standings
      # Loop through other teams 
      for j_t in range(len(new_teams)):
        if i_t != j_t: 
          # More wins than team_j
          if wins[i_t][g] > wins[j_t][g]:
            teams_beat += 1
          # Same wins, but win points tie breaker against team_j
          elif wins[i_t][g] == wins[j_t][g] and pointsFor[i_t][g] > pointsFor[j_t][g]:
            teams_beat += 1
      # Have to beat at least 6 teams to be in the playoffs      
      if teams_beat >= 6:
        playoffs[i_t] += 1

  # Print odds for this week:
  print('\nThis Week')
  for i_t,t in enumerate(new_teams):
    win_prob = 100.*( sum(wins[i_t]) - t[3]*n_games )/n_games
    print('%s %.3f%%'%(t[0],win_prob))
  # Print each teams odds
  print('\nPlayoff Odds')
  for t_p,t in zip(playoffs, new_teams):
    print('%s %.3f%%'%(t[0], 100.*t_p/n_games))








