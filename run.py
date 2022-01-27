import praw
import time
import schedule
import configparser
from requests import get
from requests.exceptions import ConnectionError


config = configparser.ConfigParser()
config.read('conf.ini')
control_users = [x.strip() for x in config['SETTINGS']['control_users'].split(',')]
write_subreddits = [x.strip() for x in config['SETTINGS']['write_subreddits'].split(',')]
sleep_schedule = config['SETTINGS'].getboolean('sleep_schedule')
sleep_timer = int(config['SETTINGS']['sleep_timer'])
test_mode = config['SETTINGS'].getboolean('test_mode')

reddit = praw.Reddit(
    username=config['REDDIT']['reddit_user'],
    password=config['REDDIT']['reddit_pass'],
    client_id=config['REDDIT']['reddit_client_id'],
    client_secret=config['REDDIT']['reddit_client_secret'],
    user_agent='Mention Crossposter (by u/impshum)'
)


def wait_until_online(timeout, slumber):
    offline = 1
    t = 0
    while offline:
        try:
            r = get('https://google.com', timeout=timeout).status_code
        except ConnectionError:
            r = None
        if r == 200:
            offline = 0
        else:
            t += 1
            if t > 3:
                quit()
            else:
                print('BOT OFFLINE')
                time.sleep(10)


def runner():
    wait_until_online(10, 3)

    for mention in reddit.inbox.mentions(limit=None):
        if mention.new and str(mention.author) in control_users:
            permalink = '/'.join(mention.context.split('/')[:5])
            id = mention.context.split('/')[4:5][0]
            post_url = f'https://reddit.com{permalink}'
            if not test_mode:
                submission = reddit.submission(id)
                for write_subreddit in write_subreddits:
                    submission.crosspost(subreddit=write_subreddit)
                    print(f'Crossposted {post_url} to {write_subreddit}')
                    time.sleep(3)
                mention.mark_read()
            else:
                print(f'TEST - Crossposted {post_url} to {write_subreddit}')



def main():
    runner()

    if sleep_schedule:
        schedule.every().hours.do(runner)

        while True:
            schedule.run_pending()
            time.sleep(1)


if __name__ == '__main__':
    main()
