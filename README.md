# 🏈 College Football Power Rating Model (2025 Season)

## 📘 Overview
This project builds a simple **data-driven power rating model** for the 2025 college football season using the [CollegeFootballData API](https://collegefootballdata.com).  
It applies **linear regression** to estimate each team’s strength (in points above or below average), while accounting for home-field advantage.

---

## ⚙️ How It Works
1. **Pull game data**  
   The script uses the CFBD API to download all 2025 games with final scores.

2. **Build a design matrix**  
   Each game becomes an equation:
margin = (home_team_rating - away_team_rating) + home_field

Copy code
- Home team → +1  
- Away team → -1  
- Home field → +1 constant term  

3. **Train the model**  
A `LinearRegression` model from scikit-learn estimates:
- Each team’s power rating  
- The average home-field advantage (in points)

4. **Predict results**  
You can simulate any matchup with:
```python
predict_game("Penn State", "Virginia")
which outputs a predicted margin and win probability.

5. Visualize rankings
The model plots the top 25 teams as a horizontal bar chart.
