import requests
from .utils import two_step_dominance

#___________________
class League(object):
  '''Creates a League instance for Public ESPN league'''

  def __init__(self, league_id, year):
    self.league_id = league_id
    self.year = year
    self.ENDPOINT = "http://games.espn.com/ffl/api/v2/"
    self.teams = []
    self._fetch_teams()

  def __repr__(self):
    return 'League %s, %s Season' % (self.league_id, self.year)

  def _fetch_teams(self):
    '''Fetch teams in league'''
    url = "%sleagueSettings?leagueId=%s&seasonId=%s"
    r = requests.get(url % (self.ENDPOINT, self.league_id, self.year))
    data = r.json()
    teams = data['leaguesettings']['teams']

    for team in teams:
      self.teams.append(Team(teams[team]))

    # replace opponentIds in schedule with team instances
    for team in self.teams:
      for week, matchup in enumerate(team.schedule):
        for opponent in self.teams:
          if matchup == opponent.teamId:
            team.schedule[week] = opponent

    # calculate margin of victory
    for team in self.teams:
      for week, opponent in enumerate(team.schedule):
        mov = team.scores[week] - opponent.scores[week]
        team.mov.append(mov)

  def calc_dom(self, week):
    '''Return dominance matrix rankings for any week'''
    # calculate win for every week
    win_matrix = []
    teams_sorted = sorted(self.teams, key=lambda x: x.teamId, reverse=False)
    
    for team in teams_sorted:
      wins = [0]*len(teams_sorted)
      for i,(mov,opponent) in enumerate(zip(team.mov[:week], team.schedule[:week])):
        opp = int(opponent.teamId)-1
        if mov > 0:
          wins[opp]+= 1 + (0.5)*i/float(week) # last game weighted more
      win_matrix.append(wins)
      
    # save dominance score
    two_step_dominance(win_matrix, teams_sorted)

#_________________
class Team(object):
  '''Teams are part of the league'''
  
  def __init__(self, data):
    self.teamId        = data['teamId']
    self.teamAbbrev    = data['teamAbbrev']
    self.teamName      = "%s %s"%(data['teamLocation'], data['teamNickname'])
    self.owner         = "%s %s"%(data['owners'][0]['firstName'], data['owners'][0]['lastName'])
    self.logoUrl       = data['owners'][0]['photoUrl'] if 'logoUrl' not in data.keys() else data['logoUrl']
    self.divisionId    = data['division']['divisionId']
    self.divisionName  = data['division']['divisionName']
    self.faab          = data['teamTransactions']['acquisitionBudgetSpent']
    self.trans         = data['teamTransactions']['overallAcquisitionTotal']
    self.trades        = data['teamTransactions']['trades']
    self.waiver        = data['waiverRank']
    self.wins          = data['record']['overallWins']   # recomputed later based on week
    self.losses        = data['record']['overallLosses'] # recomputed later based on week
    self.streak        = data['record']['streakLength']  # recomputed later based on week
    self.streak_sgn    = 1 if data['record']['streakType'] == 1  else -1
    self.pointsFor     = data['record']['pointsFor']     # recomputed later based on week
    self.pointsAgainst = data['record']['pointsAgainst'] # recomputed later based on week
    self.schedule      = []
    self.home_away     = [] # 0: home 1: away
    self.scores        = []
    self.mov           = []
    self.awp           = 0.
    self.awins         = 0.
    self.alosses       = 0.
    self.sos           = 1.
    self.power_rank    = 1.
    self.dom_rank      = 1.
    self.colley_rank   = 1.
    self.lsq_rank      = 1.
    self.luck          = 1.
    self.tier          = 1.
    self.rank_overall  = 1.
    self.prev_rank     = 1.
    self.prev_rank_overall= 1.
    self._fetch_schedule(data)
      
  def __repr__(self):
    return 'Team %s' % self.teamName

  def _dump_info(self):
    for attr in sorted(self.__dict__):
      if hasattr(self, attr):
        print('%20s:\t%s'%(attr, getattr(self,attr)))
  
  def _fetch_schedule(self, data):
    '''Fetch schedule and scores for team'''
    matchups = data['scheduleItems']
    for matchup in matchups:
      if matchup['matchups'][0]['isBye'] == False:
        if matchup['matchups'][0]['awayTeamId'] == self.teamId:
          score = matchup['matchups'][0]['awayTeamScores'][0]
          opponentId = matchup['matchups'][0]['homeTeamId']
          home_away = 1 # 1 for away
        else:
          score = matchup['matchups'][0]['homeTeamScores'][0]
          opponentId = matchup['matchups'][0]['awayTeamId']
          home_away = 0 # 0 for home
      else:
        score = matchup['matchups'][0]['homeTeamScores'][0]
        opponentId = matchup['matchups'][0]['homeTeamId']
        print('WARNING, BYE WEEK...Check!') #FIXME what to do here?
      
      self.scores.append(score)
      self.schedule.append(opponentId)
      self.home_away.append(home_away)
