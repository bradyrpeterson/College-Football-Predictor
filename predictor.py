##Import needed packages
import pandas as pd
import numpy as np
import cfbd
import requests
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt


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

# --- Reshape stats to have one row per team ---
stats_wide = stats_df.pivot(index="team", columns="statName", values="statValue").reset_index()

# --- Create efficiency metrics ---
stats_wide["yardsPerPlay_off"] = stats_wide["totalYards"] / (stats_wide["rushingAttempts"] + stats_wide["passAttempts"])
stats_wide["yardsPerPlay_def"] = stats_wide["totalYardsOpponent"] / (stats_wide["rushingAttemptsOpponent"] + stats_wide["passAttemptsOpponent"])
stats_wide["thirdDownPct"] = stats_wide["thirdDownConversions"] / stats_wide["thirdDowns"]
stats_wide["turnoverMargin"] = stats_wide["turnoversOpponent"] - stats_wide["turnovers"]

# --- Keep useful columns only ---
useful = ["team", "yardsPerPlay_off", "yardsPerPlay_def", "thirdDownPct", "turnoverMargin"]
stats_clean = stats_wide[useful]
#Turn JSON into a data frame
df = pd.DataFrame([g.to_dict() for g in games])
#print("Columns available:", df.columns.tolist())
need_cols = ["season","week","homeTeam","awayTeam","homePoints","awayPoints"]
df = df[need_cols].dropna(subset=["homePoints","awayPoints"]).reset_index(drop=True)
if df.empty:
    raise RuntimeError("No completed games found (after dropping NaNs). Try a different year/week or rerun later.")

#Create features
df["margin"] = df["homePoints"] - df["awayPoints"]
teams = sorted(set(df["homeTeam"]).union(df["awayTeam"]))

#Make design matrix
X = pd.DataFrame(0, index=np.arange(len(df)), columns=teams)
for i, row in df.iterrows():
    X.loc[i, row["homeTeam"]] = 1    # +1 for home team
    X.loc[i, row["awayTeam"]] = -1   # -1 for away team

#Add home field column
X["home_field"] = 1

y = df["margin"]

# Step 5: fit linear regression
model = LinearRegression(fit_intercept=False)
model.fit(X, y)

# Step 6: extract team ratings + home-field advantage
coefs = pd.Series(model.coef_, index=X.columns)
home_field = coefs["home_field"]
ratings = coefs.drop("home_field")
ratings -= ratings.mean()   # normalize mean=0

##Merge together both team stats and ratings
ratings_df = pd.DataFrame({"team": ratings.index, "rating": ratings.values})
merged = ratings_df.merge(stats_clean, on="team", how="left")

# show top 15
#print("Estimated home-field advantage (points):", round(home_field, 2))
#Print(ratings.sort_values(ascending=False).head(15))

# Step 7: make a quick prediction function
def predict_game(home, away):
    rating_diff = ratings[home] - ratings[away]
    #Pull the home and away team stats and compare them
    h_stats = stats_clean.loc[stats_clean["team"] == home].iloc[0]
    a_stats = stats_clean.loc[stats_clean["team"] == away].iloc[0]
    
    # Compute stat differences
    ypp_diff = h_stats["yardsPerPlay_off"] - a_stats["yardsPerPlay_def"]
    third_down_diff = h_stats["thirdDownPct"] - a_stats["thirdDownPct"]
    turnover_diff = h_stats["turnoverMargin"] - a_stats["turnoverMargin"]

    #Different weights of each
    w_rating=0.7
    w_ypp=0.1
    w_third=0.05
    w_turnover=0.15
    margin=(w_rating*rating_diff+(w_ypp*ypp_diff*10)+(w_third*third_down_diff*20)+(w_turnover*turnover_diff)+home_field)

    prob = 1 / (1 + np.exp(-margin / 7))  # rough logistic
    return margin, prob

# example
m, p = predict_game("Florida State", "Ohio State")
print(f"\nPredicted margin {m:.2f}, win probability {p*100:.1f}%")

# Step 8: visualize
#ratings.sort_values(ascending=True).tail(25).plot(kind="barh", figsize=(6,8))
#plt.title("Top 25 Team Ratings (CFB 2025)")
#plt.xlabel("Power Rating (points above average)")
#plt.show()
