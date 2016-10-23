import os
import numpy as np


#__________________
def get_arrow(i, j):
  '''Create glyphicon chevron
     i: previous rank
     j: current rank'''
  
  snu = '  <span class="text-success">'
  snd = '  <span class="text-danger">'
  ns = '</span>'
  up = '<span class="glyphicon glyphicon-chevron-up"></span>'
  dn = '<span class="glyphicon glyphicon-chevron-down"></span>'
  
  arrow = ''
  change = int(i) - int(j)
  if change > 0:
    arrow += snu + up + ' %d'%np.fabs(change) + ns
  elif change < 0:
    arrow += snd + dn + ' %d'%np.fabs(change) + ns

  return arrow


#________________________________________
def make_progress_bar(title, value, rank):
  '''Makes progress bar with label and value'''
  tr = '<tr>'
  td = '<td>'
  p  = '<p class="h4">'
  dp = '<div class="progress">'
  db = '<div class="progress-bar %s" role="progressbar" aria-value-now="%d" aria-valuemin="0" aria-valuemax="100" style="width: %d%%">'
  sp = '<span>'
  ps = '</span>'
  vd = '</div>'
  pp = '</p>'
  dt = '</td>'
  rt = '</tr>'
  s  = 'progress-bar-success'
  w  = 'progress-bar-warning'
  d  = 'progress-bar-danger'

  progress_bar = tr + td + p + title + pp + dp
  if value < 33.33: progress_bar += db%(d,value,value)
  elif value < 66.66: progress_bar += db%(w,value,value)
  else:  progress_bar += db%(s,value,value)
  if "FAAB" in title:
    progress_bar += sp+'$%d of $100'%(value) + ps #how to retreive max value?
  else:
    progress_bar += sp+'(%s)'%rank + ps
  progress_bar += vd + vd +dt + rt
  return progress_bar  


#_______________________________
def make_game_log(t, week):
  '''Returns table body for game log'''
  tr = '<tr>'
  td = '<td>'
  dt = '</td>'
  rt = '</tr>'
  win = '<span class="text-success">W</span>'
  loss = '<span class="text-danger">L</span>'
  game_log = ''

  for w,o in enumerate(t.schedule[:week]):
    own   = 'Meff Shulz' if ('Jeff' in o.owner) else o.owner # maybe set earlier with own function
    
    game_log += tr + td + '%s'%(w+1) + dt
    game_log += td + '%s'%(o.teamName) + dt
    game_log += td + '%s'%own + dt
    game_log += td + '%.2f &mdash; %.2f'%(float(o.scores[w]),float(t.scores[w])) + dt
    game_log += td + (win if float(t.scores[w]) > float(o.scores[w]) else loss ) + dt + rt

  return game_log


#________________________________
def make_power_table(teams,week):
  '''Creates simple table with rankings'''
  tr = '<tr>'
  td = '<td>'
  dt = '</td>'
  rt = '</tr>'
  table = ''
  
  for i,t in enumerate(sorted(teams, key=lambda x: x.power_rank, reverse=True)):
    arrow = get_arrow(int(t.prev_rank), int(i+1))
    own   = 'Meff Shulz' if ('Jeff' in t.owner) else t.owner # make earlier, same as above

    table += tr
    table += td + str(i+1) + dt
    table += td + own.title() + arrow + dt
    table += td + '%s-%s'%(t.wins,t.losses) + dt
    table += td + "{0:.3f}".format(float(t.power_rank)) + dt
    table += td + "{0:.3f}".format(float(t.lsq_rank)) + dt
    table += td + "{0:.3f}".format(float(t.dom_rank)) + dt
    table += td + "{0:.3f}".format(float(t.colley_rank)) + dt
    table += td + "{0:.3f}".format(float(t.sos)) + dt
    table += td + "{0:.3f}".format(float(t.luck)) + dt
    table += td + str(t.tier) + dt
    table += rt

  return table


#__________________________________
def get_index(teams_sorted, teamId):
  '''Return ranking from ordered list of teamId'''

  for i,t in enumerate(teams_sorted):
    if t.teamId == teamId:
      return i+1


