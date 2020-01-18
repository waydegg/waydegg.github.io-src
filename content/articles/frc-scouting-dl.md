Title: (Data Cleaning) DL/ML in FRC Robotics Scouting/Strategy
Date: 2018-10-25 12:13
Modified: 2018-10-25 12:13
Tags: personal projects, robotics, scouting, deep learning
Slug: frc-robotics-dl
Authors: Wayde Gilliam
Summary: Data Cleaning & Feature Engineering on FRC Match/Team Data

## Data Preparation

### Objective

Before doing any model training, we've got to gather our data. We have several data sets to work with: the match and overall team stats from TBA and the Scouting data provided by our team. With the data in its raw form, we'll have to clean it up so that the machine learning models can best train on the datasets. Getting rid of redundant columns, fixing mislabeled scouting data, and properly formatting column names will be a few of many changes needed to be made. After cleaning all our data, we'll need to merge our data sets to get better prediction accuracy and to speed up training time. Finally, after some preprocessing, our new cleaned and formatted dataset will be ready for Deep Learning.

### Pulling TBA and Scouting Data

To start, let's import all of the necessary libraries we'll need:

```python
import os, json, pickle, requests, re, pdb
from datetime import datetime

from fastai.structured import *
from fastai.column_data import *

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Always display all the columns
pd.set_option('display.width', 5000)
pd.set_option('display.max_columns', 160)
pd.set_option('display.max_rows', 1000)

%matplotlib inline
```

We'll be using several libraries commonly used in the Fast.ai courses as they're essential to helping pull and clean our raw datasets. Feel free to read up more on them on your own to learn more about their uses and capabilities. Towards the bottom is just some formatting options for when we view our datasets in the notebook.

Next, we'll need our authentication keys to access the data we want. How The Blue Alliance api works is that each team is assigned a specific key to pull from their database, so when you sign up to make an account on their website you can request one. This is a pretty simple system, so we used the same idea for pulling data from RoboRecon.

```python
tba_read_api_key = 'your_tba_api_key_here'
rr_read_api_key = 'your_roborecon_api_key_here'

comp_yr = '2018'
```

Next we'll create some variables for our data file paths (imported as CSV files):

```python
tba_header = { 'X-TBA-Auth-Key': tba_read_api_key }

team_match_scores_file = f'data/{comp_yr}-team-match-scores.csv'
team_event_stats_file = f'data/{comp_yr}-team-event-stats.csv'
scouting_reports_file = f'data/{comp_yr}-scouting-reports.csv'

merged_file = f'data/{comp_yr}-merged.csv'
pp_file = f'data/{comp_yr}-preprocessed.csv'
```

To have consistend column names, we'll write a function to convert all of them to snake casing:

```python
def camel_to_snake(val):
   s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', val)
   return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
```

####Getting All Events for the Competition Year

We'll be making a request to TBA for the events of the specified year (in this case, 2018) which will return a csv file of all the event stats. Checkout the [docs](https://www.thebluealliance.com/apidocs/v3) for TBA api to learn more.

```py
# get all events
r = requests.get(f'https://www.thebluealliance.com/api/v3/events/{comp_yr}', headers=tba_header)

if (r.status_code == 200):
   events = r.json()
```

####Getting All Match Stats by Team per Event

To put it simply, we'll be downloading all of the latest match data from TBA:

```py
%%time

# for each team, get all their match scores for the year
team_matches = [img]

# keep track of playoff stats for each team as well; include in overall event/team stats below
team_playoff_stats = {}

for ev in events:
   # ignore preseason and offseason
   if (ev['event_type'] in [99, 100, -1]): continue  # offseason, preseason, unlabeled
      
   # print('Getting matches for event {0}'.format(ev['key']))
  
   event_key = ev['key']
   event_start = ev['start_date']
   event_end = ev['end_date']
   event_week = ev['week']
  
   # get event match scores
   r = requests.get(f'https://www.thebluealliance.com/api/v3/event/{event_key}/matches', headers=tba_header)
  
   matches = r.json()
  
   for match in matches:
       # get team keys for each alliance and a reference to their score breakdown
       blue_team_keys = match['alliances']['blue']['team_keys']
       red_team_keys = match['alliances']['red']['team_keys']
       all_team_keys = blue_team_keys + red_team_keys
      
       if (match['score_breakdown'] != None):
           blue_score_breakdown = match['score_breakdown']['blue']
           red_score_breakdown = match['score_breakdown']['red']
      
       for team in all_team_keys:
           if (team in blue_team_keys):
               alliance = 'blue'
               opp_alliance = 'red'
               alliance_team_keys = [ k for k in blue_team_keys if (k != team) ]
           else:
               alliance = 'red'
               opp_alliance = 'blue'
               alliance_team_keys = [ k for k in red_team_keys if (k != team) ]
              
           # add team match data
           team_match = {
               'year': comp_yr,
               'event_key': event_key,
               'event_week': event_week,
               'match_key': match['key'],
               'team_key': team,
               'match_number': match['match_number'],
               'set_number': match['set_number'],
               'comp_level': match['comp_level'],
               'time': match['time'],
               'actual_time': match['actual_time'],
               'predicted_time': match['predicted_time'],
               'post_result_time': match['post_result_time'],
               'score': match['alliances'][alliance]['score'],
               'is_winner': 1 if (match['winning_alliance'] == alliance) else 0,
               'alliance': alliance,
               'alliance_robot_pos': match['alliances'][alliance]['team_keys'].index(team) + 1,
               'alliance_team_keys': alliance_team_keys,
               'winning_margin': match['alliances'][alliance]['score'] - match['alliances'][opp_alliance]['score']
           }
      
           # include score breakdown
           if (match['score_breakdown'] != None):
               if (alliance == 'blue'):
                   team_match.update(blue_score_breakdown)
               else:
                   team_match.update(red_score_breakdown)
              
           team_matches.append(team_match)
      
           # add playoff stats data
           team_event_key = team_match['team_key'] + '_' + team_match['event_key']
      
           if (team_event_key not in team_playoff_stats):
               team_playoff_stats[team_event_key] = {
                   'team_key': team_match['team_key'],
                   'event_key': team_match['event_key'],
                   'is_playoff_team': 0,
                   'is_finals_team': 0,
                   'post_qual_wins': 0
               }
          
           # comp_level = [ qm, ef, qf, sf, f ]
           if (team_match['comp_level'] != 'qm'):
               team_playoff_stats[team_event_key]['is_playoff_team'] = 1

               if (team_match['is_winner'] == 1):
                   team_playoff_stats[team_event_key]['post_qual_wins'] += 1

               if (team_match['comp_level'] == 'f'): team_playoff_stats[team_event_key]['is_finals_team'] = 1
      
# sort team matches by startdate (earliest to most recent)
team_matches = sorted(team_matches, key=lambda x: x['time'] if x['actual_time'] == None else x['actual_time'])
```

