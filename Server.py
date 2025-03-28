import socket
import select
import pickle
from random import randint
import sqlite3
from Constants import *


class Unit:
    def __init__(self, img, x=0, y=0, level=0):
        self.img = img
        self.x = x
        self.y = y
        self.level = level

    def scout_move(self):
        """
        :param self: A level 2 unit
        :return: The function checks whether the unit's move is legal and
        returns a matching boolean value
        """

        global game
        global player
        global mouse_x
        global mouse_y

        high_index = -1
        low_index = -1
        if player == 1:
            board = game.player1_units
            enemy_board = game.player2_units
        else:
            board = game.player2_units
            enemy_board = game.player1_units

        if mouse_x == self.x and mouse_y != self.y:
            for i in xrange(len(y_list)):
                if self.y == y_list[i] or mouse_y == y_list[i]:
                    if low_index == -1:
                        low_index = i
                    else:
                        high_index = i - 1
            while low_index != high_index:
                for unit in board:
                    if (unit.x == mouse_x and unit.y == y_list[high_index]) or \
                            ((mouse_x == x_list[2] or mouse_x == x_list[3] or mouse_x == x_list[6] or mouse_x == x_list[7])
                             and (y_list[high_index] == y_list[4] or y_list[high_index] == y_list[5])):
                        return False
                for unit in enemy_board:
                    if change_x(unit.x) == mouse_x and change_y(unit.y) == y_list[high_index]:
                        return False
                high_index -= 1
            return True
        elif mouse_y == self.y and mouse_x != self.x:
            for i in xrange(len(x_list)):
                if self.x == x_list[i] or mouse_x == x_list[i]:
                    if low_index == -1:
                        low_index = i
                    else:
                        high_index = i - 1
            while low_index != high_index:
                for unit in board:
                    if (unit.y == mouse_y and unit.x == x_list[high_index]) or \
                            ((x_list[high_index] == x_list[2] or x_list[high_index] == x_list[3] or
                              x_list[high_index] == x_list[6] or x_list[high_index] == x_list[7])
                             and (mouse_y == y_list[4] or mouse_y == y_list[5])):
                        return False
                for unit in enemy_board:
                    if change_y(unit.y) == mouse_y and change_x(unit.x) == x_list[high_index]:
                        return False
                high_index -= 1
            return True

        return False


class Game:
    def __init__(self, player1=None, player2=None, username1=None, username2=None):
        self.turn = 1
        self.next_turn = 2
        self.player1 = player1
        self.player2 = player2
        self.username1 = username1
        self.username2 = username2

        self.player1_units = []
        self.player1_units.append(Unit(img=Sarri, x=flag_start, y=0, level=0))
        self.player1_units.append(Unit(img=Kepa, x=x_list[0], y=0, level=1))
        for unit in xrange(8):
            self.player1_units.append(Unit(img=Alonso, x=x_list[1], y=0, level=2))
        for unit in xrange(5):
            self.player1_units.append(Unit(img=Pedro, x=x_list[2], y=0, level=3))
        for unit in xrange(4):
            self.player1_units.append(Unit(img=Rudiger, x=x_list[3], y=0, level=4))
        for unit in xrange(4):
            self.player1_units.append(Unit(img=Ruben, x=x_list[4], y=0, level=5))
        for unit in xrange(4):
            self.player1_units.append(Unit(img=Azpi, x=x_list[5], y=0, level=6))
        for unit in xrange(3):
            self.player1_units.append(Unit(img=Willian, x=x_list[6], y=0, level=7))
        for unit in xrange(2):
            self.player1_units.append(Unit(img=Luiz, x=x_list[7], y=0, level=8))
        self.player1_units.append(Unit(img=Kante, x=x_list[8], y=0, level=9))
        self.player1_units.append(Unit(img=Hazard, x=x_list[9], y=0, level=10))
        for unit in xrange(6):
            self.player1_units.append(Unit(img=Dean, x=bomb_start, y=0, level=11))

        self.player2_units = []
        self.player2_units.append(Unit(img=Emery, x=flag_start, y=0, level=0))
        self.player2_units.append(Unit(img=Leno, x=x_list[0], y=0, level=1))
        for unit in xrange(8):
            self.player2_units.append(Unit(img=Bellerin, x=x_list[1], y=0, level=2))
        for unit in xrange(5):
            self.player2_units.append(Unit(img=Xhaka, x=x_list[2], y=0, level=3))
        for unit in xrange(4):
            self.player2_units.append(Unit(img=Mustafi, x=x_list[3], y=0, level=4))
        for unit in xrange(4):
            self.player2_units.append(Unit(img=Iwobi, x=x_list[4], y=0, level=5))
        for unit in xrange(4):
            self.player2_units.append(Unit(img=Koscielny, x=x_list[5], y=0, level=6))
        for unit in xrange(3):
            self.player2_units.append(Unit(img=Laca, x=x_list[6], y=0, level=7))
        for unit in xrange(2):
            self.player2_units.append(Unit(img=Sokratis, x=x_list[7], y=0, level=8))
        self.player2_units.append(Unit(img=Torreira, x=x_list[8], y=0, level=9))
        self.player2_units.append(Unit(img=Auba, x=x_list[9], y=0, level=10))
        for unit in xrange(6):
            self.player2_units.append(Unit(img=Dean, x=bomb_start, y=0, level=11))

        self.quit = False
        self.placing = True
        self.placing1 = True
        self.placing2 = True

        self.player1_press_index = None
        self.player2_press_index = None

        self.change = None


