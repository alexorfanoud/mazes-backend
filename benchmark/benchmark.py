import requests
import math
import multiprocessing as mp
import argparse
import sys
import random
import time

results = []
output_file = "/tmp/mazes_benchmark_metrics.csv"

def init_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', type=str, required=False,
            help="HOST:PORT to send the HTTP requests to\
                    Default=http://localhost", default="http://localhost")
    parser.add_argument('--repetitions_per_testcase', type=int, required=False,
            help="Number of times each suite will run for a specific configuration (parallel subprocesses + maze size)\
                    Default=1", default=1)
    parser.add_argument('--maze_size', type=int, required=False,
            help="Maximum dimensions of the mazes to be generated\
                    Default=50(50x50 grid)", default=50)
    parser.add_argument('--subprocesses', type=int, required=False,
            help="Number of maximum processes to spawn\
                Default=5", default=5)
    parser.add_argument('--verbose', action="store_true",
            help="Extra verbosity")

    global ARGS
    ARGS = parser.parse_args()
    print(ARGS)


def register_user():
    endpoint = "/auth/signup"
    user = "user" + str(random.randint(1,sys.maxsize))
    body = {
        "email" : user + "@test.com",
        "username" : user,
        "password" : user,
        "passConfirmation" : user
    }
    r = requests.post(url = ARGS.url + endpoint, data = body)
    data = r.json()
    if ARGS.verbose:
        print("Registration response: " + str(data))
    return data

def generate_maze(size, token):
    endpoint = "/mazes/generate"
    headers = {
        "authorisation" : token        
    }
    body = {
        "size" : size
    }

    r = requests.get(url = ARGS.url + endpoint, headers = headers, data = body)
    data = r.json()
    if ARGS.verbose:
        print("Maze generation response: " + str(data))

    return data

def add_maze(maze, size, token):
    endpoint = "/mazes"
    headers = {
        "authorisation" : token        
    }
    body = {
        "maze" : maze,
        "sizeX": size
    }

    r = requests.post(url = ARGS.url + endpoint, headers = headers, data = body)
    data = r.json()
    if ARGS.verbose:
        print("Maze creation response: " + str(data))

    return data

def solve_maze(mazeId, token):
    endpoint = "/mazes/" + mazeId + "/solve"
    headers = {
        "authorisation" : token        
    }

    r = requests.get(url = ARGS.url + endpoint, headers = headers)
    data = r.json()
    if ARGS.verbose:
        print("Maze solution response: " + str(data))

    return data

def stress_app(maze_size, idx):
    try:
        start = time.time()

        reg_token = register_user()['token']
        random_maze = ''.join(generate_maze(maze_size, reg_token)['maze'])
        maze_id = add_maze(random_maze, maze_size, reg_token)[0]['Id']
        solution = solve_maze(maze_id, reg_token)

        finish = time.time()
        return finish - start
    except Exception as exception:
        print(exception)
        return -1

def collect_results(result):
    global results 
    results.append(result)

def run_benchmark(maze_size, subprocesses):
    global results, output_file

    pool = mp.Pool(subprocesses)
    for i in range(subprocesses):
        pool.apply_async(stress_app, args=(maze_size,i,), callback=collect_results)
    pool.close()
    pool.join()

    results = [res for res in results if res != -1]
    avg_suite_time = sum(results) / len(results)
    max_suite_time = max(results)
    min_suite_time = min(results)

    with open(output_file, "a") as f:
        f.write(",".join([str(subprocesses), str(maze_size), str(avg_suite_time), str(max_suite_time), str(min_suite_time)]))
        f.write("\n")
        f.close()

def main():
    global output_file

    init_args()

    with open(output_file, "w") as f:
        f.write("subprocesses,maze_size,avg_suite_time,max_suite_time,min_suite_time\n")
        f.close()

    total_iterations = (ARGS.subprocesses - 1) * (ARGS.maze_size - 4) * ARGS.repetitions_per_testcase
    idx = 0
    last_percent = 0
    for subprocess_amt in range(2, ARGS.subprocesses + 1):
        for maze_size in range(5, ARGS.maze_size + 1):
            for rep in range(ARGS.repetitions_per_testcase):
                idx += 1
                percentage_complete = (idx / total_iterations) * 100
                if percentage_complete % 2 < 1 and math.floor(percentage_complete) > last_percent:
                    last_percent = math.floor(percentage_complete)
                    print("Percentage complete: " + str(last_percent))
                run_benchmark(maze_size, subprocess_amt)

if __name__ == "__main__":
    main()
