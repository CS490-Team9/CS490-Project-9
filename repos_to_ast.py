import os
import argparse
import shutil


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("repos_file", help="the file contained the list of github report links")
    parser.add_argument("--intermediate", default="temp")
    parser.add_argument("--outpath", default="output")
    parser.add_argument("--keep", help="keep the intermediate source code from git", type=bool, default=False)

    args = parser.parse_args()

    path = args.intermediate
    outpath = args.outpath
    repos_file = args.repos_file
    keep = args.keep

    if not os.path.exists(path):
        os.makedirs(path)

    if not os.path.exists(outpath):
        os.makedirs(outpath)

    # Download the source code for each repo and run the ast convert on each of the repo
    with open(repos_file, "r") as f:
        for line in f:
            line = line[:-1]
            repo_path = os.path.join(path, "/".join(line.split("/")[-2:]))
            output_path = os.path.join(outpath, "/".join(line.split("/")[-2:]))

            if os.path.exists(output_path):
                continue

            if not os.path.exists(repo_path):
                os.system(f'git clone {line + ".git"} {repo_path}')

            os.system(f'python main.py {repo_path} {output_path}')

            if not keep:
                # repo_path may no exist git clone was not successful
                if os.path.exists(repo_path):
                    shutil.rmtree(repo_path)


if __name__ == "__main__":
    main()
