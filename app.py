from flask import Flask, render_template, request
from predictor import predict_game, ratings  # imports your model + function
import requests

app = Flask(__name__)

# --- Get FBS team list from CollegeFootballData API ---
headers = {
    "Authorization": "Bearer API_KEY"
}
teams_url = "https://api.collegefootballdata.com/teams/fbs?year=2025"
response = requests.get(teams_url, headers=headers)

if response.ok:
    fbs_teams = sorted([team["school"] for team in response.json()])
else:
    # fallback to whatever your model has if the API fails
    fbs_teams = sorted(ratings.index)

@app.route("/", methods=["GET", "POST"])
def home():
    result = None
    if request.method == "POST":
        home_team = request.form["home_team"]
        away_team = request.form["away_team"]

        try:
            margin, prob = predict_game(home_team, away_team)
            winner = home_team if margin > 0 else away_team
            result = f"{winner} is predicted to win by {abs(margin):.2f} points ({prob*100:.1f}% chance)."
        except KeyError:
            result = "One of those teams isn't available in the dataset."

    return render_template("index.html", teams=fbs_teams, result=result)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")