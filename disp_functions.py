import pandas as pd
import numpy as np
import os
import operator

default_path = './DATA/'

def team_dict(path,team_name,drop=[]) :
    '''
    Creates a dictionary for a specific team with key as the name of the player
    and the value the dataframe corresponding to said player.
    
    Inputs :
        path (str) - The path to the folder containing the team directory
        team_name (str) - The name of the directory containing team player info
        drop (list) - A list of game numbers to drop (game numbers are reverse chronological)
    
    Output :
        team (dict) - As described above.
    '''
    team = {}
    for dir_path , dir_name , file_names in os.walk(path+team_name) :
        for name in file_names :
            if name[-3:] == 'adj' :
                player_name = name[:-4]
                team[player_name] = pd.read_csv(os.path.join(dir_path,name))
                team[player_name] = team[player_name].drop('Unnamed: 0',axis=1)
                for game in drop :
                    team[player_name] = team[player_name].drop(game)
    return team

def create_avgs(top_players) :
    '''
    Takes a dictionary of the top players and calculates the average statistics described
    
    Inputs :
        top_players (dict) - Dictionary like the return value of team_dict, but filtered
    
    Outputs :
        avgs (dict) - A dictionary of the player's averages
        final_data (array) - The data stacked together
    '''
    # Create avgs dictionary
    avgs = {}
    final_data = []
    # Go through the top players
    for player in top_players.keys() :
        data = top_players[player]
        n = len(data.index)
        # Average out data
        two_pt_att_avg = sum(data['2Pt %Att'])/n
        three_pt_att_avg = sum(data['3Pt %Att'])/n
        ft_tp_att_avg = sum(data['FT %Att'])/n
        points_avg = sum(data['Pts'])/n
        pnts_prev_avg = sum(data['Pnts-Prev'])/n
        two_pt_perc_avg = sum(data['2Pt %'])/n
        three_pt_perc_avg = sum(data['3Pt %'])/n
        ft_perc_avg = sum(data['FT %'])/n
        avgs[player] = [two_pt_perc_avg,three_pt_perc_avg,
                        ft_perc_avg,two_pt_att_avg,three_pt_att_avg,
                        ft_tp_att_avg,points_avg,pnts_prev_avg]
        # First time you have to make it an array
        # Otherwise, append it
        if isinstance(final_data,list) :
            final_data = np.array(avgs[player])
        else :
            final_data = np.vstack((final_data,avgs[player]))
    return avgs, final_data
    
def find_points(team_avgs,threes,twos,fts) :
    '''
    Distributes scoring attempts for a given team
    
    Inputs :
        team_avgs (dict) - Contains averages as created in create_avgs
        threes (int) - Number of 3s to be attempted
        twos (int) - Number of 2s to be attempted
        fts (int) - Number of fts to be attempted
    
    Returns :
        made (dict) : Dictionary with player names as key and a list of :
                        twos made, threes made, fts made
    '''
    made = {}
    max_3s = -1
    max_3s_player = ''
    max_2s = -1
    max_2s_player = ''
    max_ft = -1
    max_ft_player = ''
    # Go through each player and get number
    for player in team_avgs.keys() :
        # Get attempt values
        twos_att = round(twos*team_avgs[player][3])
        threes_att = round(threes*team_avgs[player][4])
        fts_att = round(fts*team_avgs[player][5])
        if twos_att > max_2s :
            max_2s = twos_att
            max_2s_player = player
        if threes_att > max_3s :
            max_3s = threes_att
            max_3s_player = player
        if fts_att > max_ft :
            max_ft = fts_att
            max_ft_player = player
        made[player] = [twos_att,threes_att,fts_att]
    # Correct any rounding errors
    two_error = sum([made[player][0] for player in team_avgs.keys()]) - twos
    three_error = sum([made[player][1] for player in team_avgs.keys()]) - threes
    ft_error = sum([made[player][2] for player in team_avgs.keys()]) - fts
    if two_error != 0 :
        made[max_2s_player][0] -= two_error
    if three_error != 0 :
        made[max_3s_player][1] -= three_error
    if ft_error != 0 :
        made[max_ft_player][2] -= ft_error
    # Calculate how many will actually be made :
    for player in made.keys() :
        made[player][0] = round(made[player][0]*team_avgs[player][0])
        made[player][1] = round(made[player][1]*team_avgs[player][1])
        made[player][2] = round(made[player][2]*team_avgs[player][2])
    return made

