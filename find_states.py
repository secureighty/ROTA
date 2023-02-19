from main import Board
import itertools
from copy import copy
import random

# whitelist is a dict of board: {set of allowed moves}
whitelist = dict()
# blacklist is a dict for troubleshooting reasons. board:[list of reasons board is in blacklist]. should be traceable to a won game
blacklist = dict()

# add all boards to whitelist
start = Board()
whitelist[start] = start.get_neighbor_boards()
otherstart = copy(start)
otherstart.advance_turn()
whitelist[otherstart] = otherstart.get_neighbor_boards()
while True:
    new_whitelist = whitelist.copy()
    for i in whitelist:
        for j in i.get_neighbor_boards():
            new_whitelist[j] = j.get_neighbor_boards()
    if len(new_whitelist) == len(whitelist):
        break
    else:
        whitelist = new_whitelist


#create initial blacklist

new_whitelist = whitelist.copy()
for i in whitelist:
    #I wrote paragraphs about this line \/; x is allowed to try to win!
    if i.is_won() == "o":
        new_whitelist.pop(i)
        blacklist[i] = None
whitelist = new_whitelist



def pruned_list(whitelist, blacklist):
    new_whitelist = whitelist.copy()
    new_blacklist = blacklist.copy()
    for i in whitelist:
        # if o can win, don't let o win by banning this board from happening
        if i.turn == "o":
            for j in whitelist[i]:
                if j in blacklist:
                    new_blacklist[i] = [j]
                    new_whitelist.pop(i)
                    break
        # if it's x's turn, a: don't win, and b: don't move such that o can win.
        else: # if i.turn == "x"
            new_neighborlist = set()
            for j in whitelist[i]:
                if j not in blacklist:
                    new_neighborlist.add(j)
            new_whitelist[i] = new_neighborlist
            if len(new_neighborlist) == 0:
                new_whitelist.pop(i)
                new_blacklist[i] = list(i.get_neighbor_boards())

    return new_whitelist, new_blacklist


# prune network
while True:
    new_whitelist, new_blacklist = pruned_list(whitelist, blacklist)
    if whitelist == new_whitelist and blacklist == new_blacklist:
        break
    whitelist = new_whitelist
    blacklist = new_blacklist

# demo time
keys = list(whitelist.keys())
for i in keys:
    if i.placements <3:
        print(i)

# for i in keys:
#     board = i
#     print(f"-----starting board-----")
#     print(board)
#     for j in range(40):
#         if board.turn == "x":
#             board = list(whitelist[board])[0]
#         else:
#             board = random.choice(list(board.get_neighbor_boards()))
#         print(board)
#         print(f"turn {j+1}")

'''
Alright, explanation time for when folks read my code because this realization came at 1 AM on a Friday and I have no
one to tell.

There is no way to assuredly infinitely prolong a game against an AI that wants it to end. I ran network pruning on
the dataset and it prunes the starting board. That's not a bug, as much as I troubleshooted it thinking it was.

However, the goal of any sensible player (or AI) isn't to "end the game". It's to win the game. Even if I'm not trying
to win, I can force moves with winthreat despite never intending to win.

here, x goes first:
x can take the center square for placement 1. No matter where o goes for placement 2, it normalizes to the same square.
we'll put it at the top left. the board now looks like this

o--
-x-
---

For the 3rd placement, x can place next to the o on either side. This has mirror symmetry and also normalizes out, so
we'll just put it up top

ox-
-x-
---

Since o doesn't want to lose, it thinks it has to block x's win, and its hand is forced. It places on the bottom

ox-
-x-
-o-

This boardstate is in the whitelist built in code above, and x can guarantee an infinite game from here. This challenge
is only possible BECAUSE the AI isn't dumb. I think that's pretty neat.
'''