playercount=80
def create_player_card_list():#creates list of number of players for refrence in check_player_angle
    global playercount,player_cards
    player_cards=[]
    for i in range(playercount):
        player_cards.append(i+1)

def check_player_angle(): #finds the optimal angle for each players hand based on player count for card generaiton e.i: playercount=4 has player 1 at 90 degree angle player 2 at 180...
    global player_cards,intial_angle
    intial_angle=360/len(player_cards)
    intial_angle2=0
    intial_angle2=intial_angle
    for i in range (len(player_cards)):
        if i+1==player_cards[i]:
            print(intial_angle2)
            intial_angle2=intial_angle+intial_angle2
create_player_card_list()
check_player_angle()