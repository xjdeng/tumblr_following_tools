# Tumblr Following Tools #

## Motivation ##

Earning new followers for your Tumblr account is hard work, so I've created some tools to help eliminate some of the more tedious steps of the process.  One of the fastest ways to build up an initial following is to create a good looking blog and then follow other people who are likely interested in the topics you have on your blog.  Usually, about 10-20% of them will follow you back.  You can follow up to 200 people a day on Tumblr and 5000 people total.  With the recent changes in the Tumblr interface, it's a lot more difficult to quickly follow a lot of people at once but I've created this tool to make the process as quick as possible.

## Getting Started ##


### Setting up Python ###

This tool requires Python 2.7 and the following libraries:

- Pytumblr
- Pandas

If you're new to Python, I recommend you install [Anaconda](https://www.continuum.io/downloads) for Python 2.7 which includes Pandas. **DO NOT GET THE VERSION FOR PYTHON 3.X!!!**

Then install Pytumblr by running the following at the command line:

_pip install pytumblr_

(In Windows, simply open Windows Explorer, shift-right-click a directory listing with nothing selected, and select **Open command window here** and run the above command.)

### Get your OAuth Keys ###

Log in to your [Tumblr](www.tumblr.com) account the go to the [Tumblr API Console](https://api.tumblr.com/console/calls/user/info), clicking on the link "Or Register a New Application".

Fill out the **Application Name** with whatever name you want (I just call it "Testing" or something like that.)

Fill out your Tumblr blog's URL in the **Application Website**.

Write _something_ in the **Application Description**; I just put something like "Just testing".  It doesn't matter what you have as long as it's filled.

Fill the **Default Callack URL** with _http://www.tumblr.com/dashboard_

Once everything's filled out, proceed to register your application.

You'll then be presented with a screen with a list of your applications. Click on **Explore API** for your newly registered application.

Now open the file **example-credentials.csv** in a spreadsheet (i.e. Excel) and save it as something else.  (I'll use the name **credentials.csv** in this guide but you can follow along with whatever name you choose.)

Click on **PYTHON** and you'll be presented with some code like:

```
# Authenticate via OAuth
client = pytumblr.TumblrRestClient(
```

And this is followed by 4 lines of Gibberish.

Now, be very careful as you copy these lines into your **credentials.csv** !!

Copy the 1st line of gibberish **WITHOUT** the apostrophes (') or commas (,), just the letters and numbers and paste it into Cell A2 in the spreadsheet.  Make sure there are no spaces when it's pasted!!!

Copy the 2nd line (without apostrophes, commas, or spaces!!  Just letters and numbers!) and paste it into Cell B2 in the spreadsheet

Copy the 3nd line (without apostrophes, commas, or spaces!!  Just letters and numbers!) and paste it into Cell C2 in the spreadsheet

Copy the 4th line (without apostrophes, commas, or spaces!!  Just letters and numbers!) and paste it into Cell D2 in the spreadsheet


### Testing Your Setup ###

Open a command line window in the directory where you installed this (in Windows, go to that directory in Explorer and shift-right-click and select open command window here.)

Run Python by simply typing _python_ and pressing enter.

Next, run the following commands:

```
import mytools as m
client = m.getClient("credentials.csv")
client.info()
```

If you see a big wall of text after running `client.info()`, then your setup is good!  If you get an error on the first command, make sure you've set up Python correctly as I've detailed earlier.

If you didn't input your OAuth credentials correctly, you'll likely see the following when you run `client.info()`:

`{u'meta': {u'status': 401, u'msg': u'Unauthorized'}, u'response': []}`

Make sure your OAuth credentials have been inputted into your **credentials.csv** file correctly.  This means no spaces, no apostrophes, no commas, just letter and numbers!!!


### Get your list of followers ###

Now run the following command in Python:

`myfollowing = m.getF(client.following, verbose=True)`

This may take some time as it retrieves all of the blogs you're following.  You can do the next step while you wait.

### Create a target list of blogs you'd like to follow ###

Unfortunately, a lot of this hasn't been automated by this program yet so you're gonna have to manually build a spreadsheet filled with blogs you plan on following.  If this is your first time running this, you won't have this spreadsheet so I'll go over how to build one quickly.

First, go to [Google Sheets](http://sheets.google.com) and create a new sheet.

Next, you want to look around on Tumblr for posts with lots of notes (100+) that are related to what you'll be posting on your blog.  Recent posts with lots of notes are ideal.  If you can't find any, do a Google search for `Tumblr tagged <your niche>` where you replace `<your niche>` with whatever your Tumblr blog is about (i.e. cats, food, fashion, etc.)  Another option is to look for popular Tumblr blogs in your niche and open their recent posts.

Once you've got some popular Tumblr posts related to your niche, go below and you'll find all of the people who have liked or reshared that post.  Keep hitting the "Show more notes" link until it stops showing more notes (or you've got a ridiculous number of notes".  Now, select all of those tidbits like _user1 liked this_ or _user2 reblogged this from user3_ and paste them into **Column A** of your **Spreadsheet.**  Don't worry if it's messy or ugly at this point.

Keep posting the notes below these Tumblr posts until you've gotten several thousand of them!  Yes, I'm serious, you'll definitely need that many!


#### Cleaning up the Spreadsheet ####

Select Column A

Then go to Data -> Split text to columns.

Select _Space_ for the **Separator** dialog in the lower left.

Your spreadsheet may freeze up for a minute or two.  This is normal.

Next, select all columns from C all the way to the end at the far right side and hit **Delete**.  This may also take a while which is normal.

Now, select **Columns A and B**, then go to Data -> Sort range.

For the **Sort by** option, pick **Column B**

Now delete all rows where Column B isn't _liked_ or _reblogged_.  (If you have a popular niche on Tumblr and only want the highest quality of followers, only preserve the rows where **Column B** = _reblogged_.)

Now select **Column B** and hit Delete.

Go to **cell B1** and type the following formula and hit enter:

`=unique(A:A)`

Select **Column B**, copy it, then select **Column A**, and right click -> Paste special -> Paste values only.

Now go to File -> Download as -> Comma-separated values (.csv, curret sheet)

And save that file into the same directory as this program and your **credentials.csv** file.  Call it **target.csv** (although you can use any name you like, I'll be referring it to target.csv from now on.)


### Create your target following list for Tumblr ###

Hopefully, the program has finished getting your list of people you're following by now.  If so, run the following:

```
target = m.load_tumblr_csv("target.csv")
target2 = m.follow_wizard(target,myfollowing)
m.tumblr_follow_html(target2)
```

You'll see a new file, **followme.html**, in your working directory.  Now, open that file in the web browser that's logged in to Tumblr.


### Follow people ###


By default, there will be a maximum of 200 people in that list when you open **followme.html** in your browser.  Hold down the **Ctrl** key on your keyboard as you open each of them so they open into a new browser window.  Then go into each of those browser windows and click the "follow" button.

Congrats, you've now followed up to 200 people a day in Tumblr!


## FAQ ##


Q: Why not just directly open blogs in Tumblr and click the "Follow" button in the upper right?  Why go through all of this trouble?

A: Initially, that's what I did.  But I later found out that many people I wanted to follow are already being followed by me and I ended up wasting a lot of time there.  This happened more and more once I've followed over 1000 people.

Q: Why do this manually?  Why not use `client.follow('some blog')` repeatedly?

A: Tumblr limits the number of people you can follow every hour via the API but not via their standard web interface so it's gonna take forever this way.  Plus, you also run the risk of being banned for botting.

Q: What's **posthelper.py** for?

A: It's still a work in progress and I have yet to write some documentation for it but I'm currently using it to perform statistical analysis on the performance of my posts to find out what's the best time to post to get the best follower engagement.  You can also output some raw data to SQLite but I may expand it further to output to Excel or CSV in the future.
