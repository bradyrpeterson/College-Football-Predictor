from flask import Flask, render_template, request
from predictor import predict_game, ratings  # imports your existing model + function

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():
    result = None
    if request.method == "POST":
        home_team = request.form["home_team"]
        away_team = request.form["away_team"]
        margin, prob = predict_game(home_team, away_team)
        winner = home_team if margin > 0 else away_team
        result = f"{winner} is predicted to win by {abs(margin):.2f} points ({prob*100:.1f}% chance)."
    return render_template("index.html", teams=sorted(ratings.index), result=result)

if __name__ == "__main__":
    app.run(debug=True)
