import numpy as np

#__________________________
def calc_luck(teams, week):
  '''Calculates luck index
     factors: awp vs wp
              opponents score vs avg'''
  
  teams_sorted = sorted(teams, key=lambda x: x.teamId, reverse=False)

  for t in teams_sorted:
    o_avg_over_score = 0.
    # calc ratio of opp score over their avg score
    for w, o in enumerate(t.schedule[:week]):
      o_avg = float(sum(o.scores[:week]))/float(week)
      ratio = o_avg/float(o.scores[w])
      o_avg_over_score += ratio

    # add ratio of your win pct to awg
    record = float(t.wins) / float(t.wins + t.losses)
    luck_ind = 0.5*float(o_avg_over_score)/week + 0.5*(0.01+float(record))/(0.01+float(t.awp))
    t.luck = luck_ind


#________________________
def calc_sos(teams, week):
  '''Calculate strength of schedule based on opponents lsq ranking'''
  
  teams_sorted = sorted(teams, key=lambda x: x.teamId, reverse=False)
  
  # Find avg of opponents ranking
  for t in teams_sorted:
    rank_i = 0
    for w, o in enumerate(t.schedule[:week]):
      rank_i += 100*(o.lsq_rank**2.37)
    t.sos = rank_i/float(week)

  # Find avg sos
  sos_list = [x.sos for x in teams_sorted ]
  avg_sos = float(sum(sos_list))/len(sos_list)
  
  # normalize so avg = 1
  for t in teams_sorted:
    #t.sos = np.sqrt(t.sos * 1./avg_sos)
    t.sos = t.sos * 1./avg_sos

#________________________
def calc_wins_losses(teams, week):
  '''Calculates:
        points for
        ponits against
        wins
        losses
        streak
        aggregate wins
        aggregate losses
        aggregate winning percentage'''
  teams_sorted = sorted(teams, key=lambda x: x.teamId, reverse=False)
  
  for t in teams_sorted:
    aw_i   = 0.
    al_i   = 0.
    pf     = 0.
    pa     = 0.
    wins   = 0
    losses = 0
    st     = 0
    st_sgn = 1 
    
    for w, (s,w_o) in enumerate(zip(t.scores[:week],t.schedule[:week]) ):
      
      # points for, against, wins, losses, streak, sign
      pf += s
      pa += w_o.scores[w]
      if s > w_o.scores[w]:
        wins += 1
        if st_sgn == -1:
          st_sgn = 1
          st = 1
        else:
          st += 1
      else:
        losses += 1
        if st_sgn == 1:
          st_sgn = -1
          st = 1
        else:
          st += 1

      # aggregate wins/losses
      for o in teams:
        if o.teamId != t.teamId:
          if s > o.scores[w]:
            aw_i += 1
          else:
            al_i += 1
    t.awp            = float(aw_i)/(float(aw_i)+float(al_i))
    t.awins          = aw_i
    t.alosses        = al_i
    t.pointsFor      = pf
    t.pointsAgainst  = pa
    t.wins           = wins
    t.losses         = losses
    t.streak         = st
    t.streak_sgn     = st_sgn