def pick_players(team) :
    '''
    From a set of players, grabs the 7 who are most likely to play
    
    Inputs :
        team - A dictionary of team statistics as created by team_dict
    
    Returns :
        players - A dictionary of team statistics that only includes the 7 highest contributors
    '''
    # Counts how many of 2s, 3s, and fts each player generally contributes
    player_counts = {}
    # Get stats for two pointers
    team_two_stats = []
    for player,dataframe in team.items() :
        stats_2s = list(dataframe['2Pt %Att'])
        stats_3s = list(dataframe['3Pt %Att'])
        stats_fts = list(dataframe['FT %Att'])
        count = 0
        if np.mean(stats_2s) > 0 :
            count += 1
        if np.mean(stats_3s) > 0 :
            count += 1
        if np.mean(stats_fts) > 0 :
            count += 1
        player_counts[player] = count
    most_count = sorted(player_counts.items(), key=operator.itemgetter(1))[::-1]
    team_dict = {}
    if len(most_count) <= 7 :
        team_dict = team
    else :
        for i in range(7) :
            player_name = most_count[i][0]
            team_dict[player_name] = team[player_name]
    return team_dict
        
def get_score(team1,team2,year,path=default_path) :
    '''
    Takes in two teams and approximates the score for each team.
    
    Inputs :
        team1 (str) - name of first team (folder name in path)
        team2 (str) - name of second team (folder name in path)
        year (int) - year the team played (as the super directory of team1 and team2)
        path (str) - path to year folder
        
    Outputs :
        team1_final (int) - score for team1
        team2_final (int) - score for team2
    '''
    path += str(year) + '/'
    full_path1 = path + team1 + '/Scouting_Report_csv'
    full_path2 = path + team2 + '/Scouting_Report_csv'
    team1_stats = team_dict(path,team1,drop=[0])
    team2_stats = team_dict(path,team2,drop=[0])
    team1_scout = pd.read_csv(full_path1)
    team1_scout = team1_scout.drop('Unnamed: 0',axis=1)
    team2_scout = pd.read_csv(full_path2)
    team2_scout = team2_scout.drop('Unnamed: 0',axis=1)
    # Find pos len [row 2]
    team1_off_pos_len = float(team1_scout.loc[2]['Offense'])
    team1_def_pos_len = float(team1_scout.loc[2]['Defense'])
    team2_off_pos_len = float(team2_scout.loc[2]['Offense'])
    team2_def_pos_len = float(team2_scout.loc[2]['Defense'])
    # Average one teams offense w/ the other's defense
    team1_offense = (team1_off_pos_len + team2_def_pos_len) / 2
    team2_offense = (team2_off_pos_len + team1_def_pos_len) / 2
    # 40 minutes of gameplay -> 2400 seconds
    # Allot each team time based on tempo [row 1]
    time = 2400
    team1_tempo = float(team1_scout.loc[1]['Offense'])
    team2_tempo = float(team2_scout.loc[1]['Defense'])
    team1_time = team1_tempo / (team1_tempo + team2_tempo) * time
    team2_time = team2_tempo / (team1_tempo + team2_tempo) * time
    # Get number of possessions
    team1_num_poss = round(team1_time / team1_offense)
    team2_num_poss = round(team2_time / team2_offense)
    # Get turnover percentage for each team
    team1_off_turn = float(team1_scout.loc[4]['Offense'])
    team1_def_turn = float(team1_scout.loc[4]['Defense'])
    team2_off_turn = float(team2_scout.loc[4]['Offense'])
    team2_def_turn = float(team2_scout.loc[4]['Defense'])
    # Calculate Predicted turnover rate
    team1_turn_over = (team1_off_turn + team2_def_turn) / 2
    team2_turn_over = (team2_off_turn + team1_def_turn) / 2
    # Get rebound percentage
    team1_off_reb = float(team1_scout.loc[5]['Offense']) / 100
    team1_def_reb = float(team1_scout.loc[5]['Defense']) / 100
    team2_off_reb = float(team2_scout.loc[5]['Offense']) / 100
    team2_def_reb = float(team2_scout.loc[5]['Defense']) / 100
    # Calculate second chances from rebounds
    team1_sec_chance = round((team1_off_reb + 1 - team2_def_reb)*team1_num_poss)
    team2_sec_chance = round((team2_off_reb + 1 - team1_def_reb)*team2_num_poss)
    # Get num of scoring possessions
    # Remove turnover possessions and add in second chances
    team1_scor_poss = round(team1_num_poss*(1 - team1_turn_over / 100)) + team1_sec_chance
    team2_scor_poss = round(team2_num_poss*(1 - team2_turn_over / 100)) + team2_sec_chance
    # Get distribution numbers
    team1_3s = float(team1_scout.loc[15]['Offense']) / 100
    team1_2s = float(team1_scout.loc[16]['Offense']) / 100
    team1_ft = float(team1_scout.loc[17]['Offense']) / 100
    team2_3s = float(team2_scout.loc[15]['Offense']) / 100
    team2_2s = float(team2_scout.loc[16]['Offense']) / 100
    team2_ft = float(team2_scout.loc[17]['Offense']) / 100
    # Get number of possessions for each score type
    team1_3_atts = round(team1_scor_poss * team1_3s)
    team1_2_atts = round(team1_scor_poss * team1_2s)
    team1_1_atts = round(team1_scor_poss * team1_ft)
    team2_3_atts = round(team2_scor_poss * team2_3s)
    team2_2_atts = round(team2_scor_poss * team2_2s)
    team2_1_atts = round(team2_scor_poss * team2_ft)
    # Fix rounding error
    # Since 2 pt shots are most common, add or subtract from there
    team1_error = team1_3_atts + team1_2_atts + team1_1_atts - team1_scor_poss
    if team1_error != 0 :
        team1_2_atts -= team1_error
    team2_error = team2_3_atts + team2_2_atts + team2_1_atts - team2_scor_poss
    if team2_error != 0 :
        team2_2_atts -= team2_error
    # Create dictionaries of top player stats
    team1_top = team1_stats#pick_players(team1_stats)
    team2_top = team2_stats#pick_players(team2_stats)
    # Create avgs dictionary
    team1_avgs, team1_data = create_avgs(team1_top)
    team2_avgs, team2_data = create_avgs(team2_top)
    # Get score distributions and points prevented
    team1_scores = find_points(team1_avgs,team1_3_atts,team1_2_atts,team1_1_atts)
    team2_scores = find_points(team2_avgs,team2_3_atts,team2_2_atts,team2_1_atts)
    # Get final scores
    team1_3 = 3*(sum([team1_scores[player][0] for player in team1_scores.keys()]))
    team1_2 = 2*(sum([team1_scores[player][1] for player in team1_scores.keys()]))
    team1_1 = sum([team1_scores[player][2] for player in team1_scores.keys()])
    team2_3 = 3*(sum([team2_scores[player][0] for player in team2_scores.keys()]))
    team2_2 = 2*(sum([team2_scores[player][1] for player in team2_scores.keys()]))
    team2_1 = sum([team2_scores[player][2] for player in team2_scores.keys()])
    team1_final = team1_3 + team1_2 + team1_1
    team2_final = team2_3 + team2_2 + team2_1
    return team1_final, team2_final