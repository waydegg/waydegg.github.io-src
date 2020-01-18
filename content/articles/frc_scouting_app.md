Title: FRC Scouting App
Date: 2018-09-04 12:12
Modified: 2018-09-04 12:12
Tags: personal projects, robotics, scouting
Slug: frc-robotics-scouting
Authors: Wayde Gilliam
Summary: Using predictive analytics and deep learning to scout the best robots


#Overview

The competition format for FRC robotics consists of Qualification matches and Playoff matches. In the Qualification matches teams are randomly put with and against each other in teams of 3 to compete for a higher rank amongst the other teams at that event. In the playoff matches the top 8 seeded teams pick 2 other teams to join their "alliance" in a round-robin style order, and then compete with one another in a best of 3 matches in a quarterfinals, semifinals, and finals playoff rounds.

You can have the best engineered and performing robot in the 20+ year history of FRC robots, though by making poor choices in match strategy and alliance selection you're setting yourself up for failure. The group of students designing, machining, and programming the robot on my team is very small, so to make up for our lack in competitiveness due to robot ability we wanted to gain in match intelligence and strategic superiority. Now 4 years into development, my team's scouting app, RoboRecon, was intended to use predictive analytics, machine learning, and meaningful visualizations to give us a competitive edge by doing the following:

1. Determine qualification match-to-match strategy for how the 3 teams on our qualification alliances interact with each other and with the opposing 3 robots that we're competing against.
2. Decide our robot picklist for the playoff rounds, what the other 7 playoff alliances will look like, and how our alliance should play in each round of playoffs.
3. Predict how our robot and others will perform in the remaining matches at our current event, along with events that we'll be competing in the future.


