import time
import requests
import sys
import random
import argparse
from prometheus_client import start_http_server, Gauge, Counter

def init_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', type=str, required=False,
            help="HOST:PORT to send the HTTP requests to\
                    Default=http://localhost", default="http://localhost")
    parser.add_argument('--prom_server_port', type=int, required=False,
            help="Port at which prometheus will expose the data\
                    Default=8001", default=8001)
    parser.add_argument('--request_interval', type=int, required=False,
            help="Time interval between each wave of requests\
                    Default=5", default=5)
    parser.add_argument('--request_timeout', type=int, required=False,
            help="Timeout limit for the requests\
                    Default=200", default=200)
    parser.add_argument('--maze_size', type=int, required=False,
            help="Size of mazes to generate and solve\
                    Default=25", default=25)
    parser.add_argument('--verbose', action="store_true",
            help="Extra verbosity")

    global ARGS
    ARGS = parser.parse_args()
    print(ARGS)

class Request:
    def __init__(self, name, url, endpoint, method, authorised = False):
        self.name = name
        self.url = url
        self.endpoint = endpoint
        self.method = method
        self.authorised = authorised

    def get_name(self):
        return self.name

    def send_request(self, data = {}, **kwargs):
        global ARGS
        if self.method == "POST":
            return requests.post(url = self.url + self.endpoint.format(**kwargs), data = data,
                    headers = {} if not self.authorised else {"authorisation": kwargs["token"]}, timeout = ARGS.request_timeout)
        elif self.method == "GET":
            return requests.get(url = self.url + self.endpoint.format(**kwargs),
                    headers = {} if not self.authorised else {"authorisation": kwargs["token"]}, timeout = ARGS.request_timeout)
        else:
            return None

    def get_labels(self):
        return (self.endpoint, self.method)

class RequestUtils:

    @staticmethod
    def get_signup_body():
        user = "user" + str(random.randint(1,sys.maxsize))
        body = {
            "email" : user + "@test.com",
            "username" : user,
            "password" : "password",
            "passConfirmation" : "password"
        }
        return body

    @staticmethod
    def get_login_body():
        return {
            "email" : "test1@test.com",
            "password" : "password",
        }

    @staticmethod
    def get_add_maze_body(maze = None, size = None):
        if size is None:
            size = 15
        if maze is None:
            maze = ["." for i in range(size*size)]
            start_idx = random.randint(0, size*size -1)
            end_idx = random.randint(0,start_idx) if start_idx > 0 else random.randint(start_idx, size*size - 1)
            maze[start_idx] = "S"
            maze[end_idx] = "T"
            maze = "".join(maze)
        return {"maze": maze, "sizeX": size}

    @staticmethod
    def get_generate_maze_body(size = None):
        if size is None:
            size = 15
        return {"size": size}

    @staticmethod
    def get_default_maze_id():
        return 1

