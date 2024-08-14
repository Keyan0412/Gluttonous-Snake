import turtle
from time import time
from random import randrange, randint, choice
from functools import partial


def config_screen():
    """
    configure the setting of the screen
    """
    s = turtle.Screen()
    s.tracer(0)
    s.title("Snake")
    s.setup(500+120, 500+120+80)
    s.mode("standard")
    return s


def create_turtle(x, y, color="red", border="black"):
    """
    create turtle in particular mode
    """
    t = turtle.Turtle("square")
    t.color(border, color)
    t.pu()
    t.goto(x, y)
    return t


def config_contents():
    """
    configure the contents of screen
    """
    global g_tip, g_status

    # motion and status border
    m = create_turtle(0, -40, "", "black")
    m.shapesize(25, 25, 5)
    s = create_turtle(0, 250, "", "black")
    s.shapesize(4, 25, 5)

    tip = create_turtle(-200, 100)
    tip.hideturtle()
    tip.write("Snake game\nClick anywhere to start the game, and enjoy it!", font=("Arial", 16, "normal"))
    status = create_turtle(-200, 250, "", "black")
    status.hideturtle()
    return tip, status


def update_status():
    """
    update the status when the contents change
    """
    g_status.clear()
    g_status.write(f"Contact: {g_contact}       Time: {g_show_time}       Motion: {g_key}",
                   font=("Arial", 15, "bold")
                   )
    g_screen.update()


def config_characters():
    """
    configure snake, monster and food
    """
    global g_snake, g_monster, g_snake_pos, g_food
    g_snake = create_turtle(0, 0)
    g_snake_pos = [13, 15]

    # make sure snake and monster is far enough at the beginning
    while True:
        temp_x_mon, temp_y_mon = randrange(-210, 210, 20), randrange(-250, 10, 20)
        if temp_x_mon**2 + temp_y_mon**2 >= 2500:
            break
    g_monster = create_turtle(temp_x_mon, temp_y_mon, "purple", "purple")

    # config food
    g_food = {}
    for order in range(1, 6):
        while True:
            temp_position = (randint(1, 25), randint(1, 25))
            if temp_position not in g_food.values() and temp_position != tuple(g_snake_pos):
                turtle_food = create_turtle(temp_position[0]*20-264, temp_position[1]*20-314)
                turtle_food.hideturtle()
                g_food[turtle_food] = [temp_position, order, True]
                break
    return g_snake, g_monster, g_food


def start(x, y):
    """
    start the game when click
    """
    global g_time
    g_screen.onscreenclick(None)
    g_tip.clear()

    # show the food
    for turtle_food in g_food.keys():
        turtle_food.write(g_food[turtle_food][1], font=("Arial", 15, "bold"))

    # start the timer
    g_time = time()
    timer()

    g_screen.onkey(partial(user_input, "Up"), "Up")
    g_screen.onkey(partial(user_input, "Down"), "Down")
    g_screen.onkey(partial(user_input, "Left"), "Left")
    g_screen.onkey(partial(user_input, "Right"), "Right")
    g_screen.onkey(pause, "space")

    g_screen.ontimer(snake_motion, 100)
    g_screen.ontimer(monster_motion, 1000)
    g_screen.ontimer(hide_food, 5000)


def timer():
    """
    record the time
    """
    global g_show_time
    if g_end:
        return None
    gap = time() - g_time
    second = int(gap)
    if second != g_show_time:
        g_show_time = second
        update_status()
    g_screen.ontimer(timer, 100)


def pause():
    """
    stop snake when pause the game
    """
    global g_key, g_last_key
    if g_key != 'Pause':
        g_last_key = g_key
        g_key = 'Pause'
    else:
        g_key = g_last_key
        g_last_key = None
    update_status()


def user_input(press):
    """
    get input from user and change the direction of snake
    """
    global g_key, g_direction
    if not g_end:
        g_key = press
        if g_key in g_angle.keys():
            g_direction = g_angle[g_key]
            g_snake.setheading(g_direction)
        update_status()


def monster_motion():
    """
    control the motion of monster
    it will move towards the snake
    """
    if g_end:
        if g_end == 2:
            g_monster.write("Game over!!", align='left', font=("Arial", 15, "bold"))
        return None

    # calculate the direction of monster
    snake_x, snake_y = g_snake.position()
    monster_x, monster_y = g_monster.position()
    dif_x, dif_y = snake_x - monster_x, snake_y - monster_y
    if abs(dif_y) > abs(dif_x):
        if dif_y > 0:
            direction_mon = 90
        else:
            direction_mon = 270
    else:
        if dif_x > 0:
            direction_mon = 0
        else:
            direction_mon = 180
    g_monster.setheading(direction_mon)
    g_monster.forward(20)
    g_screen.update()

    check_monster()
    check_contact()

    g_screen.ontimer(monster_motion, randint(370, 680))