Ok, this is a lot of code but let's step through it:

1. First we decide what events we want to pull and rename a few columns so that they'll make more sense. Then we'll make another request to TBA for their match data per event.
2. We'll look through every match in every event and start grouping them by team_key. We'll create new columns for the new team-specific dataset we're creating, and rename columns so they make more sense.
3. Then we'll add in columns for playoff match data for each team.

Next we're going to convert our formatted match data frame into a pandas dataframe, clean the data, and convert it to a csv. This part will change every year depending on the competition. See the FIRST API and TBA API docs on how they are coding different scoring elements.

```python
matches_df = pd.DataFrame(team_matches)
matches_df.head(10)
```
![img](images/scouting_app/jnb_1.png)

Here's what the match dataframe for each team looks like. There are a few columns we'll want to clean up so that our data makes more sense for our machine learning algorithms, so let's get to it.

```python
# map autonomous to 1 or 0
print(matches_df.autoRobot1.unique(), matches_df.autoRobot2.unique(), matches_df.autoRobot3.unique())
robotAutoMap = { 'AutoRun': 1, 'None': 0, 'Unknown': 0, np.nan: 0 }

matches_df.autoRobot1 = matches_df.autoRobot1.map(robotAutoMap)
matches_df.autoRobot2 = matches_df.autoRobot2.map(robotAutoMap)
matches_df.autoRobot3 = matches_df.autoRobot3.map(robotAutoMap)
```

For the columns 'autoRobot1', 'autoRobot2', and 'autoRobot3' tell us which robot on a particular alliance did something in the Autonomous period of the match or not. The values TBA gives us is 'AutoRun' or 'None'. These values can and should be 0 or 1 values, so that's what we change them to.

```python
# map endgame scores (note: levitate is randomly assigned to a team)
print(matches_df.endgameRobot1.unique(), matches_df.endgameRobot2.unique(), matches_df.endgameRobot3.unique())
endgameMap = { 'Parking': 'Parking', 'Climbing': 'Climbing', 'Levitate': 'Levitate', 'None': 'None', 'Unknown': 'None', np.nan: 'None' }

matches_df.endgameRobot1 = matches_df.endgameRobot1.map(endgameMap)
matches_df.endgameRobot2 = matches_df.endgameRobot2.map(endgameMap)
matches_df.endgameRobot3 = matches_df.endgameRobot3.map(endgameMap)
```

Here we are making the columns regarding alliance endgame scoring more clear. TBA has their data where the 'Levitate' element is assigned to a random team, even though it really applies to the whole alliance. Since this is alliance-wide data we want to assign for each team, the endgameRobot columns should be able to contain multiple endgame values.

```python
# this will cover any other convertible columns (will make them floats by default)
matches_df = matches_df.apply(pd.to_numeric, errors='ignore')

# convert NaNs to 0
matches_df.fillna(0.0, inplace=True)

# event_week starts at 0 .. so add 1
matches_df.event_week = matches_df.event_week + 1

# convert count and boolean columns to int
bool_cols = ['autoQuestRankingPoint', 'autoSwitchAtZero', 'faceTheBossRankingPoint']

matches_df[bool_cols] = matches_df[bool_cols].astype(int)
```

We're doing some more cleaning in our dataset to feed it into our ML algorithms. Having NaN values in places where they shouldn't be and wrong data types can give you errors when you start training your models.

Next, let's do some feature engineering to simplify our dataframe a little. Some of the columns in our data are redundant or aren't very clear on what they're representing, so let's fix that.

