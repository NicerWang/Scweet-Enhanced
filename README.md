

# Scweet-Enhanced

All the usages are nearly the same as [Scweet](https://github.com/Altimis/Scweet).

## What Enhanced？

1. A new Parameter for `scrape`: filter_func

   You need provide a `function`, which takes an array as input. The array contains all info of a tweet, return `True` to scrape, `False` to skip.

   > Order in array is identical to CSV file.

   ```python
   def my_filter(tweet):
       print("		In My Filter")
       if len(tweet[4]) > 40: # Tweet Length > 40 to scrape
           return True
       else:				   # Just skip
           return False
       
   data = scrape(... , filter_func=my_filter)
   ```

2. A new Parameter for `scrape`: save_name

   Set name for CSV file. None for an auto name.

3. Remove Terminal Usage

4. Modified Outputs

Note : You must have Chrome installed on your system, new source code in Scweet supports Firefox, but not Scweet-Enhanced.

## Usage :

1. Install All Requirements:

   `pip install -r requirements.txt`

2. Copy **Scweet folder** to your project.

3. Then:

   ```python
   from Scweet.scweet import scrape
   from Scweet.user import get_user_information, get_users_following, get_users_followers
   ```
