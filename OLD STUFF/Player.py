class Player(object) :
    """
    A player for a specific team with needed stats.
    Class is designed for input of the url for player's advanced stats page.
    """
    def __init__(self,html_link) :
        '''
        Takes in a player's advanced stats page from kenpom.com and breaks it into a usuable class
        '''
        #html_string = get_page(html_link)
        soup = BeautifulSoup(html_link,'html.parser')
        try :
            self.name = soup.find_all('div',attrs={'id' : 'content-header'})[0].find_all('span',attrs={'class' : 'name'})[0].get_text()
        except :
            raise ValueError("No player name found.")
        try :
            self.year_stats = soup.find_all('table',attrs={'id' : 'schedule-table'})[0]
        except :
            raise ValueError("No player stats found.")
        
        stuff2 = player.year_stats.get_text().split('\n')
        stuff = []
        for i in range(len(stuff2)) :
            if stuff2[i] == '' or stuff2[i] == '\xa0' or stuff2[i] == '\xb0' :
                pass
            elif stuff2[i] == '--' :
                stuff.append(0)
                stuff.append(0)
            else :
                stuff.append(stuff2[i])
        stuff = stuff[11:-11]
        columns = ['Date','Opponent','Result','Site','MP','ORtg','%Ps','Pts','2Pt','3Pt','FT','OR','DR','A','TO','Blk','Stl','PF']
        m = len(columns)
        self.stats = {}
        for i in range(m) :
            self.stats[columns[i]] = []
        for i in range(len(stuff)) :
            if str(stuff[i])[-12:] == "Did not play" :
                n = i%m
                for j in range(n,m) :
                    self.stats[columns[j]].append(0)
            else :
                self.stats[columns[i%m]].append(stuff[i])
