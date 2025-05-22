import os
USER_RECHECK_OTHER_DISORDERS = '../data/raw/user_recheck_other_disorders.csv'
USER_RECHECK_FILE = '../data/raw/user_recheck.csv' # Users that agent1 flagged "No" for self-declaration
OUTPUT_FILE = '../data/processed/verified_self_declarations.csv' # Self-declarations that agent1 flagged "Yes"
VERIFIED_USERS_FILE = '../data/processed/verified_users.csv' # Username that agent1 flagged "Yes" for self-declarations
RAW_PATH = '../data/raw/' # Path to files that did not go through agents yet