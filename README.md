🏈 College Football Predictor
📖 Overview

The College Football Predictor is a Python-based web application that uses real game data and team statistics to predict the outcome of college football games.
It uses linear regression to calculate team power ratings and provides a simple Flask web interface where users can select two FBS teams to see a predicted score margin and win probability.

⚙️ Features

✅ Uses real 2025 data from the CollegeFootballData API

✅ Calculates team power ratings from game margins
✅ Includes games vs FCS schools for more data, but limits the app dropdown to FBS teams only
✅ Displays predicted winner, expected margin, and win probability
✅ Simple Flask web interface that runs directly in a Codespace or local environment

🧠 How It Works

cfb_predictor.py (or predictor.py)

Fetches 2025 game results from the CFBD API

Builds a design matrix where each team has +1 (home), −1 (away), or 0 (not in the game)

Runs linear regression to find each team’s rating and home-field advantage

Produces a function:

predict_game(home_team, away_team)


that returns the predicted margin and win probability.

app.py

Starts a Flask server with two dropdowns (Home/Away)

Fetches the official list of 2025 FBS teams from the CFBD API

Calls predict_game() when the user submits the form

Displays the winner, expected margin, and win probability on the page

templates/index.html

Provides a clean, minimal interface with dropdowns for team selection and a “Predict Game” button