```python
# create additional columns that aggregate others
matches_df['autoRobotRunCount'] = matches_df['autoRobot1'] + matches_df['autoRobot2'] + matches_df['autoRobot3']
matches_df['endgameRobotClimbCount'] = matches_df.apply(lambda r: (r['endgameRobot1'] == 'Climbing') + (r['endgameRobot2'] == 'Climbing') + (r['endgameRobot3'] == 'Climbing'), axis=1) having Roborecon for 2 years with its benefits clearly paying off, I wanted to see if we could push our scouting abilities even further. I had been hearing about how FRC teams are starting to use machine learning in their vision software and autonomous routines, and I was interested to see if I could apply ML/DL to scouting data and get accurate predictions. I had already gone through [Andrew Ng's "Machine Learning"](https://www.coursera.org/learn/machine-learning) course and had just started going through [Fastai's Practical Deep Learning for Coders Part 1](fast.ai), so I was still very new to this field.

As it turns out, yes, you can use Deep Learning in FRC scouting. There are tons of areas it can be used in. My scouting team and I determined a list of uses for the ML analysis that could potentially change the way we perform at competitions completely:

1. Correcting human error. When you're forcing the limited number of unwilling Freshmen on your team to scout during competition, they're going to mislabel data and entirely forget to scout some matches. Early in the season when we start out with having no data from teams for that year, it's critical that we correctly record how they're performing during the 8-11 qualification matches they get before alliance selections or we might miss pick a team and jeopardize our entire season.

2. Predicting match and event outcomes before they've happened. There are thousands of FRC teams with hundreds competing simultaneously during competition season, so the only way we could scout all of them is with the help of ML algorithms. Going into the Turing Division in 2018 at the Houston World Championships we already had match predictions and team specific stats for the 67 teams attending, most of which we had never seen compete, thanks to Deep Learning.

3. Revealing missed important match and team data. From using the Roborecon web app in the past, we'd discovered certain robot attributes that we thought mattered were irrelevant, and others we thought weren't that important actually mattered a lot. Implementing deep learning into our scouting application would only further these discoveries.

I'm going to assume you have a basic understanding of Python, [Jupyter Notebooks](http://jupyter.org), and ML/DL as I go into detail on my code and how I put everything together in this section of the writeup. Feel free to contact me with any questions or help for getting world class predictions on your own scouting data because really anyone can do this. As RoboRecon is proprietary software to Team Paradox, I'll be highlighting what code we presented at the 2018 Houston World Championships that we made public.

---

This ended up being a pretty comprehensive write up, so the Data Cleaning and Machine Learning/Deep Learning sections are split into two separate pages:

## [Data Cleaning](/frc-robotics-dl.html)

## Machine Learning/Deep Learning (Coming Soon)
 having Roborecon for 2 years with its benefits clearly paying off, I wanted to see if we could push our scouting abilities even further. I had been hearing about how FRC teams are starting to use machine learning in their vision software and autonomous routines, and I was interested to see if I could apply ML/DL to scouting data and get accurate predictions. I had already gone through [Andrew Ng's "Machine Learning"](https://www.coursera.org/learn/machine-learning) course and had just started going through [Fastai's Practical Deep Learning for Coders Part 1](fast.ai), so I was still very new to this field.

As it turns out, yes, you can use Deep Learning in FRC scouting. There are tons of areas it can be used in. My scouting team and I determined a list of uses for the ML analysis that could potentially change the way we perform at competitions completely:

1. Correcting human error. When you're forcing the limited number of unwilling Freshmen on your team to scout during competition, they're going to mislabel data and entirely forget to scout some matches. Early in the season when we start out with having no data from teams for that year, it's critical that we correctly record how they're performing during the 8-11 qualification matches they get before alliance selections or we might miss pick a team and jeopardize our entire season.

2. Predicting match and event outcomes before they've happened. There are thousands of FRC teams with hundreds competing simultaneously during competition season, so the only way we could scout all of them is with the help of ML algorithms. Going into the Turing Division in 2018 at the Houston World Championships we already had match predictions and team specific stats for the 67 teams attending, most of which we had never seen compete, thanks to Deep Learning.

3. Revealing missed important match and team data. From using the Roborecon web app in the past, we'd discovered certain robot attributes that we thought mattered were irrelevant, and others we thought weren't that important actually mattered a lot. Implementing deep learning into our scouting application would only further these discoveries.

I'm going to assume you have a basic understanding of Python, [Jupyter Notebooks](http://jupyter.org), and ML/DL as I go into detail on my code and how I put everything together in this section of the writeup. Feel free to contact me with any questions or help for getting world class predictions on your own scouting data because really anyone can do this. As RoboRecon is proprietary software to Team Paradox, I'll be highlighting what code we presented at the 2018 Houston World Championships that we made public.

---

This ended up being a pretty comprehensive write up, so the Data Cleaning and Machine Learning/Deep Learning sections are split into two separate pages:

## [Data Cleaning](/frc-robotics-dl.html)

## Machine Learning/Deep Learning (Coming Soon)
matches_df['autoRobot'] = matches_df having Roborecon for 2 years with its benefits clearly paying off, I wanted to see if we could push our scouting abilities even further. I had been hearing about how FRC teams are starting to use machine learning in their vision software and autonomous routines, and I was interested to see if I could apply ML/DL to scouting data and get accurate predictions. I had already gone through [Andrew Ng's "Machine Learning"](https://www.coursera.org/learn/machine-learning) course and had just started going through [Fastai's Practical Deep Learning for Coders Part 1](fast.ai), so I was still very new to this field.

As it turns out, yes, you can use Deep Learning in FRC scouting. There are tons of areas it can be used in. My scouting team and I determined a list of uses for the ML analysis that could potentially change the way we perform at competitions completely:

1. Correcting human error. When you're forcing the limited number of unwilling Freshmen on your team to scout during competition, they're going to mislabel data and entirely forget to scout some matches. Early in the season when we start out with having no data from teams for that year, it's critical that we correctly record how they're performing during the 8-11 qualification matches they get before alliance selections or we might miss pick a team and jeopardize our entire season.

2. Predicting match and event outcomes before they've happened. There are thousands of FRC teams with hundreds competing simultaneously during competition season, so the only way we could scout all of them is with the help of ML algorithms. Going into the Turing Division in 2018 at the Houston World Championships we already had match predictions and team specific stats for the 67 teams attending, most of which we had never seen compete, thanks to Deep Learning.

3. Revealing missed important match and team data. From using the Roborecon web app in the past, we'd discovered certain robot attributes that we thought mattered were irrelevant, and others we thought weren't that important actually mattered a lot. Implementing deep learning into our scouting application would only further these discoveries.

I'm going to assume you have a basic understanding of Python, [Jupyter Notebooks](http://jupyter.org), and ML/DL as I go into detail on my code and how I put everything together in this section of the writeup. Feel free to contact me with any questions or help for getting world class predictions on your own scouting data because really anyone can do this. As RoboRecon is proprietary software to Team Paradox, I'll be highlighting what code we presented at the 2018 Houston World Championships that we made public.

---

This ended up being a pretty comprehensive write up, so the Data Cleaning and Machine Learning/Deep Learning sections are split into two separate pages:

## [Data Cleaning](/frc-robotics-dl.html)

## Machine Learning/Deep Learning (Coming Soon).apply(lambda r: r[f'autoRobot{r["alliance_robot_pos"]}'], axis=1) having Roborecon for 2 years with its benefits clearly paying off, I wanted to see if we could push our scouting abilities even further. I had been hearing about how FRC teams are starting to use machine learning in their vision software and autonomous routines, and I was interested to see if I could apply ML/DL to scouting data and get accurate predictions. I had already gone through [Andrew Ng's "Machine Learning"](https://www.coursera.org/learn/machine-learning) course and had just started going through [Fastai's Practical Deep Learning for Coders Part 1](fast.ai), so I was still very new to this field.

As it turns out, yes, you can use Deep Learning in FRC scouting. There are tons of areas it can be used in. My scouting team and I determined a list of uses for the ML analysis that could potentially change the way we perform at competitions completely:

1. Correcting human error. When you're forcing the limited number of unwilling Freshmen on your team to scout during competition, they're going to mislabel data and entirely forget to scout some matches. Early in the season when we start out with having no data from teams for that year, it's critical that we correctly record how they're performing during the 8-11 qualification matches they get before alliance selections or we might miss pick a team and jeopardize our entire season.

2. Predicting match and event outcomes before they've happened. There are thousands of FRC teams with hundreds competing simultaneously during competition season, so the only way we could scout all of them is with the help of ML algorithms. Going into the Turing Division in 2018 at the Houston World Championships we already had match predictions and team specific stats for the 67 teams attending, most of which we had never seen compete, thanks to Deep Learning.

3. Revealing missed important match and team data. From using the Roborecon web app in the past, we'd discovered certain robot attributes that we thought mattered were irrelevant, and others we thought weren't that important actually mattered a lot. Implementing deep learning into our scouting application would only further these discoveries.

I'm going to assume you have a basic understanding of Python, [Jupyter Notebooks](http://jupyter.org), and ML/DL as I go into detail on my code and how I put everything together in this section of the writeup. Feel free to contact me with any questions or help for getting world class predictions on your own scouting data because really anyone can do this. As RoboRecon is proprietary software to Team Paradox, I'll be highlighting what code we presented at the 2018 Houston World Championships that we made public.

---

This ended up being a pretty comprehensive write up, so the Data Cleaning and Machine Learning/Deep Learning sections are split into two separate pages:

## [Data Cleaning](/frc-robotics-dl.html)

## Machine Learning/Deep Learning (Coming Soon)
matches_df['endgameRobot'] = matches having Roborecon for 2 years with its benefits clearly paying off, I wanted to see if we could push our scouting abilities even further. I had been hearing about how FRC teams are starting to use machine learning in their vision software and autonomous routines, and I was interested to see if I could apply ML/DL to scouting data and get accurate predictions. I had already gone through [Andrew Ng's "Machine Learning"](https://www.coursera.org/learn/machine-learning) course and had just started going through [Fastai's Practical Deep Learning for Coders Part 1](fast.ai), so I was still very new to this field.

As it turns out, yes, you can use Deep Learning in FRC scouting. There are tons of areas it can be used in. My scouting team and I determined a list of uses for the ML analysis that could potentially change the way we perform at competitions completely:

1. Correcting human error. When you're forcing the limited number of unwilling Freshmen on your team to scout during competition, they're going to mislabel data and entirely forget to scout some matches. Early in the season when we start out with having no data from teams for that year, it's critical that we correctly record how they're performing during the 8-11 qualification matches they get before alliance selections or we might miss pick a team and jeopardize our entire season.

2. Predicting match and event outcomes before they've happened. There are thousands of FRC teams with hundreds competing simultaneously during competition season, so the only way we could scout all of them is with the help of ML algorithms. Going into the Turing Division in 2018 at the Houston World Championships we already had match predictions and team specific stats for the 67 teams attending, most of which we had never seen compete, thanks to Deep Learning.

3. Revealing missed important match and team data. From using the Roborecon web app in the past, we'd discovered certain robot attributes that we thought mattered were irrelevant, and others we thought weren't that important actually mattered a lot. Implementing deep learning into our scouting application would only further these discoveries.

I'm going to assume you have a basic understanding of Python, [Jupyter Notebooks](http://jupyter.org), and ML/DL as I go into detail on my code and how I put everything together in this section of the writeup. Feel free to contact me with any questions or help for getting world class predictions on your own scouting data because really anyone can do this. As RoboRecon is proprietary software to Team Paradox, I'll be highlighting what code we presented at the 2018 Houston World Championships that we made public.

---

This ended up being a pretty comprehensive write up, so the Data Cleaning and Machine Learning/Deep Learning sections are split into two separate pages:

# [Data Cleaning](/frc-robotics-dl.html)

# Machine Learning/Deep Learning (Coming Soon)_df.apply(lambda r: r[f'endgameRobot{r["alliance_robot_pos"]}'], axis=1) having Roborecon for 2 years with its benefits clearly paying off, I wanted to see if we could push our scouting abilities even further. I had been hearing about how FRC teams are starting to use machine learning in their vision software and autonomous routines, and I was interested to see if I could apply ML/DL to scouting data and get accurate predictions. I had already gone through [Andrew Ng's "Machine Learning"](https://www.coursera.org/learn/machine-learning) course and had just started going through [Fastai's Practical Deep Learning for Coders Part 1](fast.ai), so I was still very new to this field.

As it turns out, yes, you can use Deep Learning in FRC scouting. There are tons of areas it can be used in. My scouting team and I determined a list of uses for the ML analysis that could potentially change the way we perform at competitions completely:

1. Correcting human error. When you're forcing the limited number of unwilling Freshmen on your team to scout during competition, they're going to mislabel data and entirely forget to scout some matches. Early in the season when we start out with having no data from teams for that year, it's critical that we correctly record how they're performing during the 8-11 qualification matches they get before alliance selections or we might miss pick a team and jeopardize our entire season.

2. Predicting match and event outcomes before they've happened. There are thousands of FRC teams with hundreds competing simultaneously during competition season, so the only way we could scout all of them is with the help of ML algorithms. Going into the Turing Division in 2018 at the Houston World Championships we already had match predictions and team specific stats for the 67 teams attending, most of which we had never seen compete, thanks to Deep Learning.

3. Revealing missed important match and team data. From using the Roborecon web app in the past, we'd discovered certain robot attributes that we thought mattered were irrelevant, and others we thought weren't that important actually mattered a lot. Implementing deep learning into our scouting application would only further these discoveries.

I'm going to assume you have a basic understanding of Python, [Jupyter Notebooks](http://jupyter.org), and ML/DL as I go into detail on my code and how I put everything together in this section of the writeup. Feel free to contact me with any questions or help for getting world class predictions on your own scouting data because really anyone can do this. As RoboRecon is proprietary software to Team Paradox, I'll be highlighting what code we presented at the 2018 Houston World Championships that we made public.

---

This ended up being a pretty comprehensive write up, so the Data Cleaning and Machine Learning/Deep Learning sections are split into two separate pages:

## [Data Cleaning](/frc-robotics-dl.html)

## Machine Learning/Deep Learning (Coming Soon)
```

