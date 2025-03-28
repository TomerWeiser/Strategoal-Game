import socket
import os
import subprocess
import pickle
from Tkinter import *
import threading
import time
from Constants import *

try:
    import pyglet
    from pyglet.window import mouse

except:
    os.system("pip install pyglet > null")
    import pyglet
    from pyglet.window import mouse

# Bonus
# ----------
# 1. Chat
# 2. Display dead units


def game():
    """
    The function is responsible for everything
    in the region of the in game screen including GUI and logic.
    """

    global exit_app
    global player
    global game_visible
    global player_board
    global enemy_board
    global placing
    global placing_label
    global end_label
    global enemy_label
    global frame
    global my_placing
    global turn
    global animation
    global count
    global username
    global score

    window = pyglet.window.Window(width=screen_width, height=screen_height, caption=Game_Caption)

    # Images
    board = pyglet.image.load(Soccer_Board)

    placing_menu = pyglet.image.load(Placing_Screen)

    # Sprites
    frame = pyglet.sprite.Sprite(img=pyglet.image.load(Frame_Box))
    frame.visible = False

    # Labels
    end_label = pyglet.text.Label("Opponent Has Left!", x=window.width/2, y=window.height/2 + 50,
                                  font_name=Cooper_Black, font_size=72, color=red, bold=True,
                                  anchor_x="center", anchor_y="center")

    crash_label = pyglet.text.Label("The Server Has Crashed", x=window.width/2, y=window.height/2 + 50,
                                    font_name=Cooper_Black, font_size=60, color=red, bold=True,
                                    anchor_x="center", anchor_y="center")

    ready_label = pyglet.text.Label("Ready?", x=50, y=600, font_name=Cooper_Black, font_size=48,
                                    color=gold, bold=True,)

    placing_label = pyglet.text.Label("", x=window.width/2, y=window.height/2 + 150,
                                      font_name=Cooper_Black, font_size=42, color=orange, bold=True,
                                      anchor_x="center", anchor_y="center")

    random_label = pyglet.text.Label("Random", x=650, y=600, font_name=Cooper_Black, font_size=48,
                                     color=gold, bold=True,)

    menu_label = pyglet.text.Label("Menu", x=window.width/2, y=50, font_name=Cooper_Black, font_size=48,
                                   color=gold, bold=True, anchor_x="center", anchor_y="center")

    turn_label = pyglet.text.Label("Your Turn", x=window.width/2, y=50, font_name=Cooper_Black, font_size=36,
                                   color=white, bold=True, anchor_x="center", anchor_y="center")
    if player == "2":
        turn_label.text = "Opponent's Turn"
        turn_label.color = black

    player_label = pyglet.text.Label(text=str(username) + ": " + str(score), x=2, y=500, font_name=Cooper_Black,
                                     font_size=float(180/(len(username) + len(score) + 3)), color=white,
                                     bold=True)

    enemy_label = pyglet.text.Label(text="", x=880, y=500, font_name=Cooper_Black, font_size=0, color=(0, 0, 0, 0),
                                    bold=True)

    game_visible = [False, False, True, False, True, False, False, True, False]

    placing = True
    my_placing = True

    animation = None

    turn = 1

    def quit_game(dt):
        """
        :param dt: The function receives a value that represents
        the gap between each call of the function.

        The function checks whether the game is over
        or rather the server has crashed and if so,
        it ends the game and closes the connection to the server.
        """

        global my_socket
        global game_visible
        global player_board
        global placing

        try:
            answer = "error"
            while answer == "error":
                my_socket.send("quit?")
                answer = my_socket.recv(512)
            if answer == "yes":
                pyglet.clock.unschedule(quit_game)
                pyglet.clock.unschedule(waiting_for_placing)
                pyglet.clock.unschedule(waiting_for_turn)
                game_visible[0] = True
                game_visible[2] = False
                game_visible[3] = False
                game_visible[4] = False
                game_visible[6] = False
                game_visible[5] = True
                if placing:
                    player_board = []

        except:
            pyglet.clock.unschedule(quit_game)
            pyglet.clock.unschedule(waiting_for_placing)
            pyglet.clock.unschedule(waiting_for_turn)
            game_visible[1] = True
            game_visible[2] = False
            game_visible[3] = False
            game_visible[4] = False
            game_visible[6] = False
            game_visible[5] = True
            if placing:
                player_board = []

    def get_board():
        """
        The function receives from the server the list of units of the player and
        places them in a list of sprites in which each sprite represents a unit.
        """

        global my_socket
        global player
        global player_board
        global enemy_board

        try:
            data = "error"
            while data == "error":
                my_socket.send("board")
                data = my_socket.recv(4096)
            data = pickle.loads(data)
            player_board = []
            enemy_board = []

            for unit in data:
                player_board.append(pyglet.sprite.Sprite(img=pyglet.image.load(unit[0]), x=unit[1], y=unit[2]))
        except:
            pass

    def get_random_board():
        """
        The function receives from the server a randomized list of units of the player and
        places them in a list of sprites in which each sprite represents a unit.
        """

        global my_socket
        global player_board

        try:
            data = "error"
            while data == "error":
                my_socket.send("random")
                data = my_socket.recv(4096)
            data = pickle.loads(data)
            player_board = []

            for unit in data:
                player_board.append(pyglet.sprite.Sprite(img=pyglet.image.load(unit[0]), x=unit[1], y=unit[2]))
        except:
            pass

    def get_enemy_board():
        """
        The function receives from the server the list of units of the opponent and
        places them in a list of sprites in which each sprite represents a unit.
        """

        global my_socket
        global enemy_board

        try:
            data = "error"
            while data == "error":
                my_socket.send("enemy board")
                data = my_socket.recv(4096)
            data = pickle.loads(data)
            enemy_board = []

            for unit in data:
                enemy_board.append(pyglet.sprite.Sprite(img=pyglet.image.load(unit[0]), x=unit[1], y=unit[2]))
        except:
            pass

    def get_enemy_profile():
        """
        This function receives from the server the profile of the opponent and presents it on the screen.
        """

        global my_socket
        global game_visible
        global enemy_label

        try:
            data = ""
            msg_type = ""
            while msg_type != "profile:":
                my_socket.send("enemy profile")
                data = my_socket.recv(1024)
                data = data.split(" ")
                if len(data) == 3:
                    msg_type = data[0]
            enemy_name = str(data[1])
            enemy_score = str(data[2])
            enemy_label = pyglet.text.Label(text=str(enemy_name) + ": " + str(enemy_score), x=872, y=500,
                                            font_name=Cooper_Black, color=black,
                                            font_size=float(180/(len(enemy_name) + len(enemy_score) + 3)), bold=True)
            game_visible[8] = True
        except:
            pass

    def waiting_for_placing(dt):
        """
        :param dt: The function receives a value that represents
        the gap between each call of the function.

        The function checks with the server
        whether the opponent has finished to place his units on the board
        and if so, it finished the placing stage.
        """

        global my_socket
        global game_visible
        global placing

        try:
            data = "error"
            while data == "error":
                my_socket.send("placing?")
                data = my_socket.recv(512)
            if data == "finished":
                placing = False
                game_visible[2] = False
                game_visible[3] = False
                game_visible[4] = False
                game_visible[6] = True
                pyglet.clock.unschedule(waiting_for_placing)
                get_enemy_profile()
                get_enemy_board()
                pyglet.clock.schedule_interval(waiting_for_turn, 0.1)
        except:
            pass

    def waiting_for_turn(dt):
        """
        :param dt: The function receives a value that represents
        the gap between each call of the function.

        The function checks whether the opponent has finished his turn,
        and if so, it checks the changes made in that turn
        and changes it on the board accordingly.
        """

        global my_socket
        global enemy_board
        global player
        global animation
        global over
        global score

        try:
            change = "error"
            while change == "error":
                my_socket.send("change?")
                change = my_socket.recv(4096)
            change = change.split(" ")
            if len(change) == 4 or len(change) == 6 or len(change) == 7:
                old_x = int(change[0])
                old_y = int(change[1])
                new_x = int(change[2])
                new_y = int(change[3])
                attack = ""
                images = [""]
                over = False
                if len(change) == 6 or len(change) == 7:
                    attack = change[4]
                    images = change[5].split("-")
                    for unit in enemy_board:
                        if unit.x == old_x and unit.y == old_y:
                            unit.image = pyglet.image.load(images[1])
                            break
                    if len(change) == 7:
                        points = change[6].split(":")[1]
                        score = str(int(score) + int(points))
                        end_label.text = "Defeat " + str(points)
                        over = True
                        end_label.font_size = 48
                index = 0
                for i in xrange(len(enemy_board)):
                    if old_x == enemy_board[i].x and old_y == enemy_board[i].y:
                        index = i
                pyglet.clock.schedule_interval(move_unit, 1 / 60.0, index, new_x, new_y, "enemy", attack, images[0], over, images)
        except:
            pass

    def move_unit(dt, player_index, new_x, new_y, board, attack="", image="", over=False, gif=[]):
        """
        :param dt: A value that represents
        the gap between each call of the function.
        :param player_index: The index of the unit in the list that is subject to change.
        :param new_x: The new x value of the changed unit.
        :param new_y: The new y value of the changed unit.
        :param board: Either the player's board or the opponent's board.
        :param attack: A string that represents which unit needs to be removed,
        from which list and an image of the unit that is being attacked.
        :param image: A string that represents the image of the unit
        that is being attacked and an image of the team's logo.
        :param over: A boolean that represents whether the game is won or lost.

        The function moves the wanted unit on the board,
        deletes a unit from the board if it has been attacked and lost
        and disconnects from the server if the game is finished.
        """

        global my_socket
        global player_board
        global enemy_board
        global animation
        global count

        direction_x = "nothing"
        direction_y = "nothing"

        if board == "player":
            if player_board[player_index].x > new_x:
                direction_x = "left"
            elif player_board[player_index].x < new_x:
                direction_x = "right"
            if player_board[player_index].y > new_y:
                direction_y = "down"
            elif player_board[player_index].y < new_y:
                direction_y = "up"

            if player_board[player_index].x == new_x and player_board[player_index].y == new_y:
                pyglet.clock.unschedule(move_unit)
                if attack != "":
                    attack = attack.split("-")
                    for dead in attack:
                        dead = dead.split(".")
                        del_board = dead[0]
                        del_x = int(dead[1])
                        del_y = int(dead[2])
                        if del_board == "player":
                            for unit in player_board:
                                if unit.x == del_x and unit.y == del_y:
                                    player_board.remove(unit)
                                    break
                            for unit in enemy_board:
                                if unit.x == del_x and unit.y == del_y:
                                    unit.image = pyglet.image.load(image)
                                    break
                        elif del_board == "enemy":
                            for unit in enemy_board:
                                if unit.x == del_x and unit.y == del_y:
                                    enemy_board.remove(unit)
                                    break
                if len(gif) == 3:
                    count = 0
                    animation = pyglet.image.load_animation(gif[2])
                    x = animation.get_max_width()/2
                    y = animation.get_max_height()/2
                    animation = pyglet.sprite.Sprite(img=animation, x=window.width/2-x, y=window.height/2-y)
                    pyglet.clock.schedule_interval(animation_time, 1)
                else:
                    if turn_label.text == "Your Turn":
                        turn_label.color = black
                        turn_label.text = "Opponent's Turn"
                    else:
                        turn_label.color = white
                        turn_label.text = "Your Turn"
                if over:
                    pyglet.clock.unschedule(quit_game)
                    pyglet.clock.unschedule(waiting_for_placing)
                    pyglet.clock.unschedule(waiting_for_turn)
                    my_socket.send("over")
                    game_visible[0] = True
                    game_visible[5] = True
                    game_visible[6] = False
            else:
                if direction_x == "left":
                    player_board[player_index].x -= 2
                elif direction_x == "right":
                    player_board[player_index].x += 2
                if direction_y == "down":
                    player_board[player_index].y -= 2
                elif direction_y == "up":
                    player_board[player_index].y += 2

        elif board == "enemy":
            if enemy_board[player_index].x > new_x:
                direction_x = "left"
            elif enemy_board[player_index].x < new_x:
                direction_x = "right"
            if enemy_board[player_index].y > new_y:
                direction_y = "down"
            elif enemy_board[player_index].y < new_y:
                direction_y = "up"

            if enemy_board[player_index].x == new_x and enemy_board[player_index].y == new_y:
                pyglet.clock.unschedule(move_unit)
                if attack != "":
                    attack = attack.split("-")
                    for dead in attack:
                        dead = dead.split(".")
                        del_board = dead[0]
                        del_x = int(dead[1])
                        del_y = int(dead[2])
                        if del_board == "player":
                            for unit in player_board:
                                if unit.x == del_x and unit.y == del_y:
                                    player_board.remove(unit)
                                    break
                            for unit in enemy_board:
                                if unit.x == del_x and unit.y == del_y:
                                    unit.image = pyglet.image.load(image)
                                    break
                        elif del_board == "enemy":
                            for unit in enemy_board:
                                if unit.x == del_x and unit.y == del_y:
                                    enemy_board.remove(unit)
                                    break
                if len(gif) == 3:
                    scale = 1.0
                    gif = gif[2].split("&")
                    if len(gif) == 2:
                        end = True
                        scale = float(gif[1])-0.5
                    else:
                        end = False
                    gif = gif[0]
                    count = 0
                    animation = pyglet.image.load_animation(gif)
                    x = animation.get_max_width()/2
                    y = animation.get_max_height()/2
                    animation = pyglet.sprite.Sprite(img=animation, x=window.width/2-x, y=window.height/2-y)
                    if end:
                        animation.scale = scale
                        animation.x = window.width/2-(scale*x)
                        animation.y = window.height/2-(scale*y)
                    pyglet.clock.schedule_interval(animation_time, 1, "enemy")
                else:
                    if turn_label.text == "Your Turn":
                        turn_label.color = black
                        turn_label.text = "Opponent's Turn"
                    else:
                        turn_label.color = white
                        turn_label.text = "Your Turn"
                    try:
                        answer = "error"
                        while answer == "error":
                            my_socket.send("switch")
                            answer = my_socket.recv(512)
                    except:
                        pass
            else:
                if direction_x == "left":
                    enemy_board[player_index].x -= 2
                elif direction_x == "right":
                    enemy_board[player_index].x += 2
                if direction_y == "down":
                    enemy_board[player_index].y -= 2
                elif direction_y == "up":
                    enemy_board[player_index].y += 2

    def animation_time(dt, board=""):
        """
        :param dt: A value that represents
        the gap between each call of the function.
        :param board:
        """

        global count
        global my_socket
        global animation
        global over

        if count == 6 and not over:
            if turn_label.text == "Your Turn":
                turn_label.color = black
                turn_label.text = "Opponent's Turn"
            else:
                turn_label.color = white
                turn_label.text = "Your Turn"
            pyglet.clock.unschedule(animation_time)
            animation = None
            if board == "enemy":
                try:
                    answer = "error"
                    while answer == "error":
                        my_socket.send("switch")
                        answer = my_socket.recv(512)
                except:
                    pass
        count += 1

    @window.event()
    def on_draw():
        """
        this function redraws the screen every time a window event happens or scheduled functions were called.
        """

        global player_board
        global enemy_board
        global placing
        global animation

        window.clear()
        board.blit(0, 0)

        frame.draw()

        for sprite in enemy_board:
            sprite.draw()
        for sprite in player_board:
            sprite.draw()

        if animation is not None:
            animation.draw()

        if placing:
            placing_menu.blit(50, 378)

        if game_visible[0]:  # game over
            end_label.draw()
        if game_visible[1]:  # server crashed
            crash_label.draw()
        if game_visible[2]:  # ready button
            ready_label.draw()
        if game_visible[3]:  # placing messages
            placing_label.draw()
        if game_visible[4]:  # random button
            random_label.draw()
        if game_visible[5]:  # menu button
            menu_label.draw()
        if game_visible[6]:  # turn label
            turn_label.draw()
        if game_visible[7]:  # player profile label
            player_label.draw()
        if game_visible[8]:  # enemy profile label
            enemy_label.draw()

    @window.event
    def on_mouse_motion(x, y, dx, dy):
        """
        :param x: Mouse x
        :param y: Mouse y
        :param dx: How many pixels did the mouse x moved
        :param dy: How many pixels did the mouse y moved

        The function is called every time the mouse is moved, it checks whether the mouse
        is currently on a certain label or object and changes its structure.
        """

        global game_visible

        if game_visible[2]:
            # Ready Button
            if 50 <= x <= 280 and 600 <= y <= 646:
                window.set_mouse_cursor(window.get_system_mouse_cursor(window.CURSOR_HAND))
                ready_label.color = white
                random_label.color = gold
            # Random Button
            elif 650 <= x <= 920 and 600 <= y <= 646:
                window.set_mouse_cursor(window.get_system_mouse_cursor(window.CURSOR_HAND))
                ready_label.color = gold
                random_label.color = black
            else:
                window.set_mouse_cursor(window.get_system_mouse_cursor(window.CURSOR_DEFAULT))
                ready_label.color = gold
                random_label.color = gold

        elif game_visible[5]:
            # Menu Button
            if 410 <= x <= 585 and 24 <= y <= 68:
                window.set_mouse_cursor(window.get_system_mouse_cursor(window.CURSOR_HAND))
                menu_label.color = white
            else:
                window.set_mouse_cursor(window.get_system_mouse_cursor(window.CURSOR_DEFAULT))
                menu_label.color = gold
        else:
            window.set_mouse_cursor(window.get_system_mouse_cursor(window.CURSOR_DEFAULT))
            ready_label.color = gold
            random_label.color = gold
            menu_label.color = gold

    @window.event()
    def on_mouse_press(x, y, button, modifiers):
        """
        :param x: Mouse x
        :param y: Mouse y
        :param button: Which button in the mouse was pressed (left/right/middle).
        :param modifiers: Whether any keyboard key was pressed during the mouse press.

        The function is called every time the mouse is pressed.
        it checks whether the mouse is currently on a certain
        label or object and if so, it calls functions or contacts the server accordingly.
        """

        global my_socket
        global game_visible
        global placing
        global placing_label
        global my_placing
        global player_board
        global enemy_board
        global frame
        global end_label
        global animation
        global over
        global exit_app
        global score

        if button == mouse.LEFT:

            # Ready
            if game_visible[2] and 50 <= x <= 280 and 600 <= y <= 646:
                    if my_placing:
                        try:
                            data = "error"
                            while data == "error":
                                my_socket.send("placing?")
                                data = my_socket.recv(512)
                            if data == "Please fill the board":
                                placing_label.text = data
                                game_visible[3] = True
                            elif data == "Enemy hasn't filled the board":
                                placing_label.text = data
                                game_visible[3] = True
                                my_placing = False
                                pyglet.clock.schedule_interval(waiting_for_placing, 0.1)
                            else:
                                my_placing = False
                                placing = False
                                game_visible[2] = False
                                game_visible[3] = False
                                game_visible[4] = False
                                game_visible[6] = True
                                get_enemy_profile()
                                get_enemy_board()
                                pyglet.clock.schedule_interval(waiting_for_turn, 0.1)
                        except:
                            pass
            # Random
            elif game_visible[2] and 650 <= x <= 920 and 600 <= y <= 646:
                get_random_board()
            # Menu
            elif game_visible[5] and 410 <= x <= 585 and 24 <= y <= 68:
                window.close()
                exit_app = False
                pyglet.clock.unschedule(animation_time)
            else:
                try:
                    change = "error"
                    while change == "error":
                        my_socket.send("mouse: " + str(x) + " " + str(y))
                        change = my_socket.recv(4096)
                    change = change.split(" ")

                    if len(change) == 2:
                        frame_x = int(change[0])
                        frame_y = int(change[1])
                        frame.x = frame_x-1
                        frame.y = frame_y
                        frame.visible = True

                    elif len(change) == 4 and change[0] == "del":
                        index = int(change[1])
                        new_x = int(change[2])
                        new_y = int(change[3])
                        player_board[index].x = new_x
                        player_board[index].y = new_y

                    else:
                        if len(change) == 3 or len(change) == 5 or len(change) == 6:
                            frame.visible = False
                            index = int(change[0])
                            new_x = int(change[1])
                            new_y = int(change[2])
                            attack = ""
                            images = [""]
                            over = False
                            if len(change) == 5 or len(change) == 6:
                                attack = change[3]
                                images = change[4].split("-")
                                for unit in enemy_board:
                                    if unit.x == new_x and unit.y == new_y:
                                        unit.image = pyglet.image.load(images[1])
                                        break
                                if len(change) == 6:
                                    points = change[5].split(":")[1]
                                    score = str(int(score) + int(points))
                                    end_label.text = "Victory! " + str(points)
                                    end_label.font_size = 48
                                    end_label.color = victory_color
                                    over = True
                            if placing:
                                player_board[index].x = new_x
                                player_board[index].y = new_y
                            else:
                                pyglet.clock.schedule_interval(move_unit, 1/60.0, index, new_x, new_y, "player", attack, images[0], over, images)
                except:
                    pass

    get_board()
    pyglet.clock.schedule_interval(quit_game, 0.1)

    pyglet.app.run()


