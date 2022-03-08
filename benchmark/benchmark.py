import requests
import math
import multiprocessing as mp
import argparse
import sys
import random
import time

results = []
requests_output_file = "/tmp/mazes_benchmark_metrics_requests.csv"
queries_output_file = "/tmp/mazes_benchmark_metrics_queries.csv"

def init_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', type=str, required=False,
            help="HOST:PORT to send the HTTP requests to\
                    Default=http://localhost", default="http://localhost")
    parser.add_argument('--maze_size', type=int, required=False,
            help="Maximum dimensions of the mazes to be generated\
                    Default=50(50x50 grid)", default=50)
    parser.add_argument('--subprocesses', type=int, required=False,
            help="Number of maximum processes to spawn\
                Default=5", default=5)
    parser.add_argument('--query_highscores', type=int, required=False,
            help="Number of rows to scan for the complex queries benchmark\
                Default=10000", default=10000)
    parser.add_argument('--query_users', type=int, required=False,
            help="Spread entries among this number of users for the complex queries benchmark\
                Default=100", default=100)
    parser.add_argument('--verbose', action="store_true",
            help="Extra verbosity")

    global ARGS
    ARGS = parser.parse_args()
    print(ARGS)

def generate_random_datetime():
    year = random.randint(1,10000)
    month = random.randint(1,12)
    day = random.randint(1,28)
    hour = random.randint(1,23)
    minute = random.randint(1,59)
    second = random.randint(1,59)
    return f"{year}-{month}-{day} {hour}:{minute}:{second}"

def register_user():
    # Insert query
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
    # No query
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
    # Insert
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
    # Select query
    endpoint = "/mazes/" + mazeId + "/solve"
    headers = {
        "authorisation" : token        
    }

    r = requests.get(url = ARGS.url + endpoint, headers = headers)
    data = r.json()
    if ARGS.verbose:
        print("Maze solution response: " + str(data))

    return data

def addHighscore(mazeId, token, score, created_at):
    # Insert query
    endpoint = "/mazes/" + mazeId + "/highscores"
    headers = {
        "authorisation" : token        
    }
    body = {
        "score" : score,
        "created_at" : created_at,
    }
    r = requests.post(url = ARGS.url + endpoint, headers = headers, data = body)
    data = r.json()
    if ARGS.verbose:
        print("Add highscore response: " + str(data))

    return data

def getBestScoreUser(mazeId, token):
    # Select query
    endpoint = "/mazes/" + mazeId + "/bestScoreUser"
    headers = {
        "authorisation" : token        
    }

    r = requests.get(url = ARGS.url + endpoint, headers = headers)
    data = r.json()
    if ARGS.verbose:
        print("Best score user" + str(data))

    return data

def getMazeAverageScore(mazeId, token):
    # Select query
    endpoint = "/mazes/" + mazeId + "/hsAvg"
    headers = {
        "authorisation" : token        
    }

    r = requests.get(url = ARGS.url + endpoint, headers = headers)
    data = r.json()
    if ARGS.verbose:
        print("Average score: " + str(data))

    return data

def load_highscore_data(num_highscores, num_users):
    try:
        reg_tokens = []
        # Register the users
        for i in range(num_users):
            reg_tokens.append(register_user()['token'])

        # Create one maze to store the highscores
        random_maze = ''.join(generate_maze(50, reg_tokens[0])['maze'])
        maze_id = add_maze(random_maze, 50, reg_tokens[0])[0]['Id']

        # Add the highscores
        for i in range(num_highscores):
            user = i%len(reg_tokens)
            score = random.randint(1, 65535)
            created_at = generate_random_datetime()
            addHighscore(maze_id, reg_tokens[user], score, created_at)

        return maze_id, reg_tokens[0]
    except Exception as exception:
        print(exception)
        return -1

def stress_app_requests(maze_size):
    try:
        start = time.time()

        # Insert
        reg_token = register_user()['token']
        # No query
        random_maze = ''.join(generate_maze(maze_size, reg_token)['maze'])
        # Insert
        maze_id = add_maze(random_maze, maze_size, reg_token)[0]['Id']
        # Select
        solution = solve_maze(maze_id, reg_token)

        finish = time.time()
        return finish - start
    except Exception as exception:
        print(exception)
        return -1

def stress_app_queries(maze_id, user_token):
    try:
        start = time.time()

        # Select
        mazeAvgScore = getMazeAverageScore(maze_id, user_token)
        # Select
        bestScoreUser = getBestScoreUser(maze_id, user_token)

        finish = time.time()
        return finish - start
    except Exception as exception:
        print(exception)
        return -1

def collect_results(result):
    global results 
    results.append(result)

def run_benchmark_requests(maze_size, subprocesses):
    global results, requests_output_file

    pool = mp.Pool(subprocesses)
    for i in range(subprocesses):
        pool.apply_async(stress_app_requests, args=(maze_size,), callback=collect_results)
    pool.close()
    pool.join()

    results = [res for res in results if res != -1]
    avg_suite_time = sum(results) / len(results)
    max_suite_time = max(results)
    min_suite_time = min(results)
    results = []

    with open(requests_output_file, "a") as f:
        f.write(",".join([str(subprocesses), str(maze_size), str(avg_suite_time), str(max_suite_time), str(min_suite_time)]))
        f.write("\n")
        f.close()

def run_benchmark_queries(maze_id, user_token, subprocesses):
    global results, queries_output_file

    pool = mp.Pool(subprocesses)
    for i in range(subprocesses):
        pool.apply_async(stress_app_queries, args=(maze_id, user_token,), callback=collect_results)
    pool.close()
    pool.join()

    results = [res for res in results if res != -1]
    avg_suite_time = sum(results) / len(results)
    max_suite_time = max(results)
    min_suite_time = min(results)
    results = []

    with open(queries_output_file, "a") as f:
        f.write(",".join([str(subprocesses), str(avg_suite_time), str(max_suite_time), str(min_suite_time)]))
        f.write("\n")
        f.close()

def main():
    global requests_output_file, queries_output_file

    init_args()

    with open(requests_output_file, "w") as f:
        f.write("subprocesses,maze_size,avg_suite_time,max_suite_time,min_suite_time\n")
        f.close()

    with open(queries_output_file, "w") as f:
        f.write("subprocesses,avg_suite_time,max_suite_time,min_suite_time\n")
        f.close()

    total_iterations = (ARGS.subprocesses - 1) * (ARGS.maze_size - 4)
    idx = 0
    last_percent = 0
    maze_id, user_token = load_highscore_data(ARGS.query_highscores, ARGS.query_users)
    for subprocess_amt in range(2, ARGS.subprocesses + 1):
        run_benchmark_queries(maze_id, user_token, subprocess_amt)
        for maze_size in range(5, ARGS.maze_size + 1):
            idx += 1
            percentage_complete = (idx / total_iterations) * 100
            if percentage_complete % 2 < 1 and math.floor(percentage_complete) > last_percent:
                last_percent = math.floor(percentage_complete)
                print("Percentage complete: " + str(last_percent))
            run_benchmark_requests(maze_size, subprocess_amt)

if __name__ == "__main__":
    main()