We're going to want a way to sort the many rows of match data. For now, it would make sense if we grouped rows by event and then sort it by time. We can always change this later. It'll also make more sense if we move the columns we're using to index our data to the beginning of our dataframe.

```python
# create addition column for a team's match number in each competition
matches_df.sort_values('actual_time', inplace=True)

matches_df['team_match_num'] = matches_df.groupby(['event_key', 'team_key']).cumcount() + 1

# convert unix timestamps to datetime
datetime_cols = ['actual_time', 'post_result_time', 'predicted_time', 'time']
matches_df[datetime_cols] = matches_df[datetime_cols].apply(pd.to_datetime, unit='s')

# sort data by even start_date (most recent on top)
matches_df.sort_values(['event_week', 'event_key', 'actual_time', 'alliance'], inplace=True)

non_sorted = ['event_key', 'match_key', 'team_key', 'event_week', 'team_match_num',
             'actual_time', 'predicted_time', 'post_result_time', 'time']

# convert columna names to snake case
matches_df.columns = [ f'tba_{camel_to_snake(c)}' if c not in non_sorted else c for c in matches_df.columns ]

# define sort order
matches_col_order = ['event_key', 'match_key', 'team_key', 'event_week', 'team_match_num', 'actual_time'] + \
                   sorted(list(matches_df.columns.drop(non_sorted))) + \
                   ['predicted_time', 'post_result_time', 'time']
      
# sort column names
matches_df = matches_df.reindex(matches_col_order, axis=1)
```

