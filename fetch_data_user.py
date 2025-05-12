import praw
import time
import re
import csv
import os
from utils.reddit_utils import get_reddit_instance
from datetime import datetime
import fetch_data_subreddit


def fetch_user_data(usernames, post_limit=None, delay=1.0):
    """
    Fetch submissions and comments for given usernames.
    Identify potential schizophrenia self-declarations via regex.
    Save results to 'data/raw/user_recheck.csv'.

    Parameters:
        usernames (list): List of Reddit usernames.
        post_limit (int): Number of items to fetch per user per type.
        delay (float): Delay in seconds between each user fetch.
    """
    reddit = get_reddit_instance()
    collected = []

    for username in usernames:
        try:
            print(f"🔍 Fetching history for u/{username}")
            user = reddit.redditor(username)

            # === Fetch submissions ===
            for submission in user.submissions.new(limit=post_limit):
                user_flair = submission.author_flair_text if submission.author_flair_text else ""
                author_name = submission.author.name if submission.author else "deleted"
                flair_declared = bool(re.search(r'schizo|psychosis', user_flair, flags=re.IGNORECASE))
                submission_declared = fetch_data_subreddit.match_self_declaration(submission.selftext + " " + submission.title)
                any_declared = flair_declared or submission_declared
                post_text = f"{submission.title}\n{submission.selftext or ''}"
                collected.append({
                    'type': 'submission',
                    'id': submission.id,
                    "parent_id": None,
                    'username': author_name,
                    'user_flair': submission.author_flair_text,
                    'created_utc': datetime.utcfromtimestamp(submission.created_utc).isoformat(),
                    'title': submission.title,
                    'text': submission.selftext,
                    'score': submission.score,
                    "upvote_ratio": submission.upvote_ratio,
                    "num_comments": submission.num_comments,
                    'subreddit': submission.subreddit.display_name,
                    "flair_declared": flair_declared,
                    "text_declared": submission_declared,
                    "any_declared": any_declared
                })

            # === Fetch comments ===
            for comment in user.comments.new(limit=post_limit):
                comment_flair = comment.author_flair_text or ""
                flair_declared_c = bool(re.search(r'schizo|psychosis', comment_flair, flags=re.IGNORECASE))
                comment_declared = fetch_data_subreddit.match_self_declaration(comment.body)
                any_declared_c = flair_declared_c or comment_declared
                if any_declared_c:
                    collected.append({
                        'type': 'comment',
                        'id': comment.id,
                        'parent_id': comment.parent_id,
                        'username': comment.author.name,
                        'user_flair': comment_flair,
                        'created_utc': datetime.utcfromtimestamp(comment.created_utc).isoformat(),
                        'title': '',
                        'text': comment.body,
                        'score': comment.score,
                        'upvote_ratio': None,
                        'num_comments': None,
                        'subreddit': comment.subreddit.display_name,
                        'flair_declared': flair_declared_c,
                        'text_declared': comment_declared,
                        'any_declared': any_declared_c
                    })

            time.sleep(delay)

        except Exception as e:
            print(f"⚠️ Could not fetch user u/{username}: {str(e)}")
            continue

    if collected:
        output_path = r"C:\Users\jvomi\PycharmProjects\MultiAgentSystem\data\raw\user_recheck.csv"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=collected[0].keys())
            writer.writeheader()
            writer.writerows(collected)
        print(f"✅ Saved {len(collected)} user posts/comments to {output_path}")
    else:
        print("⚠️ No data collected.")

