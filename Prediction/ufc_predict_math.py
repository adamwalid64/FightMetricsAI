## MMA Math Model

# CREDIT: MMA math model sourced from "The Combat Chronicler" (https://www.youtube.com/watch?v=d6KlvXnHJBo&list=PL58QqkGp8nAxDbF7B8gUx3ODBdPInUq6R&index=10)

# Model Rules --

#   Examine each fighters last 5 fights

#   - Losing:
    #   1. decision loss: -2 pts
    #   2. getting finished: -3 pts

#   - Bonus Categories:
    #   1. Age > 35: -5 pts, -1 extra for each year after
    #   2. Undefeated in UFC: +5pts
    #   3. Undefeated in last 5: +3pts
    #   4. Fighting in country of origin (Excluding US): +5pts


import pandas as pd

# Implemented Math Model --

# Point value dictionaries -

#   - Winning:
    #   1. beating champion: +16 pts
    #   2. beating rank 1: +15 pts
    #   3. beating rank 2: +14 pts
    #   ...
    #   16. beating rank 15: +1 pt

rankWinMap = {
    "chmp": 16,
    "1" : 15,
    "2" : 14,
    "3" : 13,
    "4" : 12,
    "5" : 11,
    "6" : 10,
    "7" : 9,
    "8" : 8,
    "9" : 7,
    "10" : 6,
    "11" : 5,
    "12" : 4,
    "13" : 3,
    "14" : 2,
    "15" : 1              
}



#   - Methods of winning:
winMap = {
    #   1. Finishing an opponent: +5 pts
    "finish" : 5,
    #   2. Finish streak: +1 pt for every finish in the streak
    "finishStreak1x" : 1,
    #   3. More than 2 judges give you every round: +5 pts
    "2judgesWin" : 5
}

#   - Relative Victories:
    #   1. beat someone who beat opponent: +5 pts / 1 pt if loss was avenged by other fighter
        # - +5 additional pts if finish, +1 for each ina  finish streak




def mathmodel(fighter1id, fighter2id):
    pass