At this point I'm satisfied with our new cleaned up dataset. Let's see what it looks like now:

![img](images/scouting_app/jnb_2.png)

Now to save it as a csv to use for later.

```python
matches_df.to_csv(team_match_scores_file, index=False)
```

#### Getting Overall Stats by Team per Event

The process of pulling the data from TBA, loading in the data and cleaning, and saving it as a csv file is very similar to the team match data we just formatted. For the sake of not repeating myself, I'm going to skip over the exact code/instructions. While match team data consists of specific statistics such as 'power ups activated' or 'tech fouls accumulated', overall match stats means what it's called. Parameters such as OPR, number of match wins/losses, and CCWMS are what we're looking at. Here's what the cleaned up dataframe looks like for Overall Stats:

![img](images/scouting_app/jnb_3.png)

#### Getting Scouing Reports for the Competition Year

Just like the TBA that's hosted on our Firebase server, pullling all our scouitng data is done in the exact same way.

```python
# get target event data
%time r = requests.get(f'https://paradox-scout-dc256.firebaseio.com/team_scouting_reports/2102/{rr_read_api_key}.json')

scouting_reports = [img]

if (r.status_code == 200):
   #pdb.set_trace()
   target_scouting_data = r.json()

   for event_key, scores in target_scouting_data.items():
       # print(event_key)
       # only load ratings for current comp_yr
       if (event_key[:4] != str(comp_yr)): continue
      
       scouting_reports += [ v for k,v in scores.items() if ('team_id' in v) ]
```

#### Load into a Dataframe and Clean/Transform Data

Let's start out our data cleaning by formatting our column names and orders so everything makes sense to someone reading the dataframe from left to right, and then let's fix our date & time columns so they look cleaner.

```python
# convert unix timestamps to datetime
scouting_reports_df['scored_at'] = pd.to_datetime(scouting_reports_df['scored_at'], unit='ms')

# sort by date ascending (most recent on top)
scouting_reports_df.sort_values(['team_id', 'scored_at'], inplace=True)

# remove rows without an event_id
scouting_reports_df = scouting_reports_df[pd.notnull(scouting_reports_df['event_id'])]

# drop the 'scored_by' column (and other weird/probably test values)
scouting_reports_df.drop(['scored_by'], axis=1, inplace=True)

# convert numeric columns to numeric data types
numeric_cols = scouting_reports_df.drop(['event_id', 'match_key', 'scored_at', 'team_id'], axis=1).columns
scouting_reports_df[numeric_cols] = scouting_reports_df[numeric_cols].apply(pd.to_numeric, errors='coerce')

# convert boolean columns and those that maintain a count to int
int_cols = [img]
scouting_reports_df[int_cols] = scouting_reports_df[int_cols].astype(int)
```

I see that there are 'cubes on X' (with 'X' being a specific scoring area on the playing field) 'missed' or 'made' stats in our dataframe. A better metric to see how many cubes a team can potentially score in a particular area would be 'cubes attempted on X'. It would just be another way of looking at the data we've already gathered which we'll attach to our already existing scouting dataframe:

