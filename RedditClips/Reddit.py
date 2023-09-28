import praw
import configparser
import re


def set_up_config_settings():
    config = configparser.ConfigParser()
    config_file = "config.txt"
    config.read(config_file)
    if config.has_section("API"):
        client_id = config.get("API", "client_id")
        client_secret = config.get("API", "client_secret")
        username = config.get("API", "username")
        password = config.get("API", "password")

        reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=username,
        )
        return reddit

def fetch_reddit_post_data(post_url, reddit):
    try:
        submission = reddit.submission(url=post_url)

        post_data = {
            "Title": submission.title,
            "Author": submission.author.name,
            "Text": submission.selftext,
            "Score": submission.score,
            "Flair": submission.link_flair_text,
            "Num_Comments": submission.num_comments,
        }
        post_data["Text"] = post_data["Text"].replace("&#x200B;", "")

        return post_data
    except Exception as e:
        print("An error occurred:", str(e))
        return None


def find_top_posts(reddit, subreddit_name, number):
    subreddit = reddit.subreddit(subreddit_name)
    top_posts = subreddit.top(limit=number)
    post_urls = []
    for post in top_posts:
        post_urls.append(post.url)
    return post_urls
