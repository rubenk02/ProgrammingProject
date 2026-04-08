import argparse
import os

import pandas as pd


def build_clean_matches(df):
    out = df.copy()

    if "source_player" not in out.columns:
        raise ValueError(
            "Column 'source_player' is required. Re-run scrape_matches.py to regenerate data with source_player."
        )

    out["source_player"] = out["source_player"].where(out["source_player"].notna(), None)

    source_is_winner = out["source_player"] == out["winner"]
    source_is_loser = out["source_player"] == out["loser"]

    out["winner_rank_at_match"] = pd.NA
    out["loser_rank_at_match"] = pd.NA

    out.loc[source_is_winner, "winner_rank_at_match"] = out.loc[source_is_winner, "rk"]
    out.loc[source_is_winner, "loser_rank_at_match"] = out.loc[source_is_winner, "vrk"]

    out.loc[source_is_loser, "winner_rank_at_match"] = out.loc[source_is_loser, "vrk"]
    out.loc[source_is_loser, "loser_rank_at_match"] = out.loc[source_is_loser, "rk"]

    out = out.rename(columns={"rd": "Round"})

    cols = [
        "date",
        "tournament",
        "surface",
        "Round",
        "winner",
        "winner_rank_at_match",
        "loser",
        "loser_rank_at_match",
        "score",
        "source_player",
    ]

    for c in cols:
        if c not in out.columns:
            out[c] = pd.NA

    out = out[cols]
    return out


def main():
    parser = argparse.ArgumentParser(
        description="Create readable match columns and map ranks to winner/loser correctly."
    )
    parser.add_argument("--input", default=None, help="Input CSV path. Default: data/matches_raw.csv")
    parser.add_argument("--output", default=None, help="Output CSV path. Default: data/matches_clean.csv")
    args = parser.parse_args()

    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_path = args.input or os.path.join(base_dir, "..", "data", "matches_raw.csv")
    output_path = args.output or os.path.join(base_dir, "..", "data", "matches_clean.csv")

    df = pd.read_csv(input_path)
    clean_df = build_clean_matches(df)
    clean_df.to_csv(output_path, index=False)

    unresolved = clean_df["winner_rank_at_match"].isna().sum()
    print(f"Saved {len(clean_df)} rows to: {output_path}")
    print(f"Rows with unresolved rank mapping: {int(unresolved)}")


if __name__ == "__main__":
    main()