```python
# add attempted columns
def attmptedExchange(row):
   if (pd.notnull(row['rating_overall_exchange_efficiency'])
       or row['rating_scoring_cubes_exchanged_made'] > 0):
       return 1
   return 0
def attmptedSwitch(row):
   if (pd.notnull(row['rating_overall_switch_efficiency'])
       or row['rating_scoring_cubes_on_switch_made'] > 0
       or row['rating_scoring_cubes_on_switch_missed'] > 0):
       return 1
   return 0
def attmptedSwitchAuto(row):
   if (pd.notnull(row['rating_overall_switch_efficiency_auto'])
       or row['rating_scoring_cubes_on_switch_auto_made'] > 0
       or row['rating_scoring_cubes_on_switch_auto_missed'] > 0):
       return 1
   return 0
def attmptedScale(row):
   if (pd.notnull(row['rating_overall_scale_efficiency'])
       or row['rating_scoring_cubes_on_scale_made'] > 0
       or row['rating_scoring_cubes_on_scale_missed'] > 0):
       return 1
   return 0
def attmptedScaleAuto(row):
   if (pd.notnull(row['rating_overall_scale_efficiency_auto'])
       or row['rating_scoring_cubes_on_scale_auto_made'] > 0
       or row['rating_scoring_cubes_on_scale_auto_missed'] > 0):
       return 1
   return 0

scouting_reports_df['rating_attempted_exchange'] = scouting_reports_df.apply(
   lambda r: attmptedExchange(r), axis=1)

scouting_reports_df['rating_attempted_switch'] = scouting_reports_df.apply(
   lambda r: attmptedSwitch(r), axis=1)

scouting_reports_df['rating_attempted_switch_auto'] = scouting_reports_df.apply(
   lambda r: attmptedSwitchAuto(r), axis=1)

scouting_reports_df['rating_attempted_scale'] = scouting_reports_df.apply(
   lambda r: attmptedScale(r), axis=1)

scouting_reports_df['rating_attempted_scale_auto'] = scouting_reports_df.apply(
   lambda r: attmptedScaleAuto(r), axis=1)
```

One thing that ML models do not like are NaN values. Maybe a scouting report for one team during a match wasn't submitted or a scouter forgot to watch a team's autonomous run during the match they were supposed to be, we need to replace these NaN values with something that our ML models won't complain about. One easy option is adding in a 'signal value' that would never appear in the actual data indicating that whatever cell it's placed in was previously occupied by a NaN value:

```python
scouting_reports_df.loc[scouting_reports_df.rating_attempted_switch == 0,
                       ['rating_overall_switch_efficiency',
                        'rating_scoring_cubes_on_switch_made',
                        'rating_scoring_cubes_on_switch_missed']] = -99, np.nan, np.nan

scouting_reports_df.loc[scouting_reports_df.rating_attempted_switch_auto == 0,
                       ['rating_overall_switch_efficiency_auto',
                        'rating_scoring_cubes_on_switch_auto_made',
                        'rating_scoring_cubes_on_switch_auto_missed']] = -99, np.nan, np.nan

scouting_reports_df.loc[scouting_reports_df.rating_attempted_scale == 0,
                       ['rating_overall_scale_efficiency',
                        'rating_scoring_cubes_on_scale_made',
                        'rating_scoring_cubes_on_scale_missed']] = -99, np.nan, np.nan

scouting_reports_df.loc[scouting_reports_df.rating_attempted_scale_auto == 0,
                       ['rating_overall_scale_efficiency_auto',
                        'rating_scoring_cubes_on_scale_auto_made',
                        'rating_scoring_cubes_on_scale_auto_missed']] = -99, np.nan, np.nan

scouting_reports_df.loc[scouting_reports_df.rating_attempted_exchange == 0,
                       ['rating_overall_exchange_efficiency',
                       'rating_scoring_cubes_exchanged_made']] = -99, np.nan
```

In the scouting data we had our scouters give 'efficiency ratings' to teams on a 1-5 scale on how they performed in certain areas. Just as before, we've got null values we need to replace:

```python
# fix null "efficiency" ratings with a number between 1-5 based on the ratio of mades
# via the min and max of mades in the dataset

cols = [
   ('rating_attempted_switch', 'rating_overall_switch_efficiency', 'rating_scoring_cubes_on_switch_made'),
   ('rating_attempted_switch_auto', 'rating_overall_switch_efficiency_auto', 'rating_scoring_cubes_on_switch_auto_made'),
   ('rating_attempted_scale', 'rating_overall_scale_efficiency', 'rating_scoring_cubes_on_scale_made'),
   ('rating_attempted_scale_auto', 'rating_overall_scale_efficiency_auto', 'rating_scoring_cubes_on_scale_auto_made'),
   ('rating_attempted_exchange', 'rating_overall_exchange_efficiency', 'rating_scoring_cubes_exchanged_made')
]

for x in cols:
   x_min = scouting_reports_df.loc[scouting_reports_df[x[0]] == 1, x[2]].min()
   x_max = scouting_reports_df.loc[scouting_reports_df[x[0]] == 1, x[2]].max()
  
   scouting_reports_df[x[1]] = scouting_reports_df.apply(
       lambda r: r[x[1]] if pd.notnull(r[x[1]]) else np.ceil(((r[x[2]] - x_min) / (x_max - x_min)) * (5 - 1) + 1),
       axis=1)

cols_to_fill = list(scouting_reports_df.filter(regex='^rating_').columns)
# cols_to_fill

# convert remaining NaNs to their respective means BY team
scouting_reports_df[cols_to_fill] = scouting_reports_df.groupby('team_id')[cols_to_fill].transform(
   lambda x: x.fillna(x.mean()))
```

Now let's look at what our formatted scouting dataframe looks like:

```python
scouting_reports_df[(scouting_reports_df.team_id == 'frc2102')]
```
![img](images/scouting_app/jnb_4.png)

By calling a ```DataFrameSummary(scouting_reports_df).summary()``` we can see if anything looks off in our dataframe. As we can see below, there are still some NaN values we need to get rid of:

![img](images/scouting_app/jnb_5.png)

```python
# convert remaining NaNs to 0
scouting_reports_df.fillna(0, inplace=True)

#re-sort the columns alphanumerically
non_sorted = ['event_id', 'match_key', 'team_id']

# define sort order
scouting_reports_col_order = non_sorted + sorted(list(scouting_reports_df.columns.drop(non_sorted)))

scouting_reports_df = scouting_reports_df.reindex(scouting_reports_col_order, axis=1)
```

