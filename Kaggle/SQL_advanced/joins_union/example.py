from google.cloud import bigquery
import db_dtypes

client = bigquery.Client()

dataset_ref = client.dataset(dataset_id="hacker_news", project="bigquery-public-data")
dataset = client.get_dataset(dataset_ref)

# comments table stores th eauthor of each comment for each story
comments_table_ref = dataset_ref.table("comments")
comments_table = client.get_table(comments_table_ref)

# story table
story_table_ref = dataset_ref.table("stories")
story_table = client.get_table(story_table_ref)

# working with the hacker news dataset. reviewing first several rows of the comments table
comments_preview = client.list_rows(comments_table, max_results=5).to_dataframe()
stories_preview = client.list_rows(story_table, max_results=5).to_dataframe()
print(comments_preview)
print(stories_preview)

# query that pulls info from stories and comments to create a table showing all stories
# that posted on jan 1 2012. Also include the number of comments for each

query = """
        WITH commCount AS
        (
            SELECT s.id, COUNT(*) AS num_comments
            FROM 
            `bigquery-public-data.hacker_news.comments` AS c
            GROUP BY s.id
        )
        SELECT s.title, c.num_comments
        FROM
            `bigquery-public-data.hacker_news.stories` AS s
            LEFT JOIN
            commCount AS c
            ON s.id = c.id
        WHERE EXTRACT(DATE FROM s.time_ts) = '2012-1-1'
        ORDER BY c.num_comments DESC;
        """
safe_config = bigquery.QueryJobConfig(maximum_bytes_billed=10**10)
query_job = client.query(query, job_config=safe_config)
result = query_job.to_dataframe()
print(result)
# CTE that stores number of comments per story
# combine data, from stories, showing how much comments each stories have
# this will include all stories from jan 1 2012, regardless if they have a comment or not
# can use result.tail() to see the NaN at the end

# Another query that selects all users who posted stories or comments on jan 1 2014
# distinct users
query2 = """
        SELECT c.by
        FROM `bigquery-public-data.hacker_news.comments as c
        WHERE EXTRACT(DATE FROM c.time_ts) = '2014-01-01'

        UNION DISTINCT

        SELECT s.by
        FROM `bigquery-public-data.hacker_news.stories as s
        WHERE EXTRACT(DATE FORM s.time_ts) = '2014-01-01'
        """

query_job2 = client.query(query2, job_config=safe_config)
result2 = query_job.to_dataframe()
print(result2)
# number of total users/authors
print(len(result2))

# fetch all users who wrote a comment on jan 1 2014 and authors
# union them by distinct so we don't have duplicate of authors who also commented
