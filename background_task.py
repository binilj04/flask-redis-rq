import time

def background_task_call(n):

    """ Function that returns len(n) and simulates a delay """

    delay = 1

    print("Task running")
    print(f"Simulating a {delay} second delay")

    time.sleep(delay*int(n))

    print(len(n))
    print("Task complete")

    return n