With everything cleaned up, we can save our dataframe as a csv file now:

```python
scouting_reports_df.to_csv(scouting_reports_file, index=False)
```

### Merging the Datasets

We now have 3 cleaned datasets to use in our model training, but to use all of them we need to combine them into 1 cohesive dataset. The first thing I can think of us needing to do is to remove redundant columns that the 3 datasets use for indexing rows (team number, date/time, etc.):

```python
match_scores_df = pd.read_csv(f'data/{comp_yr}-team-match-scores.csv')
event_stats_df = pd.read_csv(f'data/{comp_yr}-team-event-stats.csv')
scouting_df= pd.read_csv(f'data/{comp_yr}-scouting-reports.csv')

scouting_df.rename(columns={'event_id': 'event_key', 'team_id': 'team_key'}, inplace=True)

# merge match and event stats
merged_df = pd.merge(match_scores_df, event_stats_df, how='left', on=['event_key', 'team_key'])

print(len(merged_df))
merged_df.head(2)

# merge in scouting
merged_df = pd.merge(merged_df, scouting_df, how='left', on=['event_key', 'match_key', 'team_key'])

print(len(merged_df))
merged_df.head(2)

# sort by match date desc.
merged_df.sort_values(by=['event_week', 'event_key', 'actual_time', 'tba_alliance', 'scored_at'], inplace=True)

# deleting duplicate rows due to scouter error
dups_df = merged_df[merged_df.duplicated(subset=['event_key', 'match_key', 'team_key'], keep='first')]
len(dups_df)

merged_df.drop_duplicates(subset=['event_key', 'match_key', 'team_key'], keep='first', inplace=True)

# save merged dataframe
non_sorted = ['event_key', 'match_key', 'team_key', 'event_week', 'actual_time',
             'predicted_time', 'post_result_time', 'time', 'scored_at']

merged_col_order = ['event_key', 'match_key', 'team_key', 'event_week', 'actual_time', 'scored_at'] + \
                   list(merged_df.columns.drop(non_sorted)) + \
                   ['predicted_time', 'post_result_time', 'time']

merged_df = merged_df.reindex(merged_col_order, axis=1)
```

We now have a merged dataframe that's (almost) ready for DL. Time to save it as a csv and finish up our data cleaning with some preprocessing:

```python
merged_df.to_csv(merged_file, index=None)
```

### Preprocessing
After some trial and error when trying to train my models on the merged dataset, there have been a few things I've missed that are making my accuracy very low or were just preventing me from training anything all together.

To start, pandas needs date and time columns to be specified:

```python
# specify datatypes that pandas cannot infer, including datetime columns
date_cols = ['actual_time', 'post_result_time', 'predicted_time', 'time', 'scored_at']

# get matches
merged_df = pd.read_csv(merged_file, parse_dates=date_cols, low_memory=False)
merged_df.sort_values(by=['event_week', 'event_key', 'actual_time', 'tba_alliance', 'scored_at'], inplace=True)
merged_df.reset_index(drop=True, inplace=True)

merged_df.head()
```

![img](images/scouting_app/jnb_6.png)

#### Cleaning the Training Data

There are a lot of discrepancies with what TBA and scouters are putting down for end game scoring elements, and we may not want to use them in our models as they are messing with our results. Let's do some cleaning and make sure all the end game data matches up:

```python
cols = ['rating_scoring_climb', 'rating_scoring_number_of_robots_lifted', 'rating_scoring_park']

# if endgame == "Parking", then set scouting's climb and # of robots lifted = 0 and parking = 1
merged_df.loc[(merged_df.scored_at.isnull() != True) &
                (merged_df.tba_endgame_robot == 'Parking'), cols] = 0,0,1

# if endgame == "Levitate", then set scouting's climb and # of robots lifted = 0
merged_df.loc[(merged_df.scored_at.isnull() != True) &
             (merged_df.tba_endgame_robot == 'Levitate'), cols[:2]] = 0,0

# if endgame == "Climbing", set parking = 0
merged_df.loc[(merged_df.scored_at.isnull() != True) &
             (merged_df.tba_endgame_robot == 'Climbing'), [cols[0], cols[2]]] = 1,0

# if endgame == "Climbing", set climbs = 1 if climbing count == 1
merged_df.loc[(merged_df.scored_at.isnull() != True) &
                (merged_df.tba_endgame_robot == 'Climbing') &
                (merged_df.tba_endgame_robot_climb_count == 1), cols[:2]] = 1

# if tba_auto_robot == "1", then set scouting's rating_scoring_base_line_auto_made = 1
merged_df.loc[(merged_df.scored_at.isnull() != True),
             'rating_scoring_base_line_auto_made'] = (merged_df.tba_auto_robot == 1).astype(np.int64)
```

#### Adding Rolling Mean to TBA Data

A rolling mean is essentially a window that looks takes a grouping of values and returns a mean, with this window moving as more data is entered/received. With TBA data, it would make more sense for us to look at a rolling mean of values as the data we get from them (OPRS, scale ownership points, etc.) are all overall values for a team as it played on an alliance of 3 robots. If we want more *team specific* stats, using a rolling average over a set number of match numbers would make more sense. Let's make that new data frame for tba rolling columns:

```python
tba_rolling_cols = [ c for c in merged_df.filter(regex='^tba_').columns
                  if c not in [
                      'tba_alliance', 'tba_alliance_team_keys', 'tba_comp_level','tba_match_number',
                      'tba_set_number','tba_alliance_robot_pos', 'tba_event_week', 'tba_year',
                      'tba_tba_game_data', 'tba_is_winner','tba_auto_robot',
                      'tba_auto_robot1', 'tba_auto_robot2', 'tba_auto_robot3',
                      'tba_endgame_robot','tba_endgame_robot1', 'tba_endgame_robot2', 'tba_endgame_robot3']
                  ]

tba_rolling_new_cols = [ f'{c}_rolling' for c in tba_rolling_cols ]

g = merged_df.groupby(by='team_key')[tba_rolling_cols]
merged_df[tba_rolling_new_cols] = g.rolling(window=3, min_periods=1).mean().reset_index(0, drop=True)
```
We won't do this for scouting data because the scouting data is already team specific, so there's no need to take grouped averages of data that already is as "exact" as it could be for a team.

