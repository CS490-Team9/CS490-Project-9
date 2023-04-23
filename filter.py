import pandas as pd
import re
from bs4 import BeautifulSoup
import requests

#

prefix = "https://github.com/"
csv_name = "all_repos.csv"


def check_dependencies(repo_name, dependencies):
    url = prefix + repo_name + dependencies_suffix
    for word in dependencies:
        page = requests.get(url + "?q=" + word)
        soup = BeautifulSoup(page.content, "html.parser")
        if soup.find_all("a", {"data-hovercard-type": "dependendency_graph_package"}):
            return True
    return False


def parseReadMe(link):
    repo_name = link.split("/")[-1]
    url = prefix + link
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    texts = [e.getText() for e in soup.find_all("article", {"class": "markdown-body entry-content container-lg"})]
    regular_exp = f"((this|{repo_name.lower()}|{''.join(e for e in repo_name.lower() if e.isalnum())}|{' '.join(e for e in repo_name.lower() if e.isalnum())}) [^\.]*(utilities|utility|profiler|extension|framework|tools|tool|implementation|library|benchmark|suite|package)|for the book|tutorial|for pytorch)"
    for text in texts:
        if re.search(regular_exp, text.lower()) is not None:
            return False
    return True


def filter(repo_name, dependencies):
    return check_dependencies(repo_name, dependencies) and parseReadMe(repo_name)


df = pd.read_csv(csv_name)

dependencies_suffix = "/network/dependencies"
libraries = {"tensorflow", "keras", "torch"}

# df = df[df["GitHub Repo"].map(lambda x: filter(x, libraries))]
count = 0
for repo_name in df["GitHub Repo"]:
    count += 1
    if count % 10 == 0:
        print(count)
    try:
        if filter(repo_name, libraries):
            with open("repos.txt", "a") as f:
                f.write(prefix + repo_name + "\n")

    except:
        with open("error_repos.txt", "a") as f:
            f.write(repo_name + "\n")

# df["GitHub Repo"].to_csv("8.csv", index=False)

# drop the rows without specified libraries:
