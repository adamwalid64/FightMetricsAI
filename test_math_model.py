import pandas as pd
from Prediction.ufc_predict_math import mathmodel


def test_base_and_relative():
    data = [
        {"fighter_id": 1, "opponent_id": 105, "result": "Loss", "method": "Decision", "date": "2022-01-01", "opponent_rank": 2,
         "fighter_age": 25, "fighter_total_losses": 2, "fighter_country": "USA", "two_judges_all_rounds": False},
        {"fighter_id": 1, "opponent_id": 104, "result": "Win", "method": "Decision", "date": "2022-06-01", "opponent_rank": 4,
         "fighter_age": 25, "fighter_total_losses": 2, "fighter_country": "USA", "two_judges_all_rounds": True},
        {"fighter_id": 1, "opponent_id": 103, "result": "Win", "method": "Submission", "date": "2023-01-01", "opponent_rank": 1,
         "fighter_age": 25, "fighter_total_losses": 2, "fighter_country": "USA"},
        {"fighter_id": 1, "opponent_id": 102, "result": "Win", "method": "TKO", "date": "2023-07-01", "opponent_rank": 3,
         "fighter_age": 25, "fighter_total_losses": 2, "fighter_country": "USA"},
        {"fighter_id": 1, "opponent_id": 101, "result": "Win", "method": "KO", "date": "2024-01-01", "opponent_rank": 5,
         "fighter_age": 25, "fighter_total_losses": 2, "fighter_country": "USA"},
        # Fighter B history
        {"fighter_id": 2, "opponent_id": 101, "result": "Loss", "method": "Decision", "date": "2023-06-01"},
        {"fighter_id": 2, "opponent_id": 201, "result": "Win", "method": "KO", "date": "2023-10-01"},
    ]
    df = pd.DataFrame(data)
    score = mathmodel(df, 1, opponent_id=2, last_n=5)
    assert score == 77