class RequestExecutor:
    def __init__(self, url):
        self.url = url
        self.user_token = None
        self.request_time = Gauge('benchmark_request_processing_seconds', 'Time spent processing benchmark requests', ['endpoint', 'method', 'status_code'])
        self.query_type_counter = Counter('benchmark_query_type_count', 'Amount of queries executed from the benchmark per type (select, insert)', ['query_type'])

        # /auth
        self.signup_req = Request("signup", self.url, "/auth/signup", "POST") 
        self.login_req = Request("login", self.url, "/auth/login", "POST") 
        self.logout_req = Request("logout", self.url, "/auth/logout", "POST", True) 

        # /healthcheck
        self.db_healthcheck_req = Request("db_healthcheck", self.url, "/healthcheck/db", "GET") 

        # /mazes
        self.add_maze_req = Request("add_maze", self.url, "/mazes", "POST", True) 
        self.get_mazes_req = Request("get_mazes", self.url, "/mazes", "GET", True) 
        self.get_maze_req = Request("get_maze", self.url, "/mazes/{mazeId}", "GET", True) 
        self.generate_maze_req = Request("generate_maze", self.url, "/mazes/generate", "POST", True) 
        self.solve_maze_req = Request("solve_maze", self.url, "/mazes/{mazeId}/solve", "GET", True) 
        self.get_maze_hs_avg_req = Request("get_maze_hs_avg", self.url, "/mazes/{mazeId}/hsAvg", "GET", True) 
        self.get_maze_best_scorer_req = Request("get_maze_best_scorer", self.url, "/mazes/{mazeId}/bestScoreUser", "GET", True) 
        self.heavy_query_req = Request("heavy_query", self.url, "/mazes/heavyQuery", "GET", True) 


    def get_token(self):
        if self.user_token is None:
            self.user_token = self.login().get('response_body')["token"]
        return self.user_token

    def send_request(self, request, **kwargs):
        global ARGS
        try:
            start = time.time()
            response = request.send_request(**kwargs)
            finish  = time.time()
            self.request_time.labels(*request.get_labels(), response.status_code).set(finish-start)
            ret = {"request": request, "response_body": response.json(), "status_code": response.status_code, "time": finish - start}
        except Exception as e:
            print(e)
            ret = {"request": request, "response_body": None, "status_code": None, "time": -1}
        finally:
            if ARGS.verbose:
                print(f"Sent request: {ret.get('request').get_labels()} got status_code: {ret.get('status_code')} in time {ret.get('time')}")
            return ret

    def signup(self, body = None):
        if body is None:
            body = RequestUtils.get_signup_body()
        ret = self.send_request(self.signup_req, data = body)
        self.query_type_counter.labels('insert').inc()
        return ret

    def login(self, body = RequestUtils.get_login_body()):
        ret = self.send_request(self.login_req, data = body)
        self.query_type_counter.labels('select').inc()
        return ret

    def logout(self, token = None):
        if token is None:
            token = self.get_token()
        self.user_token = None
        ret = self.send_request(self.logout_req, token = token)
        self.query_type_counter.labels('insert').inc()
        return ret

    def db_healthcheck(self):
        ret = self.send_request(self.db_healthcheck_req)
        # self.query_type_counter.labels('select').inc()
        return ret

    def add_maze(self, maze = None, size = None, token = None):
        if token is None:
            token = self.get_token()
        body = RequestUtils.get_add_maze_body(maze, size)
        ret = self.send_request(self.add_maze_req, data = body, token = token)
        self.query_type_counter.labels('insert').inc()
        return ret

    def get_mazes(self, token = None):
        if token is None:
            token = self.get_token()
        ret = self.send_request(self.get_mazes_req, token = token)
        self.query_type_counter.labels('select').inc()
        return ret

    def get_maze(self, mazeId = RequestUtils.get_default_maze_id(), token = None):
        if token is None:
            token = self.get_token()
        ret = self.send_request(self.get_maze_req, mazeId = mazeId, token = token)
        self.query_type_counter.labels('select').inc()
        return ret

    def generate_maze(self, size = None, token = None):
        if token is None:
            token = self.get_token()
        body = RequestUtils.get_generate_maze_body(size)
        ret = self.send_request(self.generate_maze_req, data = body, token = token)
        return ret

    def solve_maze(self, mazeId = RequestUtils.get_default_maze_id(), token = None):
        if token is None:
            token = self.get_token()
        ret = self.send_request(self.solve_maze_req, mazeId = mazeId, token = token)
        self.query_type_counter.labels('select').inc()
        return ret

    def get_maze_hs_avg(self, mazeId = RequestUtils.get_default_maze_id(), token = None):
        if token is None:
            token = self.get_token()
        ret = self.send_request(self.get_maze_hs_avg_req, mazeId = mazeId, token = token)
        self.query_type_counter.labels('select').inc()
        return ret

    def get_maze_best_scorer(self, mazeId = RequestUtils.get_default_maze_id(), token = None):
        if token is None:
            token = self.get_token()
        ret = self.send_request(self.get_maze_best_scorer_req, mazeId = mazeId, token = token)
        self.query_type_counter.labels('select').inc()
        return ret

    def heavy_query(self, token = None):
        if token is None:
            token = self.get_token()
        ret = self.send_request(self.heavy_query_req, token = token)
        self.query_type_counter.labels('select').inc()
        return ret

def main():
    global ARGS

    init_args()
    executor = RequestExecutor(ARGS.url)
    start_http_server(ARGS.prom_server_port)

    server_healthy = executor.db_healthcheck().get('status_code')
    while server_healthy is None or server_healthy != 200:
        print("trying to connect...")
        time.sleep(3)
        server_healthy = executor.db_healthcheck().get('status_code')


    while True:
        try:
            executor.signup()
            executor.login()
            new_maze = "".join(executor.generate_maze(ARGS.maze_size)['response_body']['maze'])
            maze_id = executor.add_maze(new_maze, ARGS.maze_size)['response_body'][0]['Id']
            executor.solve_maze(maze_id)
            executor.get_maze_hs_avg()
            executor.get_maze_best_scorer()
        except Exception as e:
            print(e)
        finally:    
            time.sleep(ARGS.request_interval)

main()
