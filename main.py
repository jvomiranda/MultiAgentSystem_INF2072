import fetch_data_subreddit
from agents.agent1_identifier import run_agent_verify_disorder
from agents.agent1_conflicting_identifier import run_agent_verify_other_disorders
from fetch_data_user import fetch_all_data_user
from utils.path_utils import VERIFIED_USERS_FILE_S2, USER_ALL_POSTS_COMMENTS, POSTS_TOPIC_VALID
from utils.llm_utils import verify_topics

# main is used to create a chain that calls all the necessary processes for the system

def main():
    print("Starting the pipeline...")

    # Step 1: Fetch schizophrenia-related data from Reddit
    fetch_data_subreddit.fetch_subreddit_data(
        subreddit_name='schizophrenia',
        submission_goal=10,
        comment_goal=10
    )
    # Step 2: Run the self-declaration verification agent
    run_agent_verify_disorder(disorder='sz')  # This will process the Reddit data and verify self-declarations of SZ with Agent 1
    run_agent_verify_other_disorders('sz') # For each confirmed SZ user in the previous step, this will investigate if they have conflicting mental disorders

    fetch_all_data_user(VERIFIED_USERS_FILE_S2, post_limit=None, delay=1.0) #This uses praw to collect all of validated users' posts

    verify_topics(USER_ALL_POSTS_COMMENTS, POSTS_TOPIC_VALID)

main()