from __future__ import annotations

"""MMA Math rating utilities.

This module implements the scoring formula described in the project
README.  Scores are computed from a fighter's last ``n`` UFC bouts and
optionally adjusted with "MMA math" relative victory bonuses.
"""

from typing import Optional
import pandas as pd

# ---------------------------------------------------------------------------
# Helper tables
# ---------------------------------------------------------------------------

# Ranking points: champion (0) through rank 15.
RANK_POINTS = {i: 16 - i for i in range(16)}
RANK_POINTS[0] = 16


def is_finish(method: str) -> bool:
    """Return ``True`` if ``method`` represents a finish."""
    return bool(method) and "decision" not in method.lower()


def _get_last_fights(df: pd.DataFrame, fighter_id: int, last_n: int = 5) -> pd.DataFrame:
    """Return the last ``last_n`` fights for ``fighter_id`` sorted chronologically."""
    fighter_df = df[df["fighter_id"] == fighter_id]
    if "date" in fighter_df.columns:
        fighter_df = fighter_df.sort_values("date")
    return fighter_df.tail(last_n)


def _base_score(last_fights: pd.DataFrame) -> int:
    """Calculate the base score without relative victory bonuses."""

    score = 0
    finish_streak = 0

    for _, row in last_fights.iterrows():
        result = row.get("result", "")
        method = row.get("method", "")
        rank = row.get("opponent_rank")
        champ = bool(row.get("opponent_is_champ", False))

        if result == "Win":
            if champ:
                score += RANK_POINTS[0]
            elif pd.notna(rank) and int(rank) in RANK_POINTS:
                score += RANK_POINTS[int(rank)]

            if is_finish(method):
                finish_streak += 1
                score += 5 + max(finish_streak - 1, 0)
            else:
                finish_streak = 0
                if row.get("two_judges_all_rounds"):
                    score += 5
        elif result == "Loss":
            finish_streak = 0
            if is_finish(method):
                score -= 3
            else:
                score -= 2
        else:
            finish_streak = 0

    if last_fights.empty:
        return score

    last_row = last_fights.iloc[-1]
    age = last_row.get("fighter_age")
    if pd.notna(age) and age > 35:
        score -= 5 + int(age - 35)

    total_losses = last_row.get("fighter_total_losses")
    if pd.notna(total_losses) and int(total_losses) == 0:
        score += 5
    elif (last_fights["result"] != "Loss").all():
        score += 3

    country = last_row.get("fighter_country")
    if pd.notna(country) and country not in {"USA", "United States"}:
        ccol = "fight_country" if "fight_country" in last_fights.columns else "location_country"
        if ccol in last_fights.columns and any(row.get(ccol) == country for _, row in last_fights.iterrows()):
            score += 5

    return score


def _relative_victory_score(df: pd.DataFrame, fighter_a: int, fighter_b: int, last_n: int = 5) -> int:
    """Return bonus points for fighter ``fighter_a`` over ``fighter_b``."""

    a_fights = _get_last_fights(df, fighter_a, last_n)
    b_fights = _get_last_fights(df, fighter_b, last_n)

    score = 0
    for _, row in a_fights[a_fights["result"] == "Win"].iterrows():
        opp = row.get("opponent_id")
        if pd.isna(opp):
            continue
        b_losses = b_fights[(b_fights["opponent_id"] == opp) & (b_fights["result"] == "Loss")]
        if b_losses.empty:
            continue
        loss_index = b_losses.index[0]
        avenged = not b_fights[(b_fights["opponent_id"] == opp) & (b_fights["result"] == "Win") & (b_fights.index > loss_index)].empty
        score += 1 if avenged else 5

    return score


def mathmodel(df: pd.DataFrame, fighter_id: int, opponent_id: Optional[int] = None, last_n: int = 5) -> int:
    """Compute the total MMA math score for ``fighter_id``."""

    last_fights = _get_last_fights(df, fighter_id, last_n)
    score = _base_score(last_fights)

    if opponent_id is not None:
        score += _relative_victory_score(df, fighter_id, opponent_id, last_n)

    return score


def adjusted_scores(df: pd.DataFrame, fighter_a: int, fighter_b: int, last_n: int = 5) -> tuple[int, int]:
    """Return scores for both fighters in a matchup."""
    score_a = mathmodel(df, fighter_a, opponent_id=fighter_b, last_n=last_n)
    score_b = mathmodel(df, fighter_b, opponent_id=fighter_a, last_n=last_n)
    return score_a, score_b