def menu():
    """
    The function is responsible for everything
    in the region of the main menu including GUI and logic.
    """

    global visible
    global finding
    global username
    global score
    global instructions_screen
    global leaderboard_screen
    global leaderboard_labels
    global exit_app

    # Window
    window = pyglet.window.Window(width=screen_width, height=screen_height, caption=Game_Caption)

    # Images
    background = pyglet.image.load(Soccer_Background)
    instructions = pyglet.image.load(Instructions_Image)

    # Labels
    play_label = pyglet.text.Label("Play", x=20, y=290, font_name=Cooper_Black, font_size=48,
                                   color=gold, bold=True)

    instruction_label = pyglet.text.Label("Instructions", x=20, y=160, font_name=Cooper_Black, font_size=48,
                                          color=gold, bold=True)

    quit_label = pyglet.text.Label("Quit", x=20, y=30, font_name=Cooper_Black, font_size=48, color=gold, bold=True)

    finding_label = pyglet.text.Label("Finding Game...", x=window.width/2, y=window.height/2, font_name=Cooper_Black,
                                      font_size=90, color=gold, bold=True,
                                      anchor_x="center", anchor_y="center")

    connect_label = pyglet.text.Label("Server isn't up, try again later.", x=window.width/2, y=window.height/2 + 50,
                                      font_name=Cooper_Black, font_size=42, color=orange, bold=True,
                                      anchor_x="center", anchor_y="center")

    menu_label = pyglet.text.Label("Menu", x=window.width/2, y=50, font_name=Cooper_Black, font_size=48,
                                   color=gold, bold=True, anchor_x="center", anchor_y="center")

    stats_label = pyglet.text.Label(text=str(username) + " - " + str(score), x=window.width/2, y=window.height/2-10,
                                    font_name=Cooper_Black, font_size=42, color=gold, bold=True,
                                    anchor_x="center", anchor_y="center")

    leaderboard_label = pyglet.text.Label("Leaderboard", x=window.width/2 + 50, y=30, font_name=Cooper_Black, font_size=48,
                                          color=gold, bold=True)

    visible = [True, True, True, False, False, False, True, True]

    finding = False
    leaderboard_screen = False

    def find(dt):
        """
        :param dt: A value that represents
        the gap between each call of the function.

        The function checks if an opponent has been found
        and if so, it quits the menu and starts the game.
        """

        global my_socket
        global visible
        global finding

        if not finding:
            pyglet.clock.unschedule(find)
            visible = [True, True, True, False, False, False, True, True]

        else:
            try:
                my_socket.send("ready?")
                ready = my_socket.recv(512)

                if ready == "yes":
                    pyglet.clock.unschedule(find)

                    window.close()
                    game()

            except:
                pyglet.clock.unschedule(find)
                finding = False
                visible = [True, True, True, False, True, False, True, True]

    @window.event()
    def on_draw():
        """
        this function redraws the screen every time
        a window event happens or scheduled functions were called.
        """

        window.clear()
        background.blit(0, 0)

        if instructions_screen:
            instructions.blit(0, 0)

        if visible[0]:
            play_label.draw()
        if visible[1]:
            instruction_label.draw()
        if visible[2]:
            quit_label.draw()
        if visible[3]:
            finding_label.draw()
        if visible[4]:
            connect_label.draw()
        if visible[5]:
            menu_label.draw()
        if visible[6]:
            stats_label.draw()
        if visible[7]:
            leaderboard_label.draw()

        if leaderboard_screen:
            for label in leaderboard_labels:
                label.draw()

    @window.event
    def on_mouse_motion(x, y, dx, dy):
        """
        :param x: Mouse x
        :param y: Mouse y
        :param dx: How many pixels did the mouse x moved
        :param dy: How many pixels did the mouse y moved

        The function is called every time the mouse is moved,
        it checks whether the mouse is currently on a certain
        label or object and changes its structure.
        """

        global finding
        global leaderboard_screen
        global instructions_screen

        if not finding and not leaderboard_screen and not instructions_screen:
            # Play Button
            if 20 <= x <= 160 and 285 <= y <= 330:
                window.set_mouse_cursor(window.get_system_mouse_cursor(window.CURSOR_HAND))
                play_label.color = green
                instruction_label.color = gold
                quit_label.color = gold
                leaderboard_label.color = gold
            # Instruction Button
            elif 20 <= x <= 425 and 160 <= y <= 200:
                window.set_mouse_cursor(window.get_system_mouse_cursor(window.CURSOR_HAND))
                instruction_label.color = aqua
                play_label.color = gold
                quit_label.color = gold
                leaderboard_label.color = gold
            # Quit Button
            elif 20 <= x <= 160 and 25 <= y <= 70:
                window.set_mouse_cursor(window.get_system_mouse_cursor(window.CURSOR_HAND))
                quit_label.color = red
                play_label.color = gold
                instruction_label.color = gold
                leaderboard_label.color = gold
            # Leaderboard Button
            elif 550 <= x <= 965 and 30 <= y <= 75:
                window.set_mouse_cursor(window.get_system_mouse_cursor(window.CURSOR_HAND))
                leaderboard_label.color = grey
                play_label.color = gold
                instruction_label.color = gold
                quit_label.color = gold
            else:
                window.set_mouse_cursor(window.get_system_mouse_cursor(window.CURSOR_DEFAULT))
                play_label.color = gold
                instruction_label.color = gold
                quit_label.color = gold
                leaderboard_label.color = gold
            menu_label.color = gold
        elif not finding and leaderboard_screen:
            # Back Button
            if 790 <= x <= 955 and 30 <= y <= 75:
                window.set_mouse_cursor(window.get_system_mouse_cursor(window.CURSOR_HAND))
                leaderboard_label.color = grey
            else:
                window.set_mouse_cursor(window.get_system_mouse_cursor(window.CURSOR_DEFAULT))
                leaderboard_label.color = gold
            play_label.color = gold
            instruction_label.color = gold
            quit_label.color = gold
            menu_label.color = gold
        elif not finding and instructions_screen:
            # Back Button
            if 790 <= x <= 955 and 30 <= y <= 75:
                window.set_mouse_cursor(window.get_system_mouse_cursor(window.CURSOR_HAND))
                instruction_label.color = aqua
            else:
                window.set_mouse_cursor(window.get_system_mouse_cursor(window.CURSOR_DEFAULT))
                instruction_label.color = gold
            play_label.color = gold
            leaderboard_label.color = gold
            quit_label.color = gold
            menu_label.color = gold
        else:
            # Menu Button
            if 410 <= x <= 585 and 24 <= y <= 68:
                window.set_mouse_cursor(window.get_system_mouse_cursor(window.CURSOR_HAND))
                menu_label.color = white
            else:
                window.set_mouse_cursor(window.get_system_mouse_cursor(window.CURSOR_DEFAULT))
                menu_label.color = gold
            play_label.color = gold
            instruction_label.color = gold
            quit_label.color = gold
            leaderboard_label.color = gold

    @window.event
    def on_mouse_press(x, y, button, modifiers):
        """
        :param x: Mouse x
        :param y: Mouse y
        :param button: Which button in the mouse was pressed (left/right/middle).
        :param modifiers: Whether any keyboard key was pressed during the mouse press.

        The function is called every time the mouse is pressed.
        it checks whether the mouse is currently on a certain
        label or object and if so, it calls functions or contacts the server accordingly.
        """

        global finding
        global instructions_screen
        global leaderboard_screen
        global visible

        if button == mouse.LEFT:

            if not finding and not instructions_screen and not leaderboard_screen:
                # Play Button
                if 20 <= x <= 160 and 285 <= y <= 330:

                    global my_socket
                    global username
                    global server_up
                    global player

                    try:
                        my_socket.send("play: " + str(username))
                        player = my_socket.recv(32)
                        visible[7] = False
                        visible[6] = False
                        visible[5] = True
                        visible[4] = False
                        visible[3] = True
                        visible[2] = False
                        visible[1] = False
                        visible[0] = False

                        if player == "1":
                            pyglet.clock.schedule_interval(find, 0.1)
                            finding = True

                        elif player == "2":
                            window.close()
                            game()
                    except:
                        visible[4] = True

                # Instruction Button
                elif 20 <= x <= 425 and 160 <= y <= 200:
                    instructions_screen = True
                    instruction_label.text = "               Back"
                    instruction_label.x = leaderboard_label.x
                    instruction_label.y = leaderboard_label.y
                    visible = [False, True, False, False, False, False, False, False]

                # Quit Button
                elif 20 <= x <= 160 and 25 <= y <= 70:
                    window.close()

                # Leaderboard Button
                elif 550 <= x <= 965 and 30 <= y <= 75:
                    global leaderboard_labels
                    try:
                        my_socket.send("leaderboard")
                        leaderboard = pickle.loads(my_socket.recv(1024))
                        profile = "".join(stats_label.text.split(" "))
                        leaderboard_labels = [pyglet.text.Label(text="You: " + str(profile), x=window.width/2 + 100,
                                                                y=window.height/2 + 25, font_name=Cooper_Black, bold=True,
                                                                font_size=40, color=gold, multiline=True, width=10)]
                        for i in xrange(len(leaderboard)):
                            leaderboard_labels.append(pyglet.text.Label(text=leaderboard[i], bold=True, x=50,
                                                                        y=window.height/2 + 50 - leaderboard_space*i,
                                                                        font_name=Cooper_Black, font_size=40, color=gold))
                        leaderboard_screen = True
                        leaderboard_label.text = "               Back"
                        visible = [False, False, False, False, False, False, False, True]
                    except:
                        visible[4] = True

            elif not finding and instructions_screen:
                # Back Button
                if 790 <= x <= 955 and 30 <= y <= 75:
                    instructions_screen = False
                    instruction_label.text = "Instructions"
                    instruction_label.x = 20
                    instruction_label.y = 160
                    visible = [True, True, True, False, False, False, True, True]

            elif not finding and leaderboard_screen:
                # Back Button
                if 790 <= x <= 955 and 30 <= y <= 75:
                    leaderboard_screen = False
                    leaderboard_label.text = "Leaderboard"
                    visible = [True, True, True, False, False, False, True, True]

            else:
                # Menu Button
                if 410 <= x <= 585 and 24 <= y <= 68:
                    my_socket.send("leave")
                    finding = False

    pyglet.app.run()


