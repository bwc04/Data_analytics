from google.cloud import bigquery
import db_dtypes

client = bigquery.Client()

# stackoverflow dataset from bigquery
dataset_ref = client.dataset(dataset_id="stackoverflow", project="bigquery-public-data")
dataset = client.get_dataset(dataset_ref)

# post_questions and post_answers tables
posts_questions_ref = dataset_ref.table("posts_questions")
posts_questions = client.get_table(posts_questions_ref)

posts_answers_ref = dataset_ref.table("posts_answers")
posts_answer = client.get_table(posts_answers_ref)

# preview
# print(client.list_rows(posts_questions, max_results=5).to_dataframe())
# print(client.list_rows(posts_answer, max_results=5).to_dataframe())

safe_config = bigquery.QueryJobConfig(maximum_bytes_billed=10**10)

'''
exercise 1: find how long it takes (secs) to for each questions to a recieve answer in Jan 2018
'''
q_ans_time_query = """
                    SELECT
                        q.id AS q_id,
                        MIN(TIMESTAMP_DIFF(a.creation_date, q.creation_date, SECOND)) AS time_to_answer
                    FROM
                        `bigquery-public-data.stackoverflow.posts_questions` AS q
                        LEFT JOIN
                        `bigquery-public-data.stackoverflow.posts_answers` AS a
                        ON q.id = a.parent_id
                    WHERE q.creation_date >= '2018-01-01' AND q.creation_date < '2018-02-01'
                    GROUP BY q_id
                    ORDER BY time_to_answer ASC;
                    """

# q_ans_time_query_job = client.query(q_ans_time_query, job_config=safe_config)
# q_ans_time = q_ans_time_query_job.to_dataframe()
# print(q_ans_time)
# # percentage of question answered
# print("Percentage of answered questions: %s%%" % \
#       (sum(q_ans_time["time_to_answer"].notnull()) / len(q_ans_time) * 100))

'''
exercise 2: is it more common for users to first ask questions or ask question when they first sign up. 
How long does the first interaction take. return user id, first question and answer creation date
Limited to questions and answers posted in jan 2019
'''
q_and_a_query = """
                SELECT q.owner_user_id AS owner_user_id,
                    MIN(q.creation_date) AS q_creation_date,
                    MIN(a.creation_date) AS a_creation_date
                FROM `bigquery-public-data.stackoverflow.posts_questions` AS q
                    FULL JOIN `bigquery-public-data.stackoverflow.posts_answers` AS a
                ON q.owner_user_id = a.owner_user_id 
                WHERE q.creation_date >= '2019-01-01' AND q.creation_date < '2019-02-01' 
                    AND a.creation_date >= '2019-01-01' AND a.creation_date < '2019-02-01'
                GROUP BY owner_user_id;
                """

# min(timestamp) allows us to find the first question and answer for each user
# full join to include users who havent posted a question before or havent posted a answer, or both

'''
exercise 3: understanding users who joined jan 2019, track their activity
When they posted their first question, answer, if they posted at all?
ids. first question and answer creation date
Need to access the user table, which gives access to each users join date
'''

numUsers =  """
            SELECT * FROM `bigquery-public-data.stackoverflow.users` as u
            WHERE u.creation_date >= '2019-01-01' AND u.creation_date < '2019-02-01';
            """
# preview numUsers and how many users in jan 2019
# numUsers_job = client.query(numUsers, job_config=safe_config)
# numUsers = numUsers_job.to_dataframe()
# print(numUsers)

three_tables_query = """
                    SELECT u.id AS id,
                        MIN(q.creation_date) AS q_creation_date,
                        MIN(a.creation_date) AS a_creation_date
                    FROM 
                        `bigquery-public-data.stackoverflow.users` AS u
                        LEFT JOIN `bigquery-public-data.stackoverflow.posts_questions` AS q
                        ON u.id = q.owner_user_id
                        LEFT JOIN `bigquery-public-data.stackoverflow.posts_answers` AS a
                        ON u.id = a.owner_user_id
                    WHERE u.creation_date >= '2019-01-01' AND u.creation_date < '2019-02-01'
                    GROUP BY id;
                    """

# First left join all users with questions, to get all users who have posted a question or not
# left join that to answers to get all users who have answered a question or not
# at this point it will include all users who joined in jan 2019, despite them having posted or answered a question

'''
exercise 4: how many distinct users posted jan 1 2019
returns single column, the id of all users who posted at least one question or answer on January 1, 2019. Each user ID should appear at most once.
Must use union
'''

all_users_query = """
                SELECT q.owner_user_id AS owner_user_id
                    FROM `bigquery-public-data.stackoverflow.posts_questions` AS q
                    WHERE EXTRACT(DATE FROM q.creation_date) = '2019-01-01'
                UNION DISTINCT
                SELECT a.owner_user_id AS owner_user_id
                    FROM `bigquery-public-data.stackoverflow.posts_answers` AS a
                    WHERE EXTRACT(DATE FROM a.creation_date) = '2019-01-01';
                  """

# first get all questions posted jan 1 2019
# second get all answers posted jan 1 2019
# distinct union, so we dont get repeats
