import os
import praw
from pprint import pprint

reddit = praw.Reddit(client_id=os.environ['r_client_id'],
                     client_secret=os.environ['r_client_secret'],
                     user_agent='rChileRandom Bot 0.1')

for comment in reddit.subreddit('chile').stream.comments():
    print("---------------------------------\n")
    pprint(vars(comment))
    print("---------------------------------\n")