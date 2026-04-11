import argparse
import os
import re
import unicodedata

import pandas as pd


def build_clean_matches(df):    
    """
    Clean and normalize raw match-level data. Responsibilities:
    - Remove live / incomplete matches
    - Determine whether the source player was winner or loser
    - Assign correct ranking-at-match to winner and loser
    - Produce a readable, analysis-ready column layout
    """
    out = df.copy()
    # Ensure required provenance column exists
    if "source_player" not in out.columns:
        raise ValueError(
            "Column 'source_player' is required. Re-run scrape_matches.py to regenerate data with source_player."
        )
    # Explicitly normalize missing source_player values
    out["source_player"] = out["source_player"].where(out["source_player"].notna(), None)

    # Remove rows from the raw scrape that represent live/ongoing matches
    # These rows are not fixed history and should not be included in the cleaned dataset
    live_mask = out["score"].astype(str).str.lower().str.contains("live", na=False)
    empty_score_mask = out["score"].astype(str).str.strip().eq("")
    out = out[~(live_mask | empty_score_mask)].copy()

    def normalize_name(name):        
        """
        Normalize player names for comparison:
        - Handle NaN safely
        - Remove accents
        - Collapse whitespace
        - Lowercase
        """
        if pd.isna(name):
            return ""
        text = str(name).strip()
        text = unicodedata.normalize("NFKD", text)
        text = text.encode("ascii", "ignore").decode("ascii")
        text = re.sub(r"\s+", " ", text).strip().lower()
        return text

    def same_player(source, candidate):       
        """
        Determine whether two player name strings refer to the same person. Logic:
        - Compare fully normalized names
        - If not equal, allow suffix matching (e.g. last name only)
        """
        source_norm = normalize_name(source)
        candidate_norm = normalize_name(candidate)
        if not source_norm or not candidate_norm:
            return False
        # Exact normalized match
        if source_norm == candidate_norm:
            return True

        source_tokens = source_norm.split()
        candidate_tokens = candidate_norm.split()
        
        # Allow matching on trailing tokens (e.g. "Nadal" vs "Rafael Nadal")
        if len(candidate_tokens) <= len(source_tokens):
            return source_tokens[-len(candidate_tokens) :] == candidate_tokens
        return candidate_tokens[-len(source_tokens) :] == source_tokens
    
    # Determine whether the source player won or lost each match
    source_is_winner = out.apply(lambda row: same_player(row["source_player"], row["winner"]), axis=1)
    source_is_loser = out.apply(lambda row: same_player(row["source_player"], row["loser"]), axis=1)
    
    # Initialize new rank-at-match columns
    out["winner_rank_at_match"] = pd.NA
    out["loser_rank_at_match"] = pd.NA
    
    # If source player is winner:
    # - winner rank comes from rk
    # - loser rank comes from vrk
    out.loc[source_is_winner, "winner_rank_at_match"] = out.loc[source_is_winner, "rk"]
    out.loc[source_is_winner, "loser_rank_at_match"] = out.loc[source_is_winner, "vrk"]
    
    # If source player is loser:
    # - winner rank comes from vrk
    # - loser rank comes from rk
    out.loc[source_is_loser, "winner_rank_at_match"] = out.loc[source_is_loser, "vrk"]
    out.loc[source_is_loser, "loser_rank_at_match"] = out.loc[source_is_loser, "rk"]

    # Rename round column for readability
    out = out.rename(columns={"rd": "Round"})
    
    # Final column order for the cleaned dataset
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

    # Ensure all expected columns exist
    for c in cols:
        if c not in out.columns:
            out[c] = pd.NA

    out = out[cols]
    return out


def main():    
    """
    Command-line entry point for cleaning match data.
    Reads raw scraped matches, cleans and normalizes them,
    and writes an analysis-ready CSV.
    """
    parser = argparse.ArgumentParser(
        description="Create readable match columns and map ranks to winner/loser correctly."
    )
    parser.add_argument("--input", default=None, help="Input CSV path. Default: data/matches_raw.csv")
    parser.add_argument("--output", default=None, help="Output CSV path. Default: data/matches_clean.csv")
    args = parser.parse_args()

    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_path = args.input or os.path.join(base_dir, "..", "data", "matches_raw.csv")
    output_path = args.output or os.path.join(base_dir, "..", "data", "matches_clean.csv")
    
    # Load raw data
    df = pd.read_csv(input_path)
    # Clean and normalize match data
    clean_df = build_clean_matches(df)
    # Write cleaned output
    clean_df.to_csv(output_path, index=False)
    
    # Report unresolved rank mappings (diagnostic)
    unresolved = clean_df["winner_rank_at_match"].isna().sum()
    print(f"Saved {len(clean_df)} rows to: {output_path}")
    print(f"Rows with unresolved rank mapping: {int(unresolved)}")


if __name__ == "__main__":
    main()
