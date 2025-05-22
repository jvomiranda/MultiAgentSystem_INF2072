import fetch_data_subreddit
from agents.agent1_identifier import run_agent_verify_disorder


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
    print("Running self-declaration of schizophrenia verification agent (Agent 1)...")
    run_agent_verify_disorder(disorder='sz')  # This will process the Reddit data and verify self-declarations of SZ with Agent 1

main()