#_______________________________
def make_teams_page(teams, week):
  '''Make teams page with stats, standings, game log, radar plots'''

  # Ordinal makes numbers like 2nd, 3rd, 4th etc 
  ordinal   = lambda n: "%d%s" % (n,"tsnrhtdd"[(n/10%10!=1)*(n%10<4)*n%10::4]) # own function?
  stock_url = 'http://www.suttonsilver.co.uk/wp-content/uploads/blog-stock-03.jpg'  
 
  # Make team page for each owner
  for i,t in enumerate(sorted(teams, key=lambda x: x.power_rank, reverse=True)):
    # Hack for first name, and team logo FIXME
    own   = 'Meff Shulz' if 'Jeff' in t.owner else t.owner # set earlier?
    first = own.split()[0].title()
    logo  = t.logoUrl if len(t.logoUrl) > 4 else stock_url
    if ('espncdn' in logo) and ('jrschulz09' in logo):
      logo = stock_url

    # create output and directory if it doesn't exist
    out_name = 'output/%s/index.html'%first
    os.makedirs(os.path.dirname(out_name), exist_ok=True)

    template = open('template/player.html','r')
    f_out    = open(out_name,'w')

    # replace with info
    for line in template:
      line = line.replace('INSERTOWNER',own)
      line = line.replace('INSERTWEEK','week%s'%week)
      line = line.replace('IMAGELINK', logo)
      line = line.replace('TEAMNAME',t.teamName)
      line = line.replace('TEAMABBR',t.teamAbbrev)
      line = line.replace('INSERTRECORD','%s-%s'%(t.wins,t.losses))
      line = line.replace('INSERTACQUISITIONS','%d'%int(t.trans))
      line = line.replace('INSERTTRADES','%d'%int(t.trades))
      line = line.replace('INSERTWAIVER','%s'%ordinal(t.waiver))
      line = line.replace('OVERALLRANK','%s <small>%s</small>'%(ordinal(t.rank_overall), 
                                                                get_arrow(int(t.prev_rank_overall),
                                                                int(t.rank_overall)) ) )
      line = line.replace('POWERRANK','%s <small>%s</small>'%(ordinal(int(i+1)), 
                                                              get_arrow(int(t.prev_rank),
                                                              int(i+1)) ))
      line = line.replace('AGGREGATEPCT','%.3f <small>(%d-%d)</small>'%(t.awp,t.awins,t.alosses))
      line = line.replace('RADARPLOT','radar_%s.png'%t.teamId)
      if 'INSERT_TPF_PB' in line:
        pf_sort = sorted(teams, key=lambda x: x.pointsFor, reverse=True)
        pf_rank = get_index(pf_sort, t.teamId)
        line = make_progress_bar('Total Points For: %.2f'%float(t.pointsFor), #fix any number of teams
                                  110-100.*float(pf_rank)/10., 
                                  ordinal(int(pf_rank))  )
      elif 'INSERT_TPA_PB' in line:
        pa_sort = sorted(teams, key=lambda x: x.pointsAgainst, reverse=True)
        pa_rank = get_index(pa_sort, t.teamId)
        line = make_progress_bar('Total Points Against: %.2f'%float(t.pointsAgainst), 
                                  110-100.*float(pa_rank)/10.,  
                                  ordinal(int(pa_rank))  )
      elif 'INSERT_HS_PB' in line:
        hs_sort = sorted(teams, key=lambda x: max(x.scores[:week]), reverse=True)
        hs_rank = get_index(hs_sort, t.teamId)
        line = make_progress_bar('High Score: %.2f'%max(t.scores[:week]), 
                                  110-100.*float(hs_rank)/10., 
                                  ordinal(int(hs_rank))  )
      elif 'INSERT_LS_PB' in line:
        ls_sort = sorted(teams, key=lambda x: min(x.scores[:week]), reverse=True)
        ls_rank = get_index(ls_sort, t.teamId)
        line = make_progress_bar('Low Score: %.2f'%min(t.scores[:week]), 
                                  110-100.*float(ls_rank)/10., 
                                  ordinal(int(ls_rank))  )
      elif 'INSERT_FAAB_PB' in line:
        line = make_progress_bar('FAAB Remaining', float(100-t.faab) ,int(100-t.faab) ) #fix for any league
      elif 'INSERTTABLEBODY' in line:
        line = make_game_log(t, week)
      # after checking all substitutions, finally write each line
      f_out.write(line)
    # close file  
    f_out.close()
    template.close()


#________________________________
def make_power_page(teams, week):
  '''Produces power rankings page'''

  out_name = 'output/power.html'
  os.makedirs(os.path.dirname(out_name), exist_ok=True)

  template = open('template/power.html','r')
  f_out    = open(out_name,'w')

  for line in template:
    if 'INSERT WEEK' in line:
      line = line.replace('INSERT WEEK','Week %s'%week)
    elif 'INSERT TABLE' in line:
      line = make_power_table(teams,week)
    f_out.write(line)

  f_out.close()
  template.close()


#________________________________
def make_about_page(week):
  '''Produces about page, updating week for power rankings'''  
  
  # create directory if doesn't already exist
  out_name = 'output/about/index.html'
  os.makedirs(os.path.dirname(out_name), exist_ok=True)
  
  template = open('template/about.html','r')
  f_out    = open(out_name,'w')
  
  # copy lines
  for line in template:
    f_out.write(line)
  
  # close files
  f_out.close()
  template.close()


#_________________________
def make_web(teams, week):
  '''Makes power rankings page
           team summary page
           about page'''

  make_power_page(teams, week)
  make_teams_page(teams, week)
  make_about_page(week)

