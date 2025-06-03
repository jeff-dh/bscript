from time import sleep
from random import random

from bscript import task, Running, Failure, sequence, fallback

##### actions #####
def peel_banana():
    if random() < 0.3:
        print("peeling banana failed"); raise Failure()
    print("peeling banana"); yield Running
    # implicit return None / return Success

def eat_apple():
    print("eating apple"); yield Running

def eat_banana():
    if random() < 0.3:
        print("eating banana failed"); raise Failure()
    print("eating banana"); yield Running

def listen_to_the_radio():
    print("~lalala~"); return Running

def handle_emergency():
    print("running"); return Running

##### conditions #####
@task
def emergency():
    if random() > 0.9:
        print("fire! running"); yield Running
        print("fire! running"); yield Running

##### composites #####
def consume_banana():
    yield from sequence(peel_banana(), eat_banana())

@task
def eat():
    yield from fallback(consume_banana(), eat_apple())

def eat_something():
    return (emergency() and handle_emergency()) or (eat() and listen_to_the_radio())

##### main loop #####
for _ in range(20):
    print(eat_something())
    sleep(1)
    print("-----frame-----")
