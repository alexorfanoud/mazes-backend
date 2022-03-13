import time
import requests
import sys
import random

class Request:
    def __init__(self, url, endpoint, method, authorised = False):
        self.url = url
        self.endpoint = endpoint
        self.method = method
        self.authorised = authorised

    def send_request(self, data = {}, **kwargs):
        if self.method == "POST":
            return requests.post(url = self.url + self.endpoint.format(**kwargs), data = data,
                    headers = {} if not self.authorised else {"authorisation": kwargs["token"]})
        elif self.method == "GET":
            return requests.get(url = self.url + self.endpoint.format(**kwargs),
                    headers = {} if not self.authorised else {"authorisation": kwargs["token"]})
        else:
            return None

    def get_labels(self):
        return (self.endpoint, self.method)

class RequestUtils:

    @staticmethod
    def generate_random_user():
        user = "user" + str(random.randint(1,sys.maxsize)) + str(random.randint(1, sys.maxsize))
        body = {
            "email" : user + "@test.com",
            "username" : user,
            "password" : "password",
            "passConfirmation" : "password"
        }
        return body

    @staticmethod
    def get_default_user():
        return {
            "email" : "test1@test.com",
            "password" : "password",
        }

    @staticmethod
    def generate_random_maze(size = 15):
        maze = ["." for i in range(size*size)]
        start_idx = random.randint(0, size*size -1)
        end_idx = random.randint(0,start_idx) if start_idx > 0 else random.randint(start_idx, size*size - 1)
        maze[start_idx] = "S"
        maze[end_idx] = "T"
        return {"maze": "".join(maze), "sizeX": size}

    @staticmethod
    def get_default_maze_id():
        return 1

class RequestExecutor:
    def __init__(self, url):
        self.url = url

        # /auth
        self.signup_req = Request(self.url, "/auth/signup", "POST") 
        self.login_req = Request(self.url, "/auth/login", "POST") 
        self.logout_req = Request(self.url, "/auth/logout", "POST", True) 

        # /healthcheck
        self.db_healthcheck_req = Request(self.url, "/healthcheck/db", "GET") 

        # /mazes
        self.add_maze_req = Request(self.url, "/mazes", "POST", True) 
        self.get_mazes_req = Request(self.url, "/mazes", "GET", True) 
        self.get_maze_req = Request(self.url, "/mazes/{mazeId}", "GET", True) 
        self.generate_maze_req = Request(self.url, "/mazes/generate", "GET", True) 
        self.solve_maze_req = Request(self.url, "/mazes/{mazeId}/solve", "GET", True) 
        self.get_maze_hs_avg_req = Request(self.url, "/mazes/{mazeId}/hsAvg", "GET", True) 
        self.get_maze_best_scorer_req = Request(self.url, "/mazes/{mazeId}/bestScoreUser", "GET", True) 

        # Assign a fallback token to use
        self.user_token = self.login()["response"].json()["token"]

    def send_request(self, request, **kwargs):
        try:
            start = time.time()
            response = request.send_request(**kwargs)
            finish  = time.time()

            return {"request": request, "response": response, "time": finish - start}
        except Exception as e:
            print(e)
            return {"request": request, "response": None, "time": -1}

    def signup(self, user = RequestUtils.generate_random_user()):
        return self.send_request(self.signup_req, data = user)

    def login(self, user = RequestUtils.get_default_user()):
        return self.send_request(self.login_req, data = user)

    def logout(self, token = None):
        if token is None:
            token = self.user_token
        return self.send_request(self.logout_req, token = token)

    def db_healthcheck(self):
        return self.send_request(self.db_healthcheck_req)

    def add_maze(self, maze = RequestUtils.generate_random_maze(), token = None):
        if token is None:
            token = self.user_token
        return self.send_request(self.add_maze_req, data = maze, token = token)

    def get_mazes(self, token = None):
        if token is None:
            token = self.user_token
        return self.send_request(self.get_mazes_req, token = token)

    def get_maze(self, mazeId = RequestUtils.get_default_maze_id(), token = None):
        if token is None:
            token = self.user_token
        return self.send_request(self.get_maze_req, mazeId = mazeId, token = token)

    def generate_maze(self, token = None):
        if token is None:
            token = self.user_token
        return self.send_request(self.generate_maze_req, token = token)

    def solve_maze(self, mazeId = RequestUtils.get_default_maze_id(), token = None):
        if token is None:
            token = self.user_token
        return self.send_request(self.solve_maze_req, mazeId = mazeId, token = token)

    def get_maze_hs_avg(self, mazeId = RequestUtils.get_default_maze_id(), token = None):
        if token is None:
            token = self.user_token
        return self.send_request(self.get_maze_hs_avg_req, mazeId = mazeId, token = token)

    def get_maze_best_scorer(self, mazeId = RequestUtils.get_default_maze_id(), token = None):
        if token is None:
            token = self.user_token
        return self.send_request(self.get_maze_best_scorer_req, mazeId = mazeId, token = token)

class PrometheusParser():
    def parse_response(self, request, response, time):
        endpoint, method = request.get_labels()
        status_code = response.status_code if response is not None else -1
        return self.create_line("aorf_requests", value = time, endpoint = endpoint, method = method, status_code = status_code)

    def create_line(self, metric_name, value, **kwargs):
        labels = ""
        for label in kwargs:
            labels += f",{label}=\"{kwargs[label]}\""
        labels = "{" + labels[1:] + "}"

        prom_line = f"{metric_name}{labels} {value}"
        return prom_line

        

def main():
    executor = RequestExecutor("http://localhost:8765")
    prom_parser = PrometheusParser()
    print(prom_parser.parse_response(*executor.db_healthcheck().values()))
    print(prom_parser.parse_response(*executor.login().values()))
    print(prom_parser.parse_response(*executor.get_maze().values()))
    print(prom_parser.parse_response(*executor.get_mazes().values()))
    print(prom_parser.parse_response(*executor.add_maze().values()))

    # TODO: Generate maze is a get request with a body
    # print(prom_parser.parse_response(*executor.generate_maze().values()))

    print(prom_parser.parse_response(*executor.solve_maze().values()))
    print(prom_parser.parse_response(*executor.get_maze_hs_avg().values()))
    print(prom_parser.parse_response(*executor.get_maze_best_scorer().values()))

main()
