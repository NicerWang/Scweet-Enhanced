

# Scweet-Enhanced

A Tool Enhanced from [Scweet](https://github.com/Altimis/Scweet).

## What Enhanced？

1. **Support Filter**

   Inherit Filter (in entity.py), and implement `run` method.

   Then you can do anything to tweet in `run`, or return `None` to discard it.

2. **Detach Durability**

   In Scweet, you will get a Dataframe and csv files after a run.

   In Scweet-Enhanced, you need to add `DurabilityHandler` for that. 

   You can create your handlers, but there are two provided:

   * CSVDurabilityHandler

     To write or append tweets to csv file. (**MUST** provide filename)

   * MySQLDurabilityHandler

     To add tweets to MySQL database.

   > If you want `resume`, pass `resume_handler` which accounts for getting newest tweet's time.

3. **Second Precision**

   since&until **MUST** be `"%Y-%m-%d %H:%M:%S"`, such as "2023-04-18 23:00:00".

4. Optimize parameters of `scrape`

   Some name of parametersare changed.

   You can create Query and Setting (in entity.py) to simplify parameters (See Example in [Usage](#Usage)).

5. Other small changes.

**Note : You must have Chrome installed, new source code in Scweet supports Firefox, but not Scweet-Enhanced.**

## Usage

1. Copy **Scweet folder** to your project.

2. Install All Requirements:

   `pip install -r requirements.txt`

   * To use CSVDurabilityHandler: `pip install pandas`
   * To use MySQLDurabilityHandler: `pip install pymysql`

3. Then: (An Example)

   ```python3
   from Scweet.scweet import scrape
   from Scweet.entity import Filter, CSVDurabilityHandler, MySQLDurabilityHandler, Query, Setting, Tweet
   
   query = Query(hashtag="bitcoin", since="2023-04-01", until="2023-04-02", interval=1, display_type="Top", replies_only=False, proximity=True)
   setting = Setting(headless=True, show_images=False, save_images=False, proxy="http://127.0.0.1:7890")
   
   
   class MyFilter(Filter):
       def run(self, tweet: Tweet) -> Tweet:
           print("Your can modify tweet here")
           return tweet
   
   
   csv_handler = CSVDurabilityHandler(file_name="file.csv")
   mysql_handler = MySQLDurabilityHandler("url", "username", "passwd", "db", "table")
   
   data = scrape(**vars(query), **vars(setting), filter_handler=MyFilter(), endure_handler=[csv_handler, mysql_handler])
   ```
