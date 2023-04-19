import os
import random
import time
from datetime import datetime, timedelta, timezone
from time import sleep
from typing import List

from .entity import DurabilityHandler
from .utils import init_driver, log_search_page, keep_scrolling, download_images


def scrape(since=None, until=None, words=None, to_account=None, from_account=None, mention_account=None,
           interval=timedelta(days=1), lang=None, headless=True, limit=float("inf"), display_type="Top",
           proxy=None, hashtag=None, show_images=False, save_images=False, image_dir=None, replies_only=False,
           proximity=False, geocode=None, min_replies=None, min_likes=None, min_retweets=None, filter_handler=None,
           listen_interval=None, endure_handler: List[DurabilityHandler] = None,
           resume_handler: DurabilityHandler = None,
           ):
    """
    scrape data from twitter using requests, starting from <since> until <until>. The program make a search between
    each <since> and <until_local> until it reaches the <until> date if it's given, else it stops at the actual date.
    """
    if endure_handler is None or len(endure_handler) == 0:
        print("No endure handler to record outputs")
        return

    # listener mode
    listener = False
    if listen_interval is not None:
        display_type = "Latest"
        listener = True
        until = None
    else:
        if since is None:
            print("MUST provide <since> when not in listener mode")
            return

    # unique tweet ids
    tweet_ids = set()
    # if <until>=None, set it to the actual date
    if until is None:
        until = datetime.strftime(datetime.fromtimestamp(time.time(), tz=timezone.utc), '%Y-%m-%d %H:%M:%S')

    # time bounds in seconds
    until_seconds = datetime.strptime(until, '%Y-%m-%d %H:%M:%S')
    if listener and resume_handler is None:
        since = datetime.strftime(until_seconds - listen_interval, '%Y-%m-%d %H:%M:%S')
    since_seconds = datetime.strptime(since, '%Y-%m-%d %H:%M:%S')
    # start scraping from <since> until <until>
    since_local = datetime.strptime(since[:10], '%Y-%m-%d')
    until_local = datetime.strptime(since[:10], '%Y-%m-%d') + interval

    until = until_seconds + timedelta(hours=23, minutes=59, seconds=59)
    until = datetime(year=until.year, month=until.month, day=until.day)

    # set refresh at 0. we refresh the page for each <interval> of time.
    refresh = 0

    # show images during scraping (for saving purpose)
    img_links = []
    if save_images:
        show_images = True
        if image_dir is None:
            image_dir = "./images"

    # initiate the driver
    driver = init_driver(headless, proxy, show_images)
    # resume scraping from previous work
    if resume_handler is not None:
        last_date = resume_handler.get_last_date()
        since_seconds = datetime.strptime(last_date, '%Y-%m-%d %H:%M:%S')
        since_local = datetime.strptime(last_date[:10], '%Y-%m-%d')

    # log search page for a specific <interval> of time and keep scrolling until scrolling stops or reach the <until>
    while until_local <= until:
        # convert <since> and <until_local> to str (Twitter only support interval by days)
        since_day = datetime.strftime(since_local, '%Y-%m-%d')
        until_local_day = datetime.strftime(until_local, '%Y-%m-%d')

        # log search page between <since> and <until_local>
        log_search_page(driver=driver, words=words, since=since_day, until_local=until_local_day, to_account=to_account,
                        from_account=from_account, mention_account=mention_account, hashtag=hashtag, lang=lang,
                        display_type=display_type, replies_only=replies_only, proximity=proximity,
                        geocode=geocode, min_replies=min_replies, min_likes=min_likes,
                        min_retweets=min_retweets)

        # number of logged pages (refresh each <interval>)
        refresh += 1

        # last position of the page : the purpose for this is to know if we reached the end of the page or not so
        # that we refresh for another <since> and <until_local>
        last_position = driver.execute_script("return window.pageYOffset;")

        # sleep
        sleep(random.uniform(0.5, 1.5))

        # start scrolling and get tweets
        links = keep_scrolling(driver, endure_handler, tweet_ids, limit, last_position, since_seconds,
                               until_seconds, filter_handler, listener)
        img_links.append(links)

        # keep updating <start date> and <end date> for every search
        since_local = since_local + interval
        until_local = until_local + interval

    # save images
    if save_images:
        print("Saving images to %s" % image_dir)
        if not os.path.exists(image_dir):
            os.makedirs(image_dir)

        download_images(img_links, image_dir, proxy=proxy)

    # close the web driver
    driver.close()
