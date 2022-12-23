import conf.config

import praw

from os import environ

client_id = environ['CLIENT_ID']
client_secret = environ['CLIENT_SECRET']

reddit = praw.Reddit(
    client_id=client_id,
    client_secret=client_secret,
    user_agent='Scrape posts for data collection'
)


def scrape_top_posts(is_daily_check, filter_dict, subreddit) -> list:
    parsed_submissions = []

    if not is_daily_check:
        if subreddit not in conf.config.scraped_subreddits.keys():  # Subreddit not yet parsed
            temp_submission_stream = []

            for submission in reddit.subreddit(subreddit).top('week'):
                temp_submission_stream.append(submission)  # Save submissions to prevent repeating search

                if contains_flairs(filter_dict, submission) and not is_stickied(submission):
                    parsed_submissions.append([submission.title, submission.url])

            conf.config.scraped_subreddits[subreddit] = temp_submission_stream

        else:
            for submission in conf.config.scraped_subreddits[subreddit]:
                if contains_flairs(filter_dict, submission) and not is_stickied(submission):
                    parsed_submissions.append([submission.title, submission.url])

    else:
        if subreddit not in conf.config.scraped_subreddits.keys():  # Subreddit not yet parsed
            temp_submission_stream = []

            for submission in reddit.subreddit(subreddit).top('day'):
                temp_submission_stream.append(submission)  # Save submissions to prevent repeating search

                if is_urgent(submission) and contains_flairs(filter_dict, submission) and not is_stickied(submission):
                    parsed_submissions.append(['HOT TODAY : ' + submission.title, submission.url])

        else:
            for submission in conf.config.scraped_subreddits[subreddit]:
                if is_urgent(submission) and contains_flairs(filter_dict, submission) and not is_stickied(submission):
                    parsed_submissions.append(['HOT TODAY : ' + submission.title, submission.url])

    return parsed_submissions


def contains_flairs(filter_dict, submission) -> bool:
    # Checks if the post flair passes validation based on dictionary flair values
    if all(len(flair_prefs) > 0 for flair_prefs in filter_dict.values()):
        if submission.link_flair_text is not None:
            required_flairs = any(flair in submission.link_flair_text.lower() for flair in filter_dict['required_flairs'])
            restricted_flairs = not any(flair in submission.link_flair_text.lower() for flair in filter_dict['restricted_flairs'])

            return required_flairs and restricted_flairs  # Everything passed, post is valid

        else:  # No flairs in post, can default to invalid
            return False
    else:  # No flair prefs, every post will be valid
        return True


def is_stickied(submission) -> bool:
    # Checks if a post is stickied (by the mods of the subreddit), can skip if true
    return submission.stickied


def is_urgent(submission) -> bool:
    # Checks if a post is considered as "urgent" - this is defined as over 200 upvotes on the post in a given day
    return submission.score > 200
