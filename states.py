from main import Board
import itertools
from copy import copy
import random

def make_whitelist():
    whitelist = dict()
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
                if j not in whitelist:
                    new_whitelist[j] = j.get_neighbor_boards()
        if len(new_whitelist) == len(whitelist):
            return whitelist
        else:
            whitelist = new_whitelist

# whitelist is a dict of board: {set of allowed moves}
stall_whitelist = make_whitelist()
win_whitelist = make_whitelist()
# blacklist is a set of all won boards or boards that lead to a won board
stall_blacklist = set()
win_blacklist = set()

# create initial blacklist

new_whitelist = stall_whitelist.copy()
for i in stall_whitelist:
    if i.is_won():
        new_whitelist.pop(i)
        stall_blacklist.add(i)
stall_whitelist = new_whitelist

# win variant

new_whitelist = win_whitelist.copy()
for i in win_whitelist:
    if i.is_won() == "o":
        new_whitelist.pop(i)
        win_blacklist.add(i)
win_whitelist = new_whitelist


def pruned_list(thiswhitelist, thisblacklist):
    new_whitelist = thiswhitelist.copy()
    new_blacklist = thisblacklist.copy()
    for i in thiswhitelist:
        if i.is_won():
            continue
        # if o can win, don't let o win by banning this board from happening
        if i.turn == "o":
            for j in thiswhitelist[i]:
                if j in thisblacklist:
                    new_blacklist.add(i)
                    new_whitelist.pop(i)
                    # print(f"{i} moved from whitelist to blacklist due to {j}")
                    break
        # if it's x's turn, ban connected board that could win. ban this board if there are no connected boards.
        else:  # if i.turn == "x"
            new_neighborlist = set()
            for j in thiswhitelist[i]:
                if j not in thisblacklist:
                    new_neighborlist.add(j)
                else:
                    pass
                    # print(f"{j} removed from {i} neighbors")
            new_whitelist[i] = new_neighborlist
            if len(new_neighborlist) == 0:
                new_whitelist.pop(i)
                new_blacklist.add(i)
                # print(f"{i} was added to blacklist because all its neighbors are blacklisted.")

    return new_whitelist, new_blacklist


# prune network
while True:
    new_whitelist, new_blacklist = pruned_list(stall_whitelist, stall_blacklist)
    if stall_whitelist == new_whitelist and stall_blacklist == new_blacklist:
        break
    stall_whitelist = new_whitelist
    stall_blacklist = new_blacklist

while True:
    new_whitelist, new_blacklist = pruned_list(win_whitelist, win_blacklist)
    if win_whitelist == new_whitelist and win_blacklist == new_blacklist:
        break
    win_whitelist = new_whitelist
    win_blacklist = new_blacklist

# # demo time
#
# # play 100 games with each starting board
# wonctr = 0
# tiectr = 0
# for _ in range(100):
#     boards = []
#     boards.append(Board())
#     otherboard = Board()
#     otherboard.advance_turn()
#     boards.append(otherboard)
#     for i in boards:
#         board = i
#         for turncount in range(40):
#             if board.turn == "x":
#                 if board in stall_whitelist:
#                     for potential_board in win_whitelist[board]:
#                         if potential_board in stall_whitelist:
#                             board = potential_board
#                 else:
#                     print("trying to win")
#                     board = list(win_whitelist[board])[0]
#             else:
#                 board = random.choice(list((board.get_neighbor_boards())))
#             print(board)
#             if board.is_won() == "o":
#                 if board in win_blacklist:
#                     print("bad and I know it")
#                 else:
#                     print("bad and im clueless")
#                 print(wonctr)
#                 print(tiectr)
#                 raise Exception("fuck")
#             elif board.is_won() == "x":
#                 wonctr += 1
#                 print("---------------------------------win-----------------------------------")
#                 break
#             elif turncount == 39:
#                 tiectr += 1
#
#
# print(f"woncounter:{wonctr}, tiecounter:{tiectr}")

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

Rather than hardcoding a switch statement though, per project guidelines, we start with a similar network where x's
goal is to win, and then if x can move to a board in the tie whitelist, it does so

'''