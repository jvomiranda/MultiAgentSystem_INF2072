import praw

def get_reddit_instance():
    # Replace these values with your own Reddit API credentials
    reddit = praw.Reddit(
        client_id="",
        client_secret="",
        user_agent=""
    )
    return reddit