import argparse
import os
import pandas as pd

def init_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--csv_path', type=str, required=True,
            help="CSV file to parse")
    parser.add_argument('--package_intervals_csv', type=str, required=False,
            help="CSV File containing the package start-end intervals in format: <package>,<start time>,<end time>",\
                    default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "package_intervals.csv"))
    parser.add_argument('--verbose', action="store_true",
            help="Extra verbosity")

    global ARGS
    ARGS = parser.parse_args()
    print(ARGS)

def main():
    global ARGS

    init_args()
    package_intervals = pd.read_csv(ARGS.package_intervals_csv)
    data = pd.read_csv(ARGS.csv_path)

    for package,start_time,end_time in package_intervals.values:
        print(f"Processing {package}\n==========================")
        print(data.loc[(data['Time'] >= start_time) & (data['Time'] < end_time)].mean(numeric_only=True))
        print("==========================\n\n")

main()

