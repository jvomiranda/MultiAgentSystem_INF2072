import praw
import time
import re
import csv
import os
from utils.reddit_utils import get_reddit_instance
from datetime import datetime
import fetch_data_subreddit
import utils.regex_utils
from utils.regex_utils import extract_unique_group_matches, find_all_but_one_patterns, get_flair_pattern_for_disorder, get_flair_pattern_excluding_disorder, find_matching_patterns
from utils.path_utils import RAW_PATH, OUTPUT_FILE, VERIFIED_USERS_FILE, USER_RECHECK_FILE, USER_RECHECK_OTHER_DISORDERS, USER_ALL_POSTS_COMMENTS
from tqdm import tqdm
import pandas as pd

def fetch_user_data_for_specific_disorder(usernames, post_limit=None, delay=1.0, disorder=''):
    """
    Fetch submissions and comments for given usernames.
    Identify potential schizophrenia self-declarations via regex.
    Save results to 'data/raw/verified_users_step1_posts.csv'.

    Parameters:
        usernames (list): List of Reddit usernames.
        post_limit (int): Number of items to fetch per user per type.
        delay (float): Delay in seconds between each user fetch.
        disorder (int): acronym for disorder of choice
    """
    reddit = get_reddit_instance()
    collected = []

    for username in usernames:
        try:
            # print(f"🔍 Fetching history for u/{username}")
            user = reddit.redditor(username)

            # === Fetch submissions ===
            for submission in tqdm(user.submissions.new(limit=post_limit), desc=f"🔍 Posts from u/{username}"):
                user_flair = submission.author_flair_text if submission.author_flair_text else ""
                author_name = submission.author.name if submission.author else "deleted"
                pattern_flair = get_flair_pattern_for_disorder(disorder)
                flair_declared = bool(pattern_flair.search(user_flair))
                submission_declared = fetch_data_subreddit.match_self_declaration(submission.selftext + " " + submission.title, disorder)
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
            for comment in tqdm(user.comments.new(limit=post_limit), desc=f"🔍 Comments from u/{username}"):
                comment_flair = comment.author_flair_text or ""
                pattern_flair = get_flair_pattern_for_disorder(disorder)
                flair_declared_c = bool(pattern_flair.search(comment_flair))
                comment_declared = fetch_data_subreddit.match_self_declaration(comment.body, disorder)
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
        output_path = USER_RECHECK_FILE
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=collected[0].keys())
            writer.writeheader()
            writer.writerows(collected)
        print(f"✅ Saved {len(collected)} user posts/comments to {output_path}")
    else:
        print("⚠️ No data collected.")