#### Additional Feature Engineering

There's a few more things to do before we train our models. Some of the feature engineering we'll do is purely for experimental use as this is the first time I've ever done any of the ML work on FRC robot/scouting data however. Anyways, let's try some things out:

Let's add minutes between matches. Maybe a quicker match turnaround doesn't affect very consistently performing teams. Or maybe we find something else:

```python
merged_df['mins_since_last_match'] = merged_df.groupby(['team_key', 'event_key'])['actual_time'].transform(
   lambda r: (r - r.shift(1)).dt.seconds // 60).fillna(0)

merged_df[merged_df.team_key=='frc2102'][['actual_time', 'mins_since_last_match']].head()
```
![img](images/scouting_app/jnb_7.png)

To make displaying our results to other teams easier, let's add in custom metrics that analyse the core game & scoring elements from a 1-10 scale. By grouping columns together we can provide a quick "summary" to teams that we'd otherwise have to explain how they relate to each other & their importance in relation to the game and opposing teams which would be a inconvenience if we had to do that to every team we spoke to during pre-match strategy. We need to be smart when we're grouping metrics together because if we just start picking random columns to pair up, we could be missing out on critical data points and making poor decisions:

```python
# filter to only include rows with scouting scores
team_ratings_df = merged_df.filter(regex='^rating_.*|team_key')[merged_df.scored_at.isnull() != True].copy()
team_ratings_g = team_ratings_df.groupby('team_key')

ability_to_climb =  team_ratings_g.rating_scoring_climb.mean()
ability_to_lift = team_ratings_g.rating_scoring_number_of_robots_lifted.mean()

ability_to_scale_auto = team_ratings_g.apply(lambda x:
       x[x.rating_attempted_scale_auto == 1].rating_overall_scale_efficiency_auto.mean() *
       x[x.rating_attempted_scale_auto == 1].rating_scoring_cubes_on_scale_auto_made.mean())

ability_to_scale_teleop = team_ratings_g.apply(lambda x:
       x[x.rating_attempted_scale == 1].rating_overall_scale_efficiency.mean() *
       x[x.rating_attempted_scale == 1].rating_scoring_cubes_on_scale_made.mean())

ability_to_switch_auto = team_ratings_g.apply(lambda x:
       x[x.rating_attempted_switch_auto == 1].rating_overall_switch_efficiency_auto.mean() *
       x[x.rating_attempted_switch_auto == 1].rating_scoring_cubes_on_switch_auto_made.mean())

ability_to_switch_teleop = team_ratings_g.apply(lambda x:
       x[x.rating_attempted_switch == 1].rating_overall_switch_efficiency.mean() *
       x[x.rating_attempted_switch == 1].rating_scoring_cubes_on_switch_made.mean())

ability_to_exchange_teleop = team_ratings_g.apply(lambda x:
       x[x.rating_attempted_exchange == 1].rating_overall_exchange_efficiency.mean() *
       x[x.rating_attempted_exchange == 1].rating_scoring_cubes_exchanged_made.mean())

team_ratings_df = pd.concat([
   ability_to_climb.rename('ability_to_climb'),
   ability_to_lift.rename('ability_to_lift'),
   ability_to_scale_auto.rename('ability_to_scale_auto'),
   ability_to_scale_teleop.rename('ability_to_scale_teleop'),
   ability_to_switch_auto.rename('ability_to_switch_auto'),
   ability_to_switch_teleop.rename('ability_to_switch_teleop'),
   ability_to_exchange_teleop.rename('ability_to_exchange_teleop')], axis=1).reset_index()

team_ratings_df[team_ratings_df.team_key=='frc2102']
```
![img](images/scouting_app/jnb_8.png)

Right now these values aren't normalized or on a 1-10 scale, so let's fix that:

```python
# normalize ability ratings to be between 0 and 1
cols = list(team_ratings_df.filter(regex='^ability_to_.*').columns)
team_ratings_df[cols] = team_ratings_df[cols].apply(lambda x: (x - x.min()) / (x.max() - x.min()))

# scale the ability ratings to be between 1 and 10
min_score = 1
max_score = 10

team_ratings_df[cols] = np.round((team_ratings_df[cols] * (max_score - min_score)) + min_score)

team_ratings_df = team_ratings_df.reset_index(drop=True)
team_ratings_df.fillna(1.0, inplace=True)

team_ratings_df.head()
```
![img](images/scouting_app/jnb_9.png)

Now we can view a summary of how all of the robots in the 2018 Turing Division stack up against each other:

```python
DataFrameSummary(team_ratings_df).summary()
```
![img](images/scouting_app/jnb_10.png)

Finally, let's merge our newly created dataframe with 1-10 metrics and our complete TBA and Scouting dataframe. We'll arrange our column order to clean things up, and then export our complete dataframe to a csv for Deep Learning:

```python
# merge in ability ratings
merged_df = pd.merge(merged_df, team_ratings_df, how='left', on=['team_key'])

non_sorted = [
   'event_key', 'match_key', 'team_key', 'event_week', 'actual_time', 'mins_since_last_match',
   'predicted_time', 'post_result_time', 'time', 'scored_at'
]

merged_col_order = ['event_key', 'match_key', 'team_key', 'event_week', 'actual_time', 'mins_since_last_match', 'scored_at'] + \
   sorted(list(merged_df.columns.drop(non_sorted))) + \
   ['predicted_time', 'post_result_time', 'time']

merged_df = merged_df.reindex(merged_col_order, axis=1)

merged_df.to_csv(pp_file, index=False)
```


