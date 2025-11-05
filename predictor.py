##Import needed packages
import pandas as pd
import numpy as np
import cfbd
import requests
import json
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt

#Using configuration suggested by CFBD turn the games into a dataset
configuration = cfbd.Configuration(
    access_token = 'API_KEY')

with cfbd.ApiClient(configuration) as api_client:
    api_instance = cfbd.GamesApi(api_client)
    games = api_instance.get_games(year=2025)

#Using requests pull all the statistical data from the data set
stats_url = "https://api.collegefootballdata.com/stats/season?year=2025"
headers = {"Authorization": "Bearer API_KEY"}  # your key
stats_response = requests.get(stats_url, headers=headers)
stats_data = stats_response.json()
stats_df = pd.DataFrame(stats_data)

#Reshape stats to have one row per team
stats_wide = stats_df.pivot(index="team", columns="statName", values="statValue").reset_index()

# Create efficiency stats using the dataset
stats_wide["yardsPerPlay_off"] = stats_wide["totalYards"] / (stats_wide["rushingAttempts"] + stats_wide["passAttempts"])
stats_wide["yardsPerPlay_def"] = stats_wide["totalYardsOpponent"] / (stats_wide["rushingAttemptsOpponent"] + stats_wide["passAttemptsOpponent"])
stats_wide["thirdDownPct"] = stats_wide["thirdDownConversions"] / stats_wide["thirdDowns"]
stats_wide["turnoverMargin"] = stats_wide["turnoversOpponent"] - stats_wide["turnovers"]

# Keep only the stats that I plan on using
useful = ["team", "yardsPerPlay_off", "yardsPerPlay_def", "thirdDownPct", "turnoverMargin"]
stats_clean = stats_wide[useful]
#Turn JSON into a data frame
df = pd.DataFrame([g.to_dict() for g in games])
#In case I need to see what columns the game dataset has to offer
#print("Columns available:", df.columns.tolist())
need_cols = ["season","week","homeTeam","awayTeam","homePoints","awayPoints","homeConference","awayConference"]
df=df[need_cols].copy()
#Only care about games where one of the teams was FBS
# Load list of FBS teams
with open("fbs_teams_2025.json", "r") as f:
    fbs_teams = json.load(f)

#Only keep games if it involved an FBS team
df = df[df["homeTeam"].isin(fbs_teams) | df["awayTeam"].isin(fbs_teams)]

df=df.reset_index(drop=True)
#Need to make an upcoming data frame as well as a completed data frame
completed = df.dropna(subset=["homePoints","awayPoints"]).reset_index(drop=True)
upcoming=df[df["homePoints"].isna() | df["awayPoints"].isna()].reset_index(drop=True)
next_week = int(upcoming["week"].dropna().sort_values().unique()[0])

#define what margin is
#sort the dataframe to have a line of home and away teams
df=completed
df["margin"] = df["homePoints"] - df["awayPoints"]
teams = sorted(set(df["homeTeam"]).union(df["awayTeam"]))

#Make design matrix
#Must add 1 to hometeam that way the model knows who has the advantage

X = pd.DataFrame(0, index=np.arange(len(df)), columns=teams)
for i, row in df.iterrows():
    X.loc[i, row["homeTeam"]] = 1    # +1 for home team
    X.loc[i, row["awayTeam"]] = -1   # -1 for away team

#Add home field column
X["home_field"] = 1

#y is the dataframe margin column
y = df["margin"]

#Create the linear regression based on the margins
model = LinearRegression(fit_intercept=False)
model.fit(X, y)

#Ensure home field is counted for in the team ratings
coefs = pd.Series(model.coef_, index=X.columns)
home_field = coefs["home_field"]
ratings = coefs.drop("home_field")
#Make the average team=0
ratings -= ratings.mean()   



#Merge together both team stats and ratings
ratings_df = pd.DataFrame({"team": ratings.index, "rating": ratings.values})
merged = ratings_df.merge(stats_clean, on="team", how="left")

# In case I want to print the home field advantage calculation
#print("Estimated home-field advantage (points):", round(home_field, 2))
#In case I went to print the best teams strictly based on my powerindex
#print(ratings.sort_values(ascending=False).head(5))

#Prediciton function
def predict_game(home, away):
    rating_diff = ratings[home] - ratings[away]
    #Pull the home and away team stats and compare them
    h_stats = stats_clean.loc[stats_clean["team"] == home].iloc[0]
    a_stats = stats_clean.loc[stats_clean["team"] == away].iloc[0]
    
    # Compute stat differences between the two teams
    ypp_diff = h_stats["yardsPerPlay_off"] - a_stats["yardsPerPlay_def"]
    third_down_diff = h_stats["thirdDownPct"] - a_stats["thirdDownPct"]
    turnover_diff = h_stats["turnoverMargin"] - a_stats["turnoverMargin"]

    #Different weights of each
    w_rating=0.7
    w_ypp=0.1
    w_third=0.05
    w_turnover=0.15
    margin=(w_rating*rating_diff+(w_ypp*ypp_diff*10)+(w_third*third_down_diff*20)+(w_turnover*turnover_diff)+home_field)

    #Calculate probabiliy based on the idea that a team favored by 7 
    #has a 75% chance to win 
    prob = 1 / (1 + np.exp(-margin / 7))  # rough logistic
    return margin, prob

def get_upcoming_predictions(week=None):
    # Use the upcoming games dataset (no scores yet)
    games_to_predict = upcoming.copy()

    if week is not None:
        games_to_predict = games_to_predict[games_to_predict["week"].astype(int) == int(week)]

    predictions = []
    for _, game in games_to_predict.iterrows():
        home, away = game["homeTeam"], game["awayTeam"]

        #skip games where data or stats are missing
        if home not in ratings.index or away not in ratings.index:
            continue
        if home not in stats_clean["team"].values or away not in stats_clean["team"].values:
            continue

       
        try:
            margin, prob = predict_game(home, away)
            winner = home if margin > 0 else away
            predictions.append({
                "home": home,
                "away": away,
                "predicted_winner": winner,
                "margin": round(abs(margin), 2),
                "prob": round(prob * 100, 1) if margin > 0 else round((1 - prob) * 100, 1)
            })
        except Exception as e:
            print(f"Error predicting {home} vs {away}: {e}")
            continue

    return pd.DataFrame(predictions)



# How to print if I wasn't using the app
#m, p = predict_game("Florida State", "Ohio State")
#print(f"\nPredicted margin {m:.2f}, win probability {p*100:.1f}%")

