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
MAZE_ID_HIGHSCORE_DATA = 1

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
    parser.add_argument('--outputdir', type=str, required=False,
            help="Directory to output the metrics to\
                Default=/metrics/benchmark", default="/metrics/benchmark")
    parser.add_argument('--verbose', action="store_true",
            help="Extra verbosity")

    global ARGS
    ARGS = parser.parse_args()
    print(ARGS)

def establish_connection():
    endpoint = "/healthcheck/db"
    status_code = -1
    retry_counter = 0
    while status_code != 200:
        time.sleep(5)
        try:
            if ARGS.verbose:
                print("Trying to reach server healthcheck endpoint")
            r = requests.get(url = ARGS.url + endpoint, timeout=5)
            status_code = r.status_code
        except Exception as exception:
            print("Healthcheck failed, will retry again: " + str(exception))
        if ARGS.verbose:
            print("Healthcheck response:" + str(status_code))

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

def login_test_user():
    # Insert query
    endpoint = "/auth/login"
    body = {
        "email" : "test1@test.com",
        "password" : "password"
    }
    r = requests.post(url = ARGS.url + endpoint, data = body)
    data = r.json()
    if ARGS.verbose:
        print("Login response: " + str(data))
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

def getBestScoreUser(mazeId, token):
    # Select query
    endpoint = "/mazes/" + str(mazeId) + "/bestScoreUser"
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
    endpoint = "/mazes/" + str(mazeId) + "/hsAvg"
    headers = {
        "authorisation" : token        
    }

    r = requests.get(url = ARGS.url + endpoint, headers = headers)
    data = r.json()
    if ARGS.verbose:
        print("Average score: " + str(data))

    return data

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
    establish_connection()
    # with open(requests_output_file, "w") as f:
    #     f.write("subprocesses,maze_size,avg_suite_time,max_suite_time,min_suite_time\n")
    #     f.close()

    # with open(queries_output_file, "w") as f:
    #     f.write("subprocesses,avg_suite_time,max_suite_time,min_suite_time\n")
    #     f.close()

    # total_iterations = (ARGS.subprocesses - 1) * (ARGS.maze_size - 4)
    # idx = 0
    # last_percent = 0
    # user_token = login_test_user()['token']
    # for subprocess_amt in range(2, ARGS.subprocesses + 1):
    #     run_benchmark_queries(MAZE_ID_HIGHSCORE_DATA, user_token, subprocess_amt)
    #     for maze_size in range(5, ARGS.maze_size + 1):
    #         idx += 1
    #         percentage_complete = (idx / total_iterations) * 100
    #         if percentage_complete % 2 < 1 and math.floor(percentage_complete) > last_percent:
    #             last_percent = math.floor(percentage_complete)
    #             print("Percentage complete: " + str(last_percent))
    #         run_benchmark_requests(maze_size, subprocess_amt)



    with open("/metrics/benchmark/metrics.prom", "w+") as f:
        f.write("aorf_metric_test 1\n")
        f.close()

if __name__ == "__main__":
    main()
