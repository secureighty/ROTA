from copy import deepcopy, copy


class BoardNode:
    def __init__(self, status="-"):
        self.linked_nodes = []
        self.opposite_node = None
        self.status = status

    def link(self, node):
        self.linked_nodes += [node]

    def link_opposite(self, node):
        self.opposite_node = node

    def __str__(self):
        return self.status

    def __repr__(self):
        return self.status

    def set_status(self, status):
        self.status = status


def tob3(char):
    if char == "x":
        return "1"
    if char == "o":
        return "0"
    else:
        return "2"


def artob3(arr):
    result = ""
    for i in arr:
        result += tob3(i)
    return int(result, 3)


def board_dif(this, other):
    result = 0
    for i, j in zip(this.edge_nodes + [this.center], other.edge_nodes + [other.center]):
        if i.status != j.status:
            result += 1
            if i.status == "o" or j.status == "o":
                result += 10
    return result


class Board:
    def __init__(self, init_array=None):
        if init_array == None:
            self.center = BoardNode()
            self.edge_nodes = [BoardNode() for i in range(8)]
        else:
            init_array = list(init_array)
            self.center = BoardNode(init_array[4])
            self.edge_nodes = [BoardNode(init_array[0])]
            self.edge_nodes.append(BoardNode(init_array[1]))
            self.edge_nodes.append(BoardNode(init_array[2]))
            self.edge_nodes.append(BoardNode(init_array[5]))
            self.edge_nodes.append(BoardNode(init_array[8]))
            self.edge_nodes.append(BoardNode(init_array[7]))
            self.edge_nodes.append(BoardNode(init_array[6]))
            self.edge_nodes.append(BoardNode(init_array[3]))
        for i in range(8):
            # link edge nodes
            self.edge_nodes[i].link(self.edge_nodes[(i + 1) % 8])
            self.edge_nodes[i].link(self.edge_nodes[(i - 1) % 8])
            # link opposite node in case center node is also owned by same player
            self.edge_nodes[i].link_opposite(self.edge_nodes[(i + 4) % 8])

        self.nodes = self.edge_nodes + [self.center]
        self.turn = "x"
        self.placements = 0

    def flipped_board(self):
        result = copy(self)
        result.edge_nodes = result.edge_nodes[::-1]
        return result

    def rotations(self):
        result = []
        edge_nodes_mut = self.edge_nodes.copy()
        for i in range(len(self.edge_nodes)):
            edge_nodes_mut = edge_nodes_mut[1:] + [edge_nodes_mut[0]]
            board = copy(self)
            board.edge_nodes = edge_nodes_mut.copy()
            board.nodes = board.edge_nodes + [board.center]
            result += [board]
        return result

    def normalize(self):
        configs = dict()
        configlist = []
        configlist += self.rotations() + self.flipped_board().rotations()
        for i in configlist:
            configs[hash(i)] = i
        self.edge_nodes = configs[min(configs.keys())].edge_nodes

    def get_move_from_normalized_board(self, prev_denormalized_board):
        def map_state_to_api(num):
            match num:
                case 0:
                    return 1
                case 1:
                    return 2
                case 2:
                    return 3
                case 3:
                    return 6
                case 4:
                    return 9
                case 5:
                    return 8
                case 6:
                    return 7
                case 7:
                    return 4
                case 8:
                    return 5
        configs = dict()
        for i in self.rotations() + self.flipped_board().rotations():
            configs[board_dif(i, prev_denormalized_board)] = i

        if self.placements < 6:
            denormalized_board = configs[1]
        else:
            try:
                denormalized_board = configs[2]
            except KeyError:
                denormalized_board = configs[1]

        start = None
        end = None
        for i in range(8):
            prevstat = prev_denormalized_board.edge_nodes[i].status
            thisstat = denormalized_board.edge_nodes[i].status
            if prevstat != thisstat:
                if prevstat == "-":
                    end = map_state_to_api(i)
                else:
                    start = map_state_to_api(i)
        prevstat = prev_denormalized_board.center.status
        thisstat = denormalized_board.center.status
        if prevstat != thisstat:
            if prevstat == "-":
                end = map_state_to_api(8)
            else:
                start = map_state_to_api(8)

        return start, end

    def __str__(self):
        return f"\n{self.edge_nodes[0]} {self.edge_nodes[1]} {self.edge_nodes[2]}\n" \
               f"{self.edge_nodes[7]} {self.center} {self.edge_nodes[3]}\n" \
               f"{self.edge_nodes[6]} {self.edge_nodes[5]} {self.edge_nodes[4]}\n" \
               f"next:{self.turn}\n"

    def __hash__(self):
        result = tob3(self.turn)
        for i in self.edge_nodes:
            result += tob3(i.status)
        result += tob3(self.center.status)
        return int(result, 3)

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __lt__(self, other):
        return hash(self) < hash(other)

    def __gt__(self, other):
        return hash(self) > hash(other)

    def __repr__(self):
        return str(self)

    def advance_turn(self, normalize=True):
        self.turn = ("o" if self.turn == "x" else "x")
        if normalize:
            self.normalize()

    def is_won(self):
        for i in self.edge_nodes:
            if i.status != "-":
                # this is less efficient than just 2 eq checks, but I like it cuz it's more scaleable
                # win by edge
                if len(set([node.status for node in i.linked_nodes] + [i.status])) == 1:
                    return i.status
                # win through center
                if len({i.status, i.opposite_node.status, self.center.status}) == 1:
                    return i.status
        return False

    def move(self, start_index, end_index, player, normalize=True):
        start = self.nodes[start_index]
        end = self.nodes[end_index]
        if end not in start.linked_nodes and start not in end.linked_nodes and end is not self.center and start is not self.center:
            print(hash(end))
            print(hash(self.center))
            print(end == self.center)
            raise Exception("spot not accessible")
        if end.status != "-":
            raise Exception("spot is taken")
        if start.status != player:
            print(start.status, player, self.turn)
            raise Exception("not your piece")
        start.set_status("-")
        end.set_status(player)
        self.advance_turn(normalize)
        return self

    def get_neighbor_boards(self, normalize=True):
        neighbors = set()
        if self.placements < 6:
            for node in self.nodes:
                if node.status == "-":
                    x = deepcopy(self)
                    x.place(self.nodes.index(node), self.turn, normalize)
                    neighbors.add(x)

        else:
            for piece in self.nodes:
                if piece.status == self.turn:
                    for blank_space in self.nodes:
                        if blank_space.status == "-":
                            if blank_space in piece.linked_nodes or blank_space is self.center or piece is self.center:
                                x = deepcopy(self)
                                x.move(self.nodes.index(piece), self.nodes.index(blank_space), self.turn)
                                # x.neighbors = None
                                neighbors.add(x)
        return neighbors

    def place(self, node_num, player, normalize=True):
        if node_num == 8:
            node = self.center
        else:
            node = self.nodes[node_num]
        if node.status == "-":
            node.set_status(player)
        else:
            raise Exception(f"spot {node_num} is taken by {self.nodes[node_num]}")
        self.placements += 1
        self.advance_turn(normalize)
