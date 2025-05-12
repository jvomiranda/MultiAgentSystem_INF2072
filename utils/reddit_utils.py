import praw

def get_reddit_instance():
    # Replace these values with your own Reddit API credentials
    reddit = praw.Reddit(
        client_id="YOUR_CLIENT_ID",
        client_secret="YOUR_SECRET",
        user_agent="YOUR_REASONING"
    )
    return reddit