def update_scores(username1, username2, update1=0, update2=0):
    """
    :param username1: The username of player 1.
    :param username2:  The username of player 2.
    :param update1: The value that should be added/decreased to the score of player 1.
    :param update2: The value that should be added/decreased to the score of player 2.
    This function updates the scores of the players.
    """

    conn = sqlite3.connect(file_name)
    conn.text_factory = str
    c = conn.cursor()
    c.execute("SELECT score FROM users WHERE username=?", (username1,))
    score1 = c.fetchone()[0] + update1
    c.execute("SELECT score FROM users WHERE username=?", (username2,))
    score2 = c.fetchone()[0] + update2
    c.execute("UPDATE users SET score=? WHERE username=?", (score1, username1))
    c.execute("UPDATE users SET score=? WHERE username=?", (score2, username2))
    conn.commit()
    conn.close()


def minimum_score(username):
    """
    :param username: The username of the player.
    :return: Boolean that represents whether the score is the minimum or not.
    """

    conn = sqlite3.connect(file_name)
    conn.text_factory = str
    c = conn.cursor()
    c.execute("SELECT score FROM users WHERE username=?", (username,))
    score = c.fetchone()[0]
    conn.close()
    if score == 0:
        return True
    return False


def enemy_turn(change):
    """
    :param change: A string that represents the graphic changes that need to be made.
    :return: An updated string that fits to the opponent's screen.
    """

    change = change.split(" ")
    last_x = int(change[0])
    last_y = int(change[1])
    x = int(change[2])
    y = int(change[3])
    if len(change) == 4:
        return str(change_x(last_x)) + " " + str(change_y(last_y)) + " " + str(change_x(x)) + " " + str(change_y(y))
    elif len(change) == 6:
        return str(change_x(last_x)) + " " + str(change_y(last_y)) + " " + str(change_x(x)) + " " + str(change_y(y)) + " " + str(change[4]) + " " + str(change[5])
    else:
        return str(change_x(last_x)) + " " + str(change_y(last_y)) + " " + str(change_x(x)) + " " + str(change_y(y)) + " " + str(change[4]) + " " + str(change[5]) + " " + str(change[6])


def change_x(x):
    """
    :param x: X value
    :return: Mirror X value
    """

    for index in xrange(len(x_list)):
        if x == x_list[index]:
            x = x_list[9-index]
            return x


def change_y(y):
    """
    :param y: Y value
    :return: Mirror Y value
    """

    for index in xrange(len(y_list)):
        if y == y_list[index]:
            y = y_list[9-index]
            return y


