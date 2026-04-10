import argparse
import os

import pandas as pd


RENAME_MAP = {
    "match": "match_record",
    "tiebreak": "tiebreak_record",
    "ace%": "ace_rate_pct",
    "1stin": "first_serve_in_pct",
    "1st%": "first_serve_points_won_pct",
    "2nd%": "second_serve_points_won_pct",
    "hld%": "service_games_held_pct",
    "spw": "service_points_won_pct",
    "brk%": "return_games_won_pct",
    "rpw": "return_points_won_pct",
    "tpw": "total_points_won_pct",
    "dr": "dominance_ratio",
}


def build_clean_stats(df):
    out = df.copy()
    out = out.rename(columns=RENAME_MAP)

    # Parse record fields into separate numeric columns
    if "match_record" in out.columns:
        match_parts = out["match_record"].astype(str).str.extract(
            r"(\d+)-(\d+)\s*\((\d+%|-)\)"
        )
        out["match_wins"] = pd.to_numeric(match_parts[0], errors="coerce").astype("Int64")
        out["match_losses"] = pd.to_numeric(match_parts[1], errors="coerce").astype("Int64")
        out["match_pct"] = match_parts[2].replace("-", 0)

    if "tiebreak_record" in out.columns:
        tiebreak_parts = out["tiebreak_record"].astype(str).str.extract(
            r"(\d+)-(\d+)\s*\((\d+%|-)\)"
        )
        out["tiebreak_wins"] = pd.to_numeric(tiebreak_parts[0], errors="coerce").astype("Int64")
        out["tiebreak_losses"] = pd.to_numeric(tiebreak_parts[1], errors="coerce").astype("Int64")
        out["tiebreak_pct"] = tiebreak_parts[2].replace("-", 0)
    stat_cols = [
    "ace_rate_pct", "first_serve_in_pct", "first_serve_points_won_pct",
    "second_serve_points_won_pct", "service_games_held_pct", "service_points_won_pct",
    "return_games_won_pct", "return_points_won_pct", "total_points_won_pct", "dominance_ratio"
    ]
    # Stat columns use NaN (not 0) for missing surface data: player never played on that surface,
    # so 0 would falsely imply poor performance rather than absence of data
    out[stat_cols] = out[stat_cols].replace("-", pd.NA)

    preferred_order = [
        "player",
        "surface",
        "match_record",
        "match_wins",
        "match_losses",
        "match_pct",
        "tiebreak_record",
        "tiebreak_wins",
        "tiebreak_losses",
        "tiebreak_pct",
        "ace_rate_pct",
        "first_serve_in_pct",
        "first_serve_points_won_pct",
        "second_serve_points_won_pct",
        "service_games_held_pct",
        "service_points_won_pct",
        "return_games_won_pct",
        "return_points_won_pct",
        "total_points_won_pct",
        "dominance_ratio",
    ]

    existing_preferred = [c for c in preferred_order if c in out.columns]
    other_columns = [c for c in out.columns if c not in existing_preferred]
    out = out[existing_preferred + other_columns]

    return out


def main():
    parser = argparse.ArgumentParser(description="Rename stats columns to readable names.")
    parser.add_argument("--input", default=None, help="Input CSV path. Default: data/stats_raw.csv")
    parser.add_argument("--output", default=None, help="Output CSV path. Default: data/stats_clean.csv")
    args = parser.parse_args()

    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_path = args.input or os.path.join(base_dir, "..", "data", "stats_raw.csv")
    output_path = args.output or os.path.join(base_dir, "..", "data", "stats_clean.csv")

    df = pd.read_csv(input_path)
    clean_df = build_clean_stats(df)
    clean_df.to_csv(output_path, index=False)

    print(f"Saved {len(clean_df)} rows to: {output_path}")


if __name__ == "__main__":
    main()
