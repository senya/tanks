#!/usr/bin/python3
import sys
import json
import copy
import math
import importlib.machinery
import random


import game
from move import Move

random.seed()

player1 = importlib.machinery.SourceFileLoader('player1',sys.argv[1]).load_module()
player2 = importlib.machinery.SourceFileLoader('player2',sys.argv[2]).load_module()

tanks = [{"health": game.MAX_HEALTH, "timeout": 0, "ind":0, "pos": [25, 25], "name": sys.argv[1]}, {"health": game.MAX_HEALTH, "timeout": 0, "ind":1, "pos": [775, 575], "name": sys.argv[2]}]
bullets = []
bonuses = []

moves = [player1.move, player2.move]

frames = [{'tanks': copy.deepcopy(tanks), 'bullets': [], 'bonuses': []}]

for i in range(int(sys.argv[3])):
    if i % game.BONUS_TIMEOUT == 0:
        bonuses.append({'type': 'med', 'pos': [random.randrange(game.BONUS_RADIUS, game.WIDTH - game.BONUS_RADIUS - 1), random.randrange(game.BONUS_RADIUS, game.HEIGHT - game.BONUS_RADIUS - 1)]})

    tn = copy.deepcopy(tanks)
    bu = copy.deepcopy(bullets)
    bo = copy.deepcopy(bonuses)
    for j in range(len(tanks)):
        t = tanks[j]
        p = t['pos']
        m = Move()
        moves[j](tn[j], tn[:j] + tn[j+1:], bu, bo, m)

        if t['timeout'] > 0:
            t['timeout'] -= 1

        if m.is_shot and t['timeout'] == 0:
            dx = (m.shot_x - p[0])
            dy = (m.shot_y - p[1])
            l = math.sqrt(dx ** 2 + dy ** 2)
            if dx != 0:
                dx /= l
            if dy != 0:
                dy /= l
            x = p[0] + dx * game.TANK_RADIUS
            y = p[1] + dy * game.TANK_RADIUS
            bullets.append({"pos": [x, y], "dir": [dx, dy]})
            t['timeout'] = game.SHOT_TIMEOUT

        l = math.sqrt(m.x ** 2 + m.y ** 2)
        if m.x != 0:
            p[0] += m.x / l * game.TANK_SPEED
        if m.y != 0:
            p[1] += m.y / l * game.TANK_SPEED
        if p[0] < game.TANK_RADIUS:
            p[0] = game.TANK_RADIUS
        if p[1] < game.TANK_RADIUS:
            p[1] = game.TANK_RADIUS
        if p[0] >= game.WIDTH - game.TANK_RADIUS:
            p[0] = game.WIDTH - game.TANK_RADIUS - 1
        if p[1] >= game.HEIGHT - game.TANK_RADIUS:
            p[1] = game.HEIGHT - game.TANK_RADIUS - 1

    for b in bullets:
        b['pos'][0] += b['dir'][0] * game.BULLET_SPEED
        b['pos'][1] += b['dir'][1] * game.BULLET_SPEED
        for t in tanks:
            dx = b['pos'][0] - t['pos'][0]
            dy = b['pos'][1] - t['pos'][1]
            l = math.sqrt(dx ** 2 + dy ** 2)
            if l < game.BULLET_RADIUS + game.TANK_RADIUS:
                b['bang'] = True
                t['health'] -= 10

    for b in bonuses:
        for t in tanks:
            dx = b['pos'][0] - t['pos'][0]
            dy = b['pos'][1] - t['pos'][1]
            l = math.sqrt(dx ** 2 + dy ** 2)
            if l < game.BONUS_RADIUS + game.TANK_RADIUS:
                b['bang'] = True
                t['health'] = min(game.MAX_HEALTH, t['health'] + 20)

    bullets = [b for b in bullets if b['pos'][0] >= game.BULLET_RADIUS and \
                                     b['pos'][1] >= game.BULLET_RADIUS and \
                                     b['pos'][0] < game.WIDTH - game.BULLET_RADIUS and \
                                     b['pos'][1] < game.HEIGHT - game.BULLET_RADIUS and \
                                     not 'bang' in b]

    bonuses = [b for b in bonuses if not 'bang' in b]

    tanks = [t for t in tanks if t['health'] > 0]

    frames.append({'tanks': copy.deepcopy(tanks), 'bullets': copy.deepcopy(bullets), 'bonuses': copy.deepcopy(bonuses)})

    if len(tanks) == 0:
        sys.stderr.write("all dead\n")
        break

    if len(tanks) == 1:
        sys.stderr.write(tanks[0]['name'] + ' win!\n')
        break

if len(tanks) > 1:
    sys.stderr.write('nobody win =(\n')

print(json.dumps(frames))
