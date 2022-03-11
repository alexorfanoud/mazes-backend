import random
from multiprocessing import Pool
import multiprocessing as mp

def generate_random_date():
    year=random.randint(1,999)
    month=random.randint(1,12)
    day=random.randint(1,28)
    hour=random.randint(1,23)
    minute=random.randint(1,59)
    second=random.randint(1,59)
    return f"{year}-{month}-{day} {hour}:{minute}:{second}"

def generate_row(i):
    print(i)
    user_id=1
    maze_id=1
    score = random.randint(1,65000)
    date = generate_random_date()
    return f"{user_id}\t{maze_id}\t{score}\t{date}\n"

def main():
    # Step 1: Init multiprocessing.Pool()
    pool = mp.Pool(mp.cpu_count())

    # Step 2: `pool.apply` the `howmany_within_range()`
    results = [pool.apply(generate_row, args=(row,)) for row in range(1000000)]

    # Step 3: Don't forget to close
    pool.close()    

    with open("init_highscores_python.txt","w") as f:
        for res in results:
            f.write(res)
        f.close()

main()
