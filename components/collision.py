import math
import pygame

def check_collision(car, track):
    return not track.is_on_track(car.x, car.y)

def handle_collision(car, track):
    car.apply_stun()

def check_car_collision(car1, car2):
    dx = car1.x - car2.x
    dy = car1.y - car2.y
    distance = math.sqrt(dx * dx + dy * dy)
    radius1 = min(car1.width, car1.height) / 3
    radius2 = min(car2.width, car2.height) / 3
    return distance < (radius1 + radius2)

def handle_car_collision(car1, car2):
    import random
    dx = car1.x - car2.x
    dy = car1.y - car2.y
    distance = math.sqrt(dx * dx + dy * dy)

    if distance == 0:
        dx = random.uniform(-1, 1)
        dy = random.uniform(-1, 1)
        distance = math.sqrt(dx * dx + dy * dy)

    nx = dx / distance
    ny = dy / distance
    pushback_distance = 8

    car1.x += nx * pushback_distance
    car1.y += ny * pushback_distance
    car2.x -= nx * pushback_distance
    car2.y -= ny * pushback_distance

    car1.speed = 0
    car2.speed = 0

    if not car1.stunned:
        car1.stunned = True
        car1.stun_timer = 0.1
        car1.stun_reverse_speed = 0

    if not car2.stunned:
        car2.stunned = True
        car2.stun_timer = 0.1
        car2.stun_reverse_speed = 0