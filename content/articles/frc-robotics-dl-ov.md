Title: DL/ML in FRC Robotics Scouting/Strategy
Date: 2018-10-25 12:12
Modified: 2018-10-25 12:12
Tags: personal projects, robotics, scouting, deep learning
Slug: frc-robotics-dl-ov
Authors: Wayde Gilliam
Summary: Using predictive analytics and deep learning to scout the best robots


After having Roborecon for 2 years with its benefits clearly paying off, I wanted to see if we could push our scouting abilities even further. I had been hearing about how FRC teams are starting to use machine learning in their vision software and autonomous routines, and I was interested to see if I could apply ML/DL to scouting data and get accurate predictions. I had already gone through [Andrew Ng's "Machine Learning"](https://www.coursera.org/learn/machine-learning) course and had just started going through [Fastai's Practical Deep Learning for Coders Part 1](fast.ai), so I was still very new to this field.

As it turns out, yes, you can use Deep Learning in FRC scouting. There are tons of areas it can be used in. My scouting team and I determined a list of uses for the ML analysis that could potentially change the way we perform at competitions completely:

1. Correcting human error. When you're forcing the limited number of unwilling Freshmen on your team to scout during competition, they're going to mislabel data and entirely forget to scout some matches. Early in the season when we start out with having no data from teams for that year, it's critical that we correctly record how they're performing during the 8-11 qualification matches they get before alliance selections or we might miss pick a team and jeopardize our entire season.

2. Predicting match and event outcomes before they've happened. There are thousands of FRC teams with hundreds competing simultaneously during competition season, so the only way we could scout all of them is with the help of ML algorithms. Going into the Turing Division in 2018 at the Houston World Championships we already had match predictions and team specific stats for the 67 teams attending, most of which we had never seen compete, thanks to Deep Learning.

3. Revealing missed important match and team data. From using the Roborecon web app in the past, we'd discovered certain robot attributes that we thought mattered were irrelevant, and others we thought weren't that important actually mattered a lot. Implementing deep learning into our scouting application would only further these discoveries.

I'm going to assume you have a basic understanding of Python, [Jupyter Notebooks](http://jupyter.org), and ML/DL as I go into detail on my code and how I put everything together in this section of the writeup. Feel free to contact me with any questions or help for getting world class predictions on your own scouting data because really anyone can do this. As RoboRecon is proprietary software to Team Paradox, I'll be highlighting what code we presented at the 2018 Houston World Championships that we made public.

---

This ended up being a pretty comprehensive write up, so the Data Cleaning stuff is on a separate page (can't share the modeling as its the "secret sauce" of the whole application!)

## [Data Cleaning](/frc-robotics-dl.html)


