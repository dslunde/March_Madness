import pandas as pd
import numpy as np
import os
from matplotlib import pyplot as plt

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
        