def connect():
    """
    This function connects the client to the server
    if he is not connected.
    """

    global my_socket
    global ip
    global running

    while running:
        try:
            my_socket.send("test")
        except:
            my_socket = socket.socket()
            try:
                my_socket.connect((ip, server_port))
                if username is not None:
                    my_socket.send("online: " + str(username))
            except:
                pass
        time.sleep(0.2)


def get_ip_list():
    arp = subprocess.check_output("arp -a").decode('utf-8')
    lines = arp.split("\n")
    ip = lines[1].lstrip()
    ip = ip[ip.find(" ") + 1:]
    ip = str(ip[:ip.find(" ")])
    start_lines = []
    for i in range(0, len(lines)):
        line = lines[i].lstrip()
        line2 = str(line[:line.find(" ")])
        start_lines.append(line2)
    ip_list = [ip]
    for line in start_lines:
        if line[:line.find(".")] == ip[:ip.find(".")] and not line.endswith('1') and not line.endswith('255'):
            ip_list.append(line)
    return ip_list


def login():
    """
    This function is responsible for everything in the region
    of the login screen in which the user can either login to his account
    or create a new account.
    """

    global exit_app
    global my_socket
    global username
    global score

    def waiting_for_server():
        """
        This function waits  untill the server is up
        """

        global my_socket
        global ip
        global running

        # my_socket = socket.socket()
        # ip_list = get_ip_list()
        # found = False
        # while running and not found:
        #     for address in ip_list:
        #         try:
        #             my_socket.connect((address, server_port))
        #             ip = address
        #             found = True
        #             break
        #         except:
        #             try:
        #                 root.winfo_exists()
        #                 if address == ip_list[-1]:
        #                     time.sleep(0.1)
        #             except:
        #                 return
        # ---------------------------
        # my_socket = socket.socket()
        # ip = '127.0.0.1'
        # while running:
        #     try:
        #         my_socket.connect((ip, server_port))
        #         break
        #     except:
        #         try:
        #             root.winfo_exists()
        #             time.sleep(0.1)
        #         except:
        #             return
        try:
            # labels
            waiting_label.grid(row=100, column=100)
            waiting_label.config(text="", font="Times 0")
            title_label.grid(row=0, column=1)
            username_label.grid(row=2, column=0, sticky=E)
            password_label.grid(row=3, column=0, sticky=E)
            # entries
            username_entry.grid(row=2, column=1)
            password_entry.grid(row=3, column=1)
            # buttons
            finish_button.grid(row=6, column=3)
            change_button.grid(row=7, column=1)

            t = threading.Thread(target=connect)
            t.start()
        except:
            pass

    def change_screen():
        """
        This Function is changing the screen either
        from the login screen to the registration screen or
        from the registration screen to the login screen.
        """

        if title_label.cget("text") == "Login":
            title_label.config(text="Register", font='Times 32')
            finish_button.config(text="Register")
            change_button.config(text="Sign In")
            confirm_label.grid(row=4, column=0)
            confirm_entry.grid(row=4, column=1)
        else:
            title_label.config(text="Login", font='Times 40')
            finish_button.config(text="Login")
            change_button.config(text="Sign Up")
            confirm_label.grid_forget()
            confirm_entry.grid_forget()
        username_entry.delete(0, 'end')
        password_entry.delete(0, 'end')
        confirm_entry.delete(0, 'end')
        error_label.grid_forget()

    def check_details():
        """
        This function checks the values in the entry boxes and
        if the values are matching then it logs the user into the
        game menu.
        """

        global exit_app
        global my_socket
        global username
        global score

        # Register
        if title_label.cget("text") == "Register":
            if username_entry.get().isalnum() and password_entry.get().isalnum() and confirm_entry.get().isalnum():
                if 2 < len(username_entry.get()) < 15:
                    if password_entry.get() == confirm_entry.get():
                        try:
                            my_socket.send("register: " + str(username_entry.get()) + " " + str(password_entry.get()))
                            data = my_socket.recv(1024)
                            if data == "valid":
                                username_entry.delete(0, 'end')
                                password_entry.delete(0, 'end')
                                confirm_entry.delete(0, 'end')
                                error_label.config(text="Successfully registered!", fg='darkgreen')
                                error_label.grid(row=5, column=1)
                            else:
                                error_label.config(text="Username already exists", fg='red')
                                error_label.grid(row=5, column=1)
                        except:
                            error_label.config(text="Server isn't up!", fg='red')
                            error_label.grid(row=5, column=1)

                    else:
                        error_label.config(text="Passwords don't match!", fg='red')
                        error_label.grid(row=5, column=1)
                else:
                    error_label.config(text="username length allowed: 3-14 letters!", fg='red')
                    error_label.grid(row=5, column=1)
            else:
                error_label.config(text="Invalid details", fg='red')
                error_label.grid(row=5, column=1)

        # Login
        elif len(username_entry.get()) > 0 and len(password_entry.get()) > 0:
            try:
                my_socket.send("login: " + str(username_entry.get()) + " " + str(password_entry.get()))
                data = my_socket.recv(1024)
                valid_data = data.split(",")
                if len(valid_data) == 2:
                    username = username_entry.get()
                    score = valid_data[1]
                    username_entry.delete(0, 'end')
                    password_entry.delete(0, 'end')
                    confirm_entry.delete(0, 'end')
                    root.destroy()
                    exit_app = False
                elif data == "invalid":
                    error_label.config(text="Username/Password is incorrect", fg='red')
                    error_label.grid(row=5, column=1)
                else:
                    error_label.config(text="User already logged in", fg='red')
                    error_label.grid(row=5, column=1)
            except:
                error_label.config(text="Server isn't up!", fg='red')
                error_label.grid(row=5, column=1)
        else:
            error_label.config(text="Fill all the details!", fg='red')
            error_label.grid(row=5, column=1)

    # window
    root = Tk()
    root.geometry("+800+300")
    root.configure(background='green')
    root.resizable(False, False)

    # labels
    title_label = Label(root, text="Login", bg='green', fg='gold', font='Times 40')
    username_label = Label(root, text="Username", bg='green')
    password_label = Label(root, text="Password", bg='green')
    confirm_label = Label(root, text="Confirm\nPassword", bg='green')
    error_label = Label(root, fg='red', bg='green')
    waiting_label = Label(root, text="Waiting for\nserver to go up...", fg='gold', bg='green', font='Times 48')
    waiting_label.grid()

    # entries
    username_entry = Entry(root, width=20)
    password_entry = Entry(root, width=20, show="*")
    confirm_entry = Entry(root, width=20, show="*")

    # buttons
    finish_button = Button(root, text="Login", command=check_details)
    change_button = Button(root, text="Sign Up", command=change_screen)

    t = threading.Thread(target=waiting_for_server)
    t.start()
    root.mainloop()