def check_contact():
    """
    control the value of contact
    """
    global g_contact
    x, y = g_monster.position()
    for s in g_stamps:
        if (20*s[0]-260-x)**2 + (20*s[1]-300-y)**2 < 250:
            # if one of the body is close to monster
            g_contact += 1
            update_status()
            break


def snake_motion():
    """
    control the action of snake
    """
    global g_snake, g_stamps

    check_food()
    if g_end:
        if g_end == 1:
            g_snake.write("Winner!!", align="left", font=("Arial", 15, "bold"))
        return None

    if g_key and g_key != 'Pause' and check():

        # stamp body
        g_snake.color("blue", "black")
        g_snake.stamp()
        g_stamps.append(tuple(g_snake_pos))
        g_snake.color("red")

        # remove stamps to maintain length of body
        if len(g_stamps) > g_size:
            g_snake.clearstamps(1)
            g_stamps = g_stamps[1:]

        g_snake.forward(20)
        record_motion()

        check_food()
        check_monster()

        g_screen.update()
    # decide different speed for snakes when lengthening
    if len(g_stamps) < g_size:
        g_screen.ontimer(snake_motion, 600)
    else:
        g_screen.ontimer(snake_motion, 380)


def check():
    """
    check whether the snake collides with the border or its body
    """
    border = 0
    if (g_direction == 0 and g_snake_pos[0] <= 24) or (g_direction == 180 and g_snake_pos[0] >= 2):
        border = 1
    elif (g_direction == 90 and g_snake_pos[1] <= 24) or (g_direction == 270 and g_snake_pos[1] >= 2):
        border = 1

    body = 1
    if g_direction == 0 or g_direction == 180:
        if (g_snake_pos[0]+1-int(g_direction/90), g_snake_pos[1]) in g_stamps:
            body = 0
    else:
        if (g_snake_pos[0], g_snake_pos[1]+2-int(g_direction/90)) in g_stamps:
            body = 0

    if border and body:
        return True


def check_food():
    """
    check whether the food contacts the snake
    """
    global g_food, g_size, g_end
    for num in g_food.keys():
        if g_food[num][0] == tuple(g_snake_pos) and g_food[num][2]:
            g_size += g_food[num][1]
            g_food[num][1] = 0
            num.clear()

    # check whether snake eats up the food
    for order in g_food.values():
        if order[1] != 0:
            break
    else:
        if len(g_stamps) == g_size:
            g_end = 1


def check_monster():
    """
    check whether monster contacts the head of snake
    """
    global g_end
    m_x, m_y = g_monster.position()
    s_x, s_y = g_snake.position()
    if (m_x - s_x)**2 + (m_y - s_y)**2 < 250:
        g_end = 2


def record_motion():
    """
    record the position of the snake
    """
    global g_snake_pos
    if g_direction == 0 or g_direction == 180:
        g_snake_pos[0] = g_snake_pos[0] + 1 - int(g_direction / 90)
    else:
        g_snake_pos[1] = g_snake_pos[1] + 2 - int(g_direction / 90)


def hide_food():
    """
    hide or show food randomly
    the food which is invisible cannot be eaten
    """
    global g_food
    if g_end:
        return None
    turtles_food = list(g_food.keys())
    while True:
        pick = choice(turtles_food)
        if g_food[pick][1]:
            if g_food[pick][2]:
                pick.clear()
                g_food[pick][2] = False
            else:
                pick.write(g_food[pick][1], font=("Arial", 15, "bold"))
                g_food[pick][2] = True
            break
    g_screen.ontimer(hide_food, 6000)


if __name__ == "__main__":
    g_angle = {"Up": 90, "Down": 270, "Left": 180, "Right": 0}

    # record progress of game
    g_size = 5
    g_key, g_last_key = None, None
    g_direction = 0
    g_snake_pos = []
    g_stamps = []
    g_time = 0
    g_show_time = 0
    g_end = 0
    g_contact = 0

    # config basic objects
    g_screen = config_screen()
    g_tip, g_status = config_contents()
    update_status()
    g_snake, g_monster, g_food = config_characters()

    # start the game
    g_screen.onscreenclick(start)
    g_screen.update()
    g_screen.listen()
    g_screen.mainloop()