if __name__ == "__main__":

    conn = sqlite3.connect(file_name)
    conn.text_factory = str
    c = conn.cursor()
    try:
        c.execute("CREATE TABLE users (username text, password text, score integer)")
        conn.commit()
        print "new"
    except:
        pass
    c.execute("SELECT username FROM users")
    print "users:"
    print c.fetchall()
    conn.close()

    server_socket = socket.socket()
    server_socket.bind(('0.0.0.0', server_port))
    server_socket.listen(5)

    open_client_sockets = []
    online_users = []
    games = []

    while True:
        rlist, wlist, xlist = select.select([server_socket] + open_client_sockets, open_client_sockets, [])
        for current_socket in rlist:
            if current_socket is server_socket:
                (new_socket, address) = server_socket.accept()
                open_client_sockets.append(new_socket)

            else:
                player = None
                found = False
                no_game = False
                game_index = 0

                for game in games:
                    if game.player1 == current_socket:
                        player = 1
                        found = True
                        break
                    elif game.player2 == current_socket:
                        player = 2
                        found = True
                        break
                    game_index += 1

                if player is None:
                    try:
                        data = current_socket.recv(1024)
                        no_game = True
                    except:
                        data = ""
                else:
                    try:
                        data = current_socket.recv(1024)
                        game = games[game_index]
                    except:
                        data = ""
                info = data.split(" ")

                if data == "":
                    if found:
                        games[game_index].quit = True
                    if player == 1:
                        if games[game_index].player2 is None:
                            games.remove(games[game_index])
                    elif player == 2:
                        if games[game_index].player1 is None:
                            games.remove(games[game_index])
                    for user in online_users:
                        if user[1] == current_socket:
                            online_users.remove(user)
                            break
                    open_client_sockets.remove(current_socket)
                    current_socket.close()
                    print("closed")

                elif data == "leave":
                    games.remove(game)

                elif data == "quit?":
                    if games[game_index].quit:
                        games.remove(games[game_index])
                        current_socket.send("yes")
                    else:
                        current_socket.send("no")

                elif data == "over":
                    game.quit = True

                elif data == "test":
                    pass

                elif info[0] == "online:":
                    online_users.append([info[1], current_socket])

                elif info[0] == "register:":
                    username = info[1]
                    password = info[2]
                    score = 0
                    conn = sqlite3.connect(file_name)
                    conn.text_factory = str
                    c = conn.cursor()
                    c.execute("SELECT * FROM users WHERE username=?", (username,))
                    matches = c.fetchall()
                    if len(matches) > 0:
                        current_socket.send("invalid")
                    else:
                        c.execute("INSERT INTO users VALUES (?, ?, ?)", (username, password, score))
                        conn.commit()
                        current_socket.send("valid")
                    conn.close()

                elif info[0] == "login:":
                    username = info[1]
                    password = info[2]
                    conn = sqlite3.connect(file_name)
                    conn.text_factory = str
                    c = conn.cursor()
                    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
                    matches = c.fetchall()
                    if len(matches) > 0:
                        logged_in = False
                        for user in online_users:
                            if user[0] == username:
                                logged_in = True
                        if not logged_in:
                            online_users.append([username, current_socket])
                            current_socket.send("valid," + str(matches[0][2]))
                        else:
                            current_socket.send("logged in")
                    else:
                        current_socket.send("invalid")
                    conn.close()

                elif data == "leaderboard":
                    conn = sqlite3.connect(file_name)
                    conn.text_factory = str
                    c = conn.cursor()
                    c.execute("SELECT username, score FROM users ORDER BY score DESC, username")
                    matches = c.fetchmany(10)
                    leaderboard = []
                    count = 1
                    for user in matches:
                        leaderboard.append(str(count) + ". " + str(user[0]) + " - " + str(user[1]))
                        count += 1
                    current_socket.send(pickle.dumps(leaderboard))
                    conn.close()

                elif info[0] == "play:":
                    if len(games) == 0:
                        games.append(Game(player1=current_socket, username1=info[1]))
                        games[-1].player1.send("1")

                    else:

                        if games[-1].player2 is None:
                            games[-1].player2 = current_socket
                            games[-1].username2 = info[1]
                            games[-1].player2.send("2")
                        else:
                            games.append(Game(player1=current_socket, username1=info[1]))
                            games[-1].player1.send("1")

                elif data == "ready?":
                    if games[game_index].player2 is not None:
                        current_socket.send("yes")
                    else:
                        current_socket.send("no")

                elif data == "board":
                    sprites = []
                    if player == 1:
                        for sprite in games[game_index].player1_units:
                            sprites.append([sprite.img, sprite.x, sprite.y])
                        current_socket.send(pickle.dumps(sprites))
                    elif player == 2:
                        for sprite in games[game_index].player2_units:
                            sprites.append([sprite.img, sprite.x, sprite.y])
                        current_socket.send(pickle.dumps(sprites))

                elif data == "random":
                    y_list_a = [y_list[0], y_list[1], y_list[2], y_list[3]]
                    if player == 1:
                        player_board = games[game_index].player1_units
                    else:
                        player_board = games[game_index].player2_units
                    empty_spots = []
                    for x in x_list:
                        for y in y_list_a:
                            found = False
                            for unit in player_board:
                                if unit.x == x and unit.y == y:
                                    found = True
                                    break
                            if not found:
                                empty_spots.append([x, y])
                    for unit in player_board:
                        if unit.y == 0:
                            index = randint(0, len(empty_spots)-1)
                            unit.x = empty_spots[index][0]
                            unit.y = empty_spots[index][1]
                            empty_spots.remove(empty_spots[index])
                    sprites = []
                    for sprite in player_board:
                        sprites.append([sprite.img, sprite.x, sprite.y])
                    current_socket.send(pickle.dumps(sprites))

                elif data == "enemy profile":
                    conn = sqlite3.connect(file_name)
                    conn.text_factory = str
                    c = conn.cursor()
                    if player == 1:
                        username = game.username2
                    else:
                        username = game.username1
                    c.execute("SELECT * FROM users WHERE username=?", (username,))
                    match = c.fetchall()
                    score = match[0][2]
                    current_socket.send("profile: " + str(username) + " " + str(score))
                    conn.close()

                elif data == "enemy board":
                    y_list_b = [y_list[6], y_list[7], y_list[8], y_list[9]]
                    if player == 2:
                        image = Chelsea
                    else:
                        image = Arsenal
                    sprites = []
                    for x in x_list:
                        for y in y_list_b:
                            sprites.append([image, x, y])
                    current_socket.send(pickle.dumps(sprites))

                elif data == "placing?":
                    if player == 1:
                        player_units = games[game_index].player1_units
                        enemy_units = games[game_index].player2_units
                    else:
                        player_units = games[game_index].player2_units
                        enemy_units = games[game_index].player1_units
                    found = False
                    for unit in player_units:
                        if unit.y == 0:
                            found = True
                            break
                    if found:
                        current_socket.send("Please fill the board")
                    else:
                        if player == 1:
                            games[game_index].placing1 = False
                            if games[game_index].placing2:
                                current_socket.send("Enemy hasn't filled the board")
                            else:
                                games[game_index].player1_press_index = None
                                games[game_index].player2_press_index = None
                                games[game_index].placing = False
                                current_socket.send("finished")
                        elif player == 2:
                            games[game_index].placing2 = False
                            if games[game_index].placing1:
                                current_socket.send("Enemy hasn't filled the board")
                            else:
                                games[game_index].player1_press_index = None
                                games[game_index].player2_press_index = None
                                games[game_index].placing = False
                                current_socket.send("finished")

                elif data == "change?":
                    msg = "nothing"
                    if game.turn == 0 and player == game.next_turn:
                        msg = enemy_turn(game.change)
                        game.turn = -1
                        if game.quit:
                            game.next_turn = 0
                    current_socket.send(msg)

                elif data == "switch":
                    game.turn = game.next_turn
                    if game.turn == 1:
                        game.next_turn = 2
                    else:
                        game.next_turn = 1
                    current_socket.send("works")

                elif info[0] == "mouse:":

                    msg = "nothing"
                    error = False
                    try:
                        mouse_x = int(info[1])
                        mouse_y = int(info[2])
                    except:
                        error = True

                    if not no_game:
                        if not error:
                            if game.placing:

                                # first press
                                if mouse_y < place_bar and left_limit < mouse_x < right_limit:
                                    while mouse_x > left_limit:
                                        if mouse_x == bomb_start or mouse_x == x_list[9] or mouse_x == x_list[8] or mouse_x == x_list[7] or\
                                           mouse_x == x_list[6] or mouse_x == x_list[5] or mouse_x == x_list[4] or mouse_x == x_list[3] or\
                                           mouse_x == x_list[2] or mouse_x == x_list[1] or mouse_x == x_list[0] or mouse_x == flag_start:
                                            break
                                        mouse_x -= 1

                                    if player == 1:
                                        for index in xrange(len(game.player1_units)):
                                            if game.player1_units[index].x == mouse_x and game.player1_units[index].y == 0:
                                                game.player1_press_index = index
                                                break
                                    elif player == 2:
                                        for index in xrange(len(game.player2_units)):
                                            if game.player2_units[index].x == mouse_x and game.player2_units[index].y == 0:
                                                game.player2_press_index = index
                                                break

                                # second press
                                elif board_bottom_limit < mouse_y < y_list[4] and board_left_limit < mouse_x < board_right_limit:
                                    while mouse_x > board_left_limit:
                                        if mouse_x == x_list[9] or mouse_x == x_list[8] or mouse_x == x_list[7] or\
                                           mouse_x == x_list[6] or mouse_x == x_list[5] or mouse_x == x_list[4] or mouse_x == x_list[3] or\
                                           mouse_x == x_list[2] or mouse_x == x_list[1] or mouse_x == x_list[0]:
                                            break
                                        mouse_x -= 1
                                    while mouse_y > board_bottom_limit:
                                        if mouse_y == y_list[3] or mouse_y == y_list[2] or mouse_y == y_list[1] or mouse_y == y_list[0]:
                                            break
                                        mouse_y -= 1

                                    found = False
                                    if player == 1:
                                        for index in xrange(len(game.player1_units)):
                                            if game.player1_units[index].x == mouse_x and game.player1_units[index].y == mouse_y:
                                                found = True
                                                unit_index = index
                                                break
                                        if found:
                                            game.player1_press_index = None
                                            curr_unit = game.player1_units[unit_index]
                                            send_y = 0
                                            if curr_unit.level == 0:
                                                send_x = flag_start
                                            elif curr_unit.level == 11:
                                                send_x = bomb_start
                                            else:
                                                send_x = x_list[curr_unit.level-1]
                                            curr_unit.x = send_x
                                            curr_unit.y = send_y
                                            msg = "del " + str(unit_index) + " " + str(send_x) + " " + str(send_y)

                                        elif game.player1_press_index is not None:
                                            last_x = game.player1_units[game.player1_press_index].x
                                            game.player1_units[game.player1_press_index].x = mouse_x
                                            game.player1_units[game.player1_press_index].y = mouse_y
                                            msg = str(game.player1_press_index) + " " + str(mouse_x) + " " + str(mouse_y)
                                            try:
                                                game.player1_press_index = None
                                                for index in xrange(len(game.player1_units)):
                                                    if game.player1_units[index].x == last_x and game.player1_units[index].y == 0:
                                                        game.player1_press_index = index
                                            except:
                                                game.player1_press_index = None

                                    elif player == 2:
                                        for index in xrange(len(game.player2_units)):
                                            if game.player2_units[index].x == mouse_x and game.player2_units[index].y == mouse_y:
                                                found = True
                                                unit_index = index
                                                break
                                        if found:
                                            game.player2_press_index = None
                                            curr_unit = game.player2_units[unit_index]
                                            send_y = 0
                                            if curr_unit.level == 0:
                                                send_x = flag_start
                                            elif curr_unit.level == 11:
                                                send_x = bomb_start
                                            else:
                                                send_x = x_list[curr_unit.level-1]
                                            curr_unit.x = send_x
                                            curr_unit.y = send_y
                                            msg = "del " + str(unit_index) + " " + str(send_x) + " " + str(send_y)

                                        elif game.player2_press_index is not None:
                                            last_x = game.player2_units[game.player2_press_index].x
                                            game.player2_units[game.player2_press_index].x = mouse_x
                                            game.player2_units[game.player2_press_index].y = mouse_y
                                            msg = str(game.player2_press_index) + " " + str(mouse_x) + " " + str(mouse_y)
                                            try:
                                                game.player2_press_index = None
                                                for index in xrange(len(game.player2_units)):
                                                    if game.player2_units[index].x == last_x and game.player2_units[index].y == 0:
                                                        game.player2_press_index = index
                                            except:
                                                game.player2_press_index = None

                            # in-game
                            elif board_bottom_limit < mouse_y < board_top_limit and board_left_limit < mouse_x < board_right_limit and game.turn == player:
                                while mouse_x > board_left_limit:
                                    if mouse_x == x_list[9] or mouse_x == x_list[8] or mouse_x == x_list[7] or \
                                       mouse_x == x_list[6] or mouse_x == x_list[5] or mouse_x == x_list[4] or mouse_x == x_list[3] or \
                                       mouse_x == x_list[2] or mouse_x == x_list[1] or mouse_x == x_list[0]:
                                        break
                                    mouse_x -= 1
                                while mouse_y > board_bottom_limit:
                                    if mouse_y == y_list[9] or mouse_y == y_list[8] or mouse_y == y_list[7] or \
                                       mouse_y == y_list[6] or mouse_y == y_list[5] or mouse_y == y_list[4] or mouse_y == y_list[3] or \
                                       mouse_y == y_list[2] or mouse_y == y_list[1] or mouse_y == y_list[0]:
                                        break
                                    mouse_y -= 1
                                if (mouse_x == x_list[2] or mouse_x == x_list[3] or mouse_x == x_list[6] or mouse_x == x_list[7]) and \
                                   (mouse_y == y_list[4] or mouse_y == y_list[5]):
                                    pass
                                else:
                                    found = False
                                    if player == 1:
                                        if game.player1_press_index is None:
                                            found = True
                                        for index in xrange(len(game.player1_units)):
                                            if game.player1_units[index].x == mouse_x and game.player1_units[index].y == mouse_y:
                                                game.player1_press_index = index
                                                found = True
                                                msg = str(game.player1_units[index].x) + " " + str(game.player1_units[index].y)
                                                break
                                    elif player == 2:
                                        if game.player2_press_index is None:
                                            found = True
                                        for index in xrange(len(game.player2_units)):
                                            if game.player2_units[index].x == mouse_x and game.player2_units[index].y == mouse_y:
                                                game.player2_press_index = index
                                                found = True
                                                msg = str(game.player2_units[index].x) + " " + str(game.player2_units[index].y)
                                                break
                                    if not found:
                                        if player == 1:
                                            unit_x = game.player1_units[game.player1_press_index].x
                                            unit_y = game.player1_units[game.player1_press_index].y
                                            unit_level = game.player1_units[game.player1_press_index].level
                                        else:
                                            unit_x = game.player2_units[game.player2_press_index].x
                                            unit_y = game.player2_units[game.player2_press_index].y
                                            unit_level = game.player2_units[game.player2_press_index].level
                                        if unit_level != 0 and unit_level != 11:
                                            move = False
                                            if (unit_x == mouse_x and (unit_y < mouse_y < unit_y+100 or unit_y-100 < mouse_y < unit_y))\
                                               or \
                                               (unit_y == mouse_y and (unit_x < mouse_x < unit_x+100 or unit_x-100 < mouse_x < unit_x)):
                                                move = True
                                            else:
                                                if player == 1 and game.player1_units[game.player1_press_index].level == 2:
                                                    if game.player1_units[game.player1_press_index].scout_move():
                                                        move = True
                                                elif player == 2 and game.player2_units[game.player2_press_index].level == 2:
                                                    if game.player2_units[game.player2_press_index].scout_move():
                                                        move = True
                                            if move:
                                                add = ["", ""]
                                                animation = ""
                                                if player == 1:
                                                    last_x = str(game.player1_units[game.player1_press_index].x)
                                                    last_y = str(game.player1_units[game.player1_press_index].y)
                                                    game.player1_units[game.player1_press_index].x = mouse_x
                                                    game.player1_units[game.player1_press_index].y = mouse_y
                                                    msg = str(game.player1_press_index) + " " + str(mouse_x) + " " + str(mouse_y)
                                                    game.change = last_x + " " + last_y + " " + str(mouse_x) + " " + str(mouse_y)
                                                    index = -1
                                                    for i in range(len(game.player2_units)):
                                                        if change_x(game.player2_units[i].x) == mouse_x and \
                                                                change_y(game.player2_units[i].y) == mouse_y:
                                                            index = i
                                                            break
                                                    if index != -1:
                                                        if game.player2_units[index].level == 0:
                                                            add[0] += " win:+100"
                                                            update1 = 100
                                                            if minimum_score(game.username2):
                                                                add[1] += " lose:-0"
                                                                update2 = 0
                                                            else:
                                                                add[1] += " lose:-50"
                                                                update2 = -50
                                                            update_scores(username1=game.username1, username2=game.username2, update1=update1, update2=update2)
                                                            animation = "-" + str(Sarri_Celebration) + "@-" + str(Emery_Angry) + "&3"
                                                        elif game.player1_units[game.player1_press_index].level == 1 and game.player2_units[index].level == 10:
                                                            animation = "-" + str(Kepa_Celebration)
                                                        elif game.player2_units[index].level == 11:
                                                            if game.player1_units[game.player1_press_index].level == 3:
                                                                animation = "-" + str(Pedro_Celebration)
                                                            else:
                                                                animation = "-" + str(Dean_Celebration)
                                                        if game.player1_units[game.player1_press_index].level > game.player2_units[index].level or \
                                                           (game.player1_units[game.player1_press_index].level == 3 and game.player2_units[index].level == 11) or \
                                                           (game.player1_units[game.player1_press_index].level == 1 and game.player2_units[index].level == 10):
                                                            msg += " enemy." + str(mouse_x) + "." + str(mouse_y) + " Arsenal.png-" + game.player2_units[index].img
                                                            game.change += " player." + str(change_x(mouse_x)) + "." + str(change_y(mouse_y)) + " Chelsea.png-" + game.player1_units[game.player1_press_index].img
                                                            game.player2_units.remove(game.player2_units[index])
                                                        elif game.player1_units[game.player1_press_index].level < game.player2_units[index].level:
                                                            msg += " player." + str(mouse_x) + "." + str(mouse_y) + " Arsenal.png-" + game.player2_units[index].img
                                                            game.change += " enemy." + str(change_x(mouse_x)) + "." + str(change_y(mouse_y)) + " Chelsea.png-" + game.player1_units[game.player1_press_index].img
                                                            game.player1_units.remove(game.player1_units[game.player1_press_index])
                                                        else:
                                                            msg += " enemy." + str(mouse_x) + "." + str(mouse_y) + "-player." + str(mouse_x) + "." + str(mouse_y) + " Arsenal.png-" + game.player2_units[index].img
                                                            game.change += " player." + str(change_x(mouse_x)) + "." + str(change_y(mouse_y)) + "-enemy." + str(change_x(mouse_x)) + "." + str(change_y(mouse_y)) + " Chelsea.png-" + game.player1_units[game.player1_press_index].img
                                                            game.player2_units.remove(game.player2_units[index])
                                                            game.player1_units.remove(game.player1_units[game.player1_press_index])
                                                        animation = animation.split("@")
                                                        if len(animation) == 2:
                                                            animation1 = animation[1]
                                                            animation = animation[0]
                                                        else:
                                                            animation = animation[0]
                                                            animation1 = animation
                                                        msg += animation + add[0]
                                                        game.change += animation1 + add[1]
                                                    game.turn = 0
                                                    game.player1_press_index = None
                                                elif player == 2:
                                                    last_x = str(game.player2_units[game.player2_press_index].x)
                                                    last_y = str(game.player2_units[game.player2_press_index].y)
                                                    game.player2_units[game.player2_press_index].x = mouse_x
                                                    game.player2_units[game.player2_press_index].y = mouse_y
                                                    msg = str(game.player2_press_index) + " " + str(mouse_x) + " " + str(mouse_y)
                                                    game.change = last_x + " " + last_y + " " + str(mouse_x) + " " + str(mouse_y)
                                                    index = -1
                                                    for i in range(len(game.player1_units)):
                                                        if change_x(game.player1_units[i].x) == mouse_x and \
                                                                change_y(game.player1_units[i].y) == mouse_y:
                                                            index = i
                                                            break
                                                    if index != -1:
                                                        if game.player1_units[index].level == 0:
                                                            add[0] += " win:+100"
                                                            update2 = 100
                                                            if minimum_score(game.username1):
                                                                add[1] += " lose:-0"
                                                                update1 = 0
                                                            else:
                                                                add[1] += " lose:-50"
                                                                update1 = -50
                                                            update_scores(username1=game.username1, username2=game.username2, update1=update1, update2=update2)
                                                            animation = "-" + str(Emery_Celebration) + "@-" + str(Sarri_Angry) + "&2"
                                                        if game.player2_units[game.player2_press_index].level == 1 and game.player1_units[index].level == 10:
                                                            animation = "-" + str(Leno_Celebration)
                                                        elif game.player1_units[index].level == 11:
                                                            if game.player2_units[game.player2_press_index].level == 3:
                                                                animation = "-" + str(Xhaka_Celebration)
                                                            else:
                                                                animation = "-" + str(Dean_Celebration)
                                                        if game.player2_units[game.player2_press_index].level > game.player1_units[index].level or \
                                                           (game.player2_units[game.player2_press_index].level == 3 and game.player1_units[index].level == 11) or \
                                                           (game.player2_units[game.player2_press_index].level == 1 and game.player1_units[index].level == 10):
                                                            msg += " enemy." + str(mouse_x) + "." + str(mouse_y) + " Chelsea.png-" + game.player1_units[index].img
                                                            game.change += " player." + str(change_x(mouse_x)) + "." + str(change_y(mouse_y)) + " Arsenal.png-" + game.player2_units[game.player2_press_index].img
                                                            game.player1_units.remove(game.player1_units[index])
                                                        elif game.player2_units[game.player2_press_index].level < game.player1_units[index].level:
                                                            msg += " player." + str(mouse_x) + "." + str(mouse_y) + " Chelsea.png-" + game.player1_units[index].img
                                                            game.change += " enemy." + str(change_x(mouse_x)) + "." + str(change_y(mouse_y)) + " Arsenal.png-" + game.player2_units[game.player2_press_index].img
                                                            game.player2_units.remove(game.player2_units[game.player2_press_index])
                                                        else:
                                                            msg += " enemy." + str(mouse_x) + "." + str(mouse_y) + "-player." + str(mouse_x) + "." + str(mouse_y) + " Chelsea.png-" + game.player1_units[index].img
                                                            game.change += " player." + str(change_x(mouse_x)) + "." + str(change_y(mouse_y)) + "-enemy." + str(change_x(mouse_x)) + "." + str(change_y(mouse_y)) + " Arsenal.png-" + game.player2_units[game.player2_press_index].img
                                                            game.player1_units.remove(game.player1_units[index])
                                                            game.player2_units.remove(game.player2_units[game.player2_press_index])
                                                        animation = animation.split("@")
                                                        if len(animation) == 2:
                                                            animation1 = animation[1]
                                                            animation = animation[0]
                                                        else:
                                                            animation = animation[0]
                                                            animation1 = animation
                                                        msg += animation + add[0]
                                                        game.change += animation1 + add[1]
                                                    game.turn = 0
                                                    game.player2_press_index = None

                            current_socket.send(msg)

                        else:
                            print data
                            current_socket.send("error")

                    else:
                        current_socket.send(msg)

                else:
                    print data
                    current_socket.send("error")