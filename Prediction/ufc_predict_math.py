## MMA Math Model

# CREDIT: MMA math model sourced from "The Combat Chronicler" (https://www.youtube.com/watch?v=d6KlvXnHJBo&list=PL58QqkGp8nAxDbF7B8gUx3ODBdPInUq6R&index=10)

# Model Rules --

#   Examine each fighters last 5 fights

#   - Losing:
    #   1. decision loss: -2 pts
    #   2. getting finished: -3 pts

#   - Bonus Categories:
    #   1. Age > 35: -5 pts, -1 extra for each year after
    #   2. Undefeated in UFC: +5pts
    #   3. Undefeated in last 5: +3pts
    #   4. Fighting in country of origin (Excluding US): +5pts


import pandas as pd
from typing import Optional

# Implemented Math Model --

# Point value dictionaries -

#   - Winning:
    #   1. beating champion: +16 pts
    #   2. beating rank 1: +15 pts
    #   3. beating rank 2: +14 pts
    #   ...
    #   16. beating rank 15: +1 pt

rankWinMap = {
    "chmp": 16,
    "1": 15,
    "2": 14,
    "3": 13,
    "4": 12,
    "5": 11,
    "6": 10,
    "7": 9,
    "8": 8,
    "9": 7,
    "10": 6,
    "11": 5,
    "12": 4,
    "13": 3,
    "14": 2,
    "15": 1,
}



#   - Methods of winning:
winMap = {
    #   1. Finishing an opponent: +5 pts
    "finish" : 5,
    #   2. Finish streak: +1 pt for every finish in the streak
    "finishStreak1x" : 1,
    #   3. More than 2 judges give you every round: +5 pts
    "2judgesWin" : 5
}

#   - Relative Victories:
    #   1. beat someone who beat opponent: +5 pts / 1 pt if loss was avenged by other fighter
        # - +5 additional pts if finish, +1 for each in a finish streak


def _get_last_fights(df: pd.DataFrame, fighter_id: int, last_n: int = 5) -> pd.DataFrame:
    """Return the last ``last_n`` fights for ``fighter_id`` sorted by most recent."""
    fighter_df = df[df["fighter_id"] == fighter_id]
    if "date" in fighter_df.columns:
        fighter_df = fighter_df.sort_values("date", ascending=False)
    return fighter_df.head(last_n)


def _base_score(last_fights: pd.DataFrame) -> int:
    """Calculate the base MMA Math score from a fighter's last fights."""
    score = 0
    finish_streak = 0

    for _, row in last_fights.iterrows():
        result = row.get("result", "")
        method = str(row.get("method", "")).lower()

        if result == "Win":
            rank = row.get("opponent_rank")
            champ = row.get("opponent_is_champ", False)
            if champ:
                score += rankWinMap["chmp"]
            elif pd.notna(rank) and str(int(rank)) in rankWinMap:
                score += rankWinMap[str(int(rank))]

            if method and method != "decision":
                finish_streak += 1
                score += winMap["finish"] + winMap["finishStreak1x"] * finish_streak
            else:
                finish_streak = 0

            if row.get("two_judges_all_rounds"):
                score += winMap["2judgesWin"]
        elif result == "Loss":
            finish_streak = 0
            if method and method != "decision":
                score -= 3
            else:
                score -= 2
        else:
            finish_streak = 0

    # Bonus rules
    if not last_fights.empty:
        first_row = last_fights.iloc[0]
        age = first_row.get("fighter_age")
        if pd.notna(age) and age > 35:
            score -= 5 + int(age - 35)

        total_losses = first_row.get("fighter_total_losses")
        if pd.notna(total_losses) and int(total_losses) == 0:
            score += 5

        fighter_country = first_row.get("fighter_country")
        if pd.notna(fighter_country) and fighter_country not in {"USA", "United States"}:
            fight_country_col = "fight_country" if "fight_country" in last_fights.columns else "location_country"
            if fight_country_col in last_fights.columns:
                if any(pd.notna(row.get(fight_country_col)) and row.get(fight_country_col) == fighter_country for _, row in last_fights.iterrows()):
                    score += 5

    if last_fights.shape[0] and (last_fights["result"] != "Loss").all():
        score += 3

    return score


def _relative_victory_score(df: pd.DataFrame, fighter_a: int, fighter_b: int, last_n: int = 5) -> int:
    """Return bonus points for fighter_a for relative victories over fighter_b."""
    a_fights = _get_last_fights(df, fighter_a, last_n)
    b_fights = _get_last_fights(df, fighter_b, last_n)

    score = 0
    for _, row in a_fights[a_fights["result"] == "Win"].iterrows():
        opp = row.get("opponent_id")
        if pd.isna(opp):
            continue

        losses_to_opp = b_fights[(b_fights["opponent_id"] == opp) & (b_fights["result"] == "Loss")]
        if not losses_to_opp.empty:
            avenged = b_fights[(b_fights["opponent_id"] == opp) & (b_fights["result"] == "Win") & (b_fights.index > losses_to_opp.index[0])]
            base = 1 if not avenged.empty else 5
            if str(row.get("method", "")).lower() != "decision":
                base += winMap["finish"]
                base += winMap["finishStreak1x"] * max(int(row.get("finish_streak", 1)) - 1, 0)
            score += base

    return score


def mathmodel(df: pd.DataFrame, fighter_id: int, opponent_id: Optional[int] = None, last_n: int = 5) -> int:
    """Calculate the MMA Math score for ``fighter_id``.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame containing fight history. Required columns:
        ``fighter_id``, ``opponent_id``, ``result``, ``method``, ``date`` and
        ``opponent_rank`` or ``opponent_is_champ``.
    fighter_id : int
        Fighter whose score to compute.
    opponent_id : int, optional
        If provided, relative victory points against ``opponent_id`` are
        included in the result.
    last_n : int, default ``5``
        Number of most recent fights to consider.
    """

    last_fights = _get_last_fights(df, fighter_id, last_n)
    score = _base_score(last_fights)

    if opponent_id is not None:
        score += _relative_victory_score(df, fighter_id, opponent_id, last_n)

    return score


def adjusted_scores(df: pd.DataFrame, fighter_a: int, fighter_b: int, last_n: int = 5) -> tuple[int, int]:
    """Return math model scores for both fighters including relative bonuses."""
    score_a = mathmodel(df, fighter_a, opponent_id=fighter_b, last_n=last_n)
    score_b = mathmodel(df, fighter_b, opponent_id=fighter_a, last_n=last_n)
    return score_a, score_b