Below is in-depth documentation on the entirety of how RoboRecon was developed and implemented, though the focus of the article will be the Deep Learning integration with the application. Here are links to the [web application](https://github.com/Paradox2102/RoboRecon-app), [database](https://github.com/Paradox2102/RoboRecon-db), and [Tableau WDC](https://github.com/Paradox2102/RoboRecon-wdc) github repositories if you want to follow along or see the completed work. If you're looking into creating your own scouting app for your team, there are instructions on how to get started on those github links. Feel free to contact me with any questions.

-----

## RoboRecon Web App

RoboRecon started out in 2016 just as a web application. The initial need for some form of web-based app came from the hassle and inefficiency of using paper as a means to record and handle scouting data. Previously, the scouting team would hand out stacks of paper for students to hand-scout teams during competitions. This was a time consuming and error-ridden process that I don't think I need to explain further as to why it sucked. We were just trying to use the data we collected to pick our alliance members during the playoff rounds, and that was so impractical with how we paper scouted we were better off just picking teams based on personal intuition. Seeing the issues with this the end of my freshmen year, myself and a few other teammates got together and began the development of the scouting application that would later turn into RoboRecon.

The application is put together using [Jekyll](https://jekyllrb.com/), built over a [Github Pages](https://pages.github.com) website, a static site generation framework that's really easy to setup and maintain. Javascript and Ruby are the primary languages used to put everything together. While RoboRecon is proprietary software to the team, [we have the previous year's web app code](https://github.com/Paradox2102/RoboRecon-app) available for teams to modify and implement for their own scouting applications. However, in this write up I'll be showing off the 2018 version of roborecon, just not the code.

### Scouting Dashboard
![Screenshot of scouting dashboard](images/scouting_app/scouting_dashboard.png)

Here, all teams of the specific event were looking at are listed with highlighted stats & metrics to best dictate robot capabilities in a match on on alliances. On the top of the page are links to other pages of the web app along with a login prompt (you'd need to be whitelisted in order to use the app anyways). On the top right is a search bar to look up specific teams, a filtering tool for columns, and buttons to get a copy of they data as a raw excel file.

### Match Screen

![Match Screen](images/scouting_app/matches.png)

All matches are listed in order of the event we're scouting with alliance and match score results. Each "cell" for a team is linked to a unique scouting report for that match. The Matches page is what scouters will be looking at when looking for teams to scout. In this year's version (2017 is depicted above) teams that have already have a scouter assigned to them are grayed out and unable to be selected for easier use of the app.

### Scouting Reports

How We Used To Scout
![Paper scouting](images/scouting_app/old_scouting.png)

How We Scout Now
![Web App Scouting](images/scouting_app/new_scouting.png) 

After selecting a team from the Matches page a scouter is directed to a Scouting Report. Each year this page changes as it's specifically tailored to the current game we're playing in. While some of the metrics we're looking for are objective like "Gears Scored" or "Climbing", much of the data we're wanting to collect is subjective such as "Pilot Competency" or "Gear Efficiency". A list of all submitted scouting reports can be seen on the "Scouting Reports" page.

We select what we want our scouters to be looking for based on not enough Blue Alliance Data. In addition the scouting data we look at from our team's scouters, we pull a large amount of data from [The Blue Alliance](https://www.thebluealliance.com) database, a privately owned and run website that tracks a numerous amount of robot stats. While a lot of their data is very useful to us, there are always several important metrics that TBA misses that we'll have to record ourselves. More on the TBA will be explained later.

### Match Intelligence Screen

![Match Screen](images/scouting_app/match_intel.png)

This page is probably the most used and most important. A Match Intelligence page can be reached by selecting a match from the Matches page. On it are highlighted stats from TBA and RoboRecon scouting data for both alliances, most of which are custom metrics that look at multiple stats and combine them into one for better analysis. To reiterate what has been mentioned before,the reason why RoboRecon has been so helpful is that it's very customizable. Many teams, especially in the early regionals, neglect the fact that the biggest factor in being competitive is to just have a working robot that does something in the 2 minutes and 30 seconds of a match. Because of this, we look at the last X matches when determining how well robots are performing, not an entire regional/season's worth of data. Typically it’s the last 2-3 matches that truly tell us how a team is performing, and the Match Intelligence page data is where the filtered data is displayed.

In the upper most section are "Match Stats" which consists of match data from whole alliances that the specified team has been on. These are stats that would be near impossible for a human scouter to record as there is simply too much going on in the match to keep track of everything, so by using generalized TBA data we can still infer how a specific team is performing. For example, in the 2017 FRC game there were hundreds of wiffle balls that robots shot into goals around the field. It would be very impractical for a scouter to try to count each individual ball shot/missed by a team, so that's why the Match Stats field exists.

In the next section below Match Stats, Team Stats better highlights how good a specific robot is based on custom metrics that mix TBA and subjective/objective scouter data. We want this screen to be as intuitive as possible, so by creating our own metrics we cut down on uninformative stats and best show what really matters to our alliance partners during pre-match strategizing.

A Strengths and Weaknesses section further highlights how our team and the 2 others on our alliance should be playing with each other and against the opposing 3 robots. When strategizing with our alliance before a match, this is the main section we'll focus on as it essentially tells everyone how to play the match and what to look out for.

### Single Robot Analysis

![Single Robot Analysis](images/scouting_app/team_stats.png)

From navigating through the Team Details page, users can access a complete analysis of individual teams that highlight raw TBA data, a score trend analysis, and a scouting report analysis. Having a simple visual representation to see how a team has performed across their matches helps us determine how teams are improving. This screen is very nice to look at after the first day of qualification matches as we can start to see trends of improved performance that other teams may not. Below a Scouting Report Analysis looks at the cumulative scouting data and displays a simple bar graph for scouters/alliance members to quickly look at and see where to improve.

---

## Firebase & TBA api

### Firebase

![Firebase Dashboard](images/scouting_app/firebase_dashboard.png)

For the past 4 years we've been using [Firebase](https://firebase.google.com) for storing all of our data. It's easy to authenticate new users, accessing data is very simple, and best of all its __free__! Some downsides to it are that understanding all the security rules and updating data is somewhat confusing, data can only be loaded over in javascript, and it's mildly demanding on the browser when loading all of the data elements. I don't see my team changing this anytime soon, as it works for what we're doing and gets the job done.

![Firebase Authentication](images/scouting_app/firebase_auth.png)


### TBA api

A majority of the data we use is gathered from a 3rd party group called [The Blue Alliance](https://www.thebluealliance.com) that takes in official data recorded by the [FIRST Events Api](https://frcevents2.docs.apiary.io/#reference/match-results/event-match-results), adds in some more useful metrics, and then allow teams to easily pull from their database with the [TBA Api](https://www.thebluealliance.com/apidocs/v3). See the "Tableau" section of this write up for examples on using the TBA api.

---

I don't know if I'll ever get around to adding into these sections :/

## Tableau
### WDC
### Visualizations


