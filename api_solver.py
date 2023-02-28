import json

from main import Board
from states import stall_whitelist, win_whitelist
from interface import *
from copy import copy


def next_move(board):
    thisboard = copy(board)
    thisboard.normalize()
    if thisboard in stall_whitelist:
        for potential_board in stall_whitelist[thisboard]:
            if potential_board in stall_whitelist:
                return potential_board
    else:
        return list(win_whitelist[thisboard])[0]

def get_board_from_result(web_result):

    webtext = json.loads(web_result.text)
    print(webtext)
    if webtext["status"] == "fail":
        raise Exception("fuck")
    result = webtext["data"]
    try:
        print(result["hash"])
        exit()
    except:
        return Board(result["board"].replace("p", "x").replace("c", "o"))

def main():
    board = get_board_from_result(new())
    while True:
        for i in range(36):
            print(board)
            print(next_move(board))
            move_to_make = next_move(board).get_move_from_normalized_board(board)
            if move_to_make[0] is None:
                board = get_board_from_result(place(move_to_make[1]))
            else:
                board = get_board_from_result(move(move_to_make[0], move_to_make[1]))
        board = get_board_from_result(next())

main()