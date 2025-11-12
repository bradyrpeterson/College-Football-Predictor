# 🏈 College Football Predictor (2025 Season)

This project predicts outcomes of **2025 college football games** using team performance data from the [CollegeFootballData API](https://collegefootballdata.com/).  
It applies a **linear regression model** to calculate team power ratings and combines them with basic efficiency metrics to estimate who will win and by how much. The
model is trained on every game that has happened and tries to fit a line that results in the smallest error 

---
# 💡 Purpose
I created this project to combine two of my passions sports and coding. I wanted to really understand how analytics can be used to predict games. This is working with real world
data so I can gain hands on experience with Flask development, APIs, and Machine Learning. Additionally, I am tracking the results week by week in order to see the accuracy of the model
at the end of the 2025 season

## ⚙️ Features

✅ Predicts the **winner**, **margin**, and **win probability** for any matchup  
✅ Each week it has a page with a predictions for every single game that week for FBS teams
✅ Pulls live data for the **2025 FBS season**  
✅ Uses **team-level stats** (yards per play, turnovers, 3rd-down %, etc.)  
✅ Simple **Flask web app** with dropdown menus for game selection  
✅ Cached **FBS team list** for faster performance and fewer API calls  

---

## 🧠 How It Works

The model assigns each team a **power rating** based on their game results.  
Each game contributes to a system of equations estimating expected point margins between teams.  
A small “home field” bonus is included to account for advantage when playing at home, which is calculated by the average home field variance.

When two teams are selected:
- Their ratings are subtracted to calculate an **expected margin of victory**.
- The ratings are then combined with efficiency metrics to predict a winner
- That margin is then converted to a **win probability** using a logistic function:  

\[
P(\text{win}) = \frac{1}{1 + e^{-\text{margin}/7}}
\]

The app takes the user’s input (home and away teams), runs this calculation, and displays the predicted winner, margin, and win probability directly in the browser.