def get_server_ip():

    global my_socket
    global ip

    def check_ip():

        global ip
        global my_socket

        ip = ip_entry.get()
        val_list = ip.split(".")
        if len(val_list) == 4:
            my_socket = socket.socket()
            try:
                my_socket.connect((ip, server_port))
                root.destroy()
                login()
            except:
                msg_label.config(text="Format: x.x.x.x\nNo Server Found")
                ip_entry.delete(0, END)
        else:
            msg_label.config(text="Format: x.x.x.x\nInvalid IP")
            ip_entry.delete(0, END)

    def get_localhost():

        ip_entry.delete(0, END)
        ip_entry.insert(0, localhost)

    # window
    root = Tk()
    root.geometry("+800+300")
    root.configure(background='green')
    root.resizable(False, False)

    # labels
    ip_label = Label(root, text="Enter Server IP", bg='green', fg='gold', font='Times 16')
    msg_label = Label(root, text="Format: x.x.x.x", bg='green', fg='red', font='Times 16')
    ip_label.grid(row=0, column=0)
    msg_label.grid(row=3, column=0)

    # entries
    ip_entry = Entry(root, width=20)
    ip_entry.grid(row=1, column=0)

    # buttons
    ip_button = Button(root, text="Connect", command=check_ip)
    localhost_button = Button(root, text="localhost", command=get_localhost)
    ip_button.grid(row=1, column=1)
    localhost_button.grid(row=2, column=1)

    root.mainloop()


if __name__ == '__main__':

    my_socket = None
    ip = None
    username = None
    score = None
    exit_app = True
    running = True

    get_server_ip()

    while not exit_app:
        exit_app = True

        server_up = None
        player = None
        visible = None
        finding = None
        game_visible = None
        placing = None
        placing_label = None
        end_label = None
        enemy_label = None
        my_placing = None
        turn = None
        frame = None
        animation = None
        count = None
        instructions_screen = None
        leaderboard_screen = None
        leaderboard_labels = []
        player_board = []
        enemy_board = []

        menu()

    try:
        my_socket.send("")
        my_socket.close()
        print "closed"
    except:
        pass
    running = False
