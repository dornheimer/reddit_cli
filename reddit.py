import argparse
import pprint
import threading
import webbrowser
import sys

import colorama
from colorama import Fore, Style
import praw


colorama.init(autoreset=True)


def get_credentials():
    """Get client ID and secret for reddit API authentication."""
    with open(".secret") as f:
        return f.read().splitlines()


def parse_command_line():
    sort_options = ["hot", "new", "top", "rising", "gilded", "controversial"]

    parser = argparse.ArgumentParser(
                prog="reddit_cli",
                description="CLI for displaying threads in a subreddit"
                )
    parser.add_argument("subreddit",
                        nargs="+",
                        help="space separated list of subreddits")
    parser.add_argument("--limit",
                        metavar="integer",
                        nargs="?",
                        type=int,
                        default=10,
                        const=10,
                        help="maximum number of posts per subreddit")
    parser.add_argument("--sort",
                        choices=sort_options,
                        metavar="",
                        default="hot",
                        help="define how results are sorted."
                             " available options: " + ",".join(sort_options))

    return parser.parse_args()


def open_url(url):
    b = lambda: webbrowser.open(url, new=2)
    browser = threading.Thread(target=b)
    browser.start()


def display_subreddit(subreddit, limit=10, sort="hot"):
    sorts = {"hot": subreddit.hot,
             "new": subreddit.new,
             "top": subreddit.top,
             "rising": subreddit.rising,
             "gilded": subreddit.gilded,
             "controversial": subreddit.controversial}

    submission_urls = []
    print(Fore.BLUE + f"### {limit} '{sort}' submissons in r/{subreddit}")
    for index, submission in enumerate(sorts.get(sort)(limit=limit)):
        submission_urls.append(submission.url)
        print(Fore.YELLOW + f"[{index}]",
              Fore.CYAN + submission.title,
              Fore.GREEN + str(submission.score),
              Style.DIM + submission.author.name)

        print(Style.DIM + f"[{submission.url}]")
        print(submission.selftext.replace("\n", " ")[:300] + "...")
        print()

    user_choice = input("\nSelect a URL to open in the browser (#/n/e): ")
    if user_choice in ("e", "exit"):
        sys.exit()
    elif user_choice in ("n", "next"):
        return
    else:
        url = submission_urls[int(user_choice)]
        open_url(url)
    #pprint.pprint(vars(submission))


def main(args):
    client_id, client_secret = get_credentials()
    user_agent = "linux:reddit.cli:v0.1 (by /u/beaveroftime)"

    reddit = praw.Reddit(client_id=client_id,
                         client_secret=client_secret,
                         user_agent=user_agent)

    subreddits = [reddit.subreddit(name) for name in args.subreddit]
    for sub in subreddits:
        display_subreddit(sub, limit=args.limit, sort=args.sort)


if __name__ == "__main__":
    args = parse_command_line()
    sys.exit(main(args))