def fetch_user_data_for_other_disorders(usernames, post_limit=None, delay=1.0, disorder=''):
    """
        Fetch submissions and comments for given usernames.
        Identify self-declarations for all disorders except the specified one.
        Save results to 'data/raw/verified_users_step1_posts_other_disorders.csv'.

        Parameters:
            usernames (list): List of Reddit usernames.
            post_limit (int): Number of items to fetch per user per type.
            delay (float): Delay in seconds between each user fetch.
            disorder (str): Disorder to exclude from pattern matching (e.g., 'sz')
    """
    reddit = get_reddit_instance()
    collected = []
    pattern_flair = get_flair_pattern_excluding_disorder(disorder)
    for username in usernames:
        try:
            print(f"🔍 Fetching history for u/{username}")
            user = reddit.redditor(username)

            # === Fetch submissions ===
            for submission in user.submissions.new(limit=post_limit):
                user_flair = submission.author_flair_text if submission.author_flair_text else ""
                author_name = submission.author.name if submission.author else "deleted"
                flair_declared = bool(pattern_flair.search(user_flair))

                full_text = submission.title + " " + (submission.selftext or "")
                pattern_found_in_text = find_matching_patterns(full_text, find_all_but_one_patterns('sz'))
                submission_declared = bool(pattern_found_in_text)

                any_declared = flair_declared or submission_declared

                collected.append({
                    'type': 'submission',
                    'id': submission.id,
                    "parent_id": None,
                    'username': author_name,
                    'user_flair': user_flair,
                    'created_utc': datetime.utcfromtimestamp(submission.created_utc).isoformat(),
                    'title': submission.title,
                    'text': submission.selftext,
                    'score': submission.score,
                    "upvote_ratio": submission.upvote_ratio,
                    "num_comments": submission.num_comments,
                    'subreddit': submission.subreddit.display_name,
                    "flair_declared": flair_declared,
                    "text_declared": submission_declared,
                    "any_declared": any_declared,
                    "pattern_found": extract_unique_group_matches(pattern_flair, full_text)
                })

            # === Fetch comments ===
            for comment in user.comments.new(limit=post_limit):
                comment_flair = comment.author_flair_text or ""
                flair_declared_c = bool(pattern_flair.search(comment_flair))

                pattern_found_in_comment = find_matching_patterns(comment.body, find_all_but_one_patterns('sz'))
                comment_declared = bool(pattern_found_in_comment)

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
                        'any_declared': any_declared_c,
                        'pattern_found': extract_unique_group_matches(pattern_flair, comment.body)
                    })

            time.sleep(delay)

        except Exception as e:
            print(f"⚠️ Could not fetch user u/{username}: {str(e)}")
            continue

    if collected:
        output_path = USER_RECHECK_OTHER_DISORDERS
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=collected[0].keys())
            writer.writeheader()
            writer.writerows(collected)
        print(f"✅ Saved {len(collected)} user posts/comments to {output_path}")
    else:
        print("⚠️ No data collected.")


def fetch_all_data_user(input_csv_path, post_limit=None, delay=1.0):
    """
    Fetch all posts and comments for a list of Reddit usernames from a CSV.
    No filtering is applied; all submissions and comments are collected.

    Parameters:
        input_csv_path (str): Path to the CSV file containing Reddit usernames.
        post_limit (int): Number of submissions/comments to fetch per user.
        delay (float): Delay (in seconds) between each user's data fetch.
    """
    reddit = get_reddit_instance()
    df = pd.read_csv(input_csv_path)
    usernames = df.iloc[:, 0].dropna().unique().tolist()  # First column usernames

    collected = []

    for username in usernames:
        try:
            print(f"🔍 Fetching history for u/{username}")
            user = reddit.redditor(username)

            # === Fetch submissions ===
            for submission in user.submissions.new(limit=post_limit):
                collected.append({
                    'type': 'submission',
                    'id': submission.id,
                    'parent_id': None,
                    'username': submission.author.name if submission.author else "deleted",
                    'user_flair': submission.author_flair_text or "",
                    'created_utc': datetime.utcfromtimestamp(submission.created_utc).isoformat(),
                    'title': submission.title,
                    'text': submission.selftext,
                    'score': submission.score,
                    'upvote_ratio': submission.upvote_ratio,
                    'num_comments': submission.num_comments,
                    'subreddit': submission.subreddit.display_name
                })

            # === Fetch comments ===
            for comment in user.comments.new(limit=post_limit):
                collected.append({
                    'type': 'comment',
                    'id': comment.id,
                    'parent_id': comment.parent_id,
                    'username': comment.author.name if comment.author else "deleted",
                    'user_flair': comment.author_flair_text or "",
                    'created_utc': datetime.utcfromtimestamp(comment.created_utc).isoformat(),
                    'title': '',
                    'text': comment.body,
                    'score': comment.score,
                    'upvote_ratio': None,
                    'num_comments': None,
                    'subreddit': comment.subreddit.display_name
                })

            time.sleep(delay)

        except Exception as e:
            print(f"⚠️ Could not fetch user u/{username}: {str(e)}")
            continue

    if collected:
        os.makedirs(os.path.dirname(USER_ALL_POSTS_COMMENTS), exist_ok=True)
        with open(USER_ALL_POSTS_COMMENTS, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=collected[0].keys())
            writer.writeheader()
            writer.writerows(collected)
        print(f"✅ Saved {len(collected)} entries to {USER_ALL_POSTS_COMMENTS}")
    else:
        print("⚠️ No data collected.")
