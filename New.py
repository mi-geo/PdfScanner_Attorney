import pdfplumber
import pandas as pd
import numpy as np
# page 5 - 12
pdf_path = r"C:\Users\46798566\Downloads\AttorneyPopulationDensity2014-15.pdf"
out_csv  = r"C:\Users\46798566\Downloads\AttorneyPopulationDensity2014-15_pages14-20_combined.csv"
out_notable = r"C:\Users\46798566\Downloads\AttorneyPopulationDensity2014-15_pages14-20_no_table_pages.txt"

start_page = 4
end_page   = 11  # inclusive

table_settings = {
    "vertical_strategy": "lines",
    "horizontal_strategy": "lines",
    "intersection_tolerance": 5,
    "snap_tolerance": 3,
    "join_tolerance": 3,
    "edge_min_length": 3,
}

def clean_df_from_table(
    table,
    header_row=0,
    min_header_nonempty_ratio=0.6,
    drop_repeated_headers=True
):
    """
    Clean a raw pdfplumber table into a usable DataFrame.
    No applymap used.
    """

    # 1) Build DataFrame
    df = pd.DataFrame(table)

    # 2) Normalize empty / whitespace-only cells
    df = df.replace(r"^\s*$", np.nan, regex=True)
    df = df.dropna(how="all").dropna(axis=1, how="all")

    if df.empty:
        return df

    # 3) Strip whitespace ONLY on object columns (vectorized)
    obj_cols = df.select_dtypes(include="object").columns
    df[obj_cols] = df[obj_cols].apply(lambda s: s.str.strip())

    # 4) Decide whether header_row is really a header
    if len(df) > header_row + 1:
        candidate = df.iloc[header_row]
        data_row = df.iloc[header_row + 1]

        nonempty_ratio = candidate.notna().mean()

        # headers are usually shorter strings than data rows
        candidate_len = candidate.astype(str).str.len().mean()
        data_len = data_row.astype(str).str.len().mean()

        if nonempty_ratio >= min_header_nonempty_ratio and candidate_len <= data_len:
            df.columns = candidate.tolist()
            df = df.iloc[header_row + 1:].reset_index(drop=True)

    # 5) Clean column names (vectorized)
    df.columns = (
        pd.Series(df.columns)
        .astype(str)
        .str.strip()
        .str.replace(r"\s+", " ", regex=True)
    )

    # 6) Deduplicate column names safely
    counts = {}
    new_cols = []
    for c in df.columns:
        if c not in counts:
            counts[c] = 1
            new_cols.append(c)
        else:
            counts[c] += 1
            new_cols.append(f"{c}_{counts[c]}")
    df.columns = new_cols

    # 7) Drop repeated header rows (multi-page tables)
    if drop_repeated_headers:
        header_values = set(map(str, df.columns))
        mask = df.apply(
            lambda r: set(map(str, r.tolist())) == header_values,
            axis=1
        )
        df = df.loc[~mask].reset_index(drop=True)

    return df

all_parts = []
no_table_pages = []
canonical_cols = None

with pdfplumber.open(pdf_path) as pdf:
    for p in range(start_page , end_page):
        page = pdf.pages[p]
        print(page)
        tables = page.extract_tables(table_settings=table_settings) or []

        if len(tables) == 0:
            no_table_pages.append(p + 1)  # human page number
            continue

        for t in tables:
            df = clean_df_from_table(t)
            if df.empty:
                continue

            if canonical_cols is None:
                canonical_cols = list(df.columns)

            # Drop repeated header rows (multi-page table)
            if canonical_cols and len(df.columns) == len(canonical_cols):
                header_row_mask = df.apply(
                    lambda r: [str(x) for x in r.tolist()] == [str(c) for c in canonical_cols],
                    axis=1
                )
                df = df.loc[~header_row_mask].reset_index(drop=True)

            df["__page__"] = p + 1
            all_parts.append(df)

combined = pd.concat(all_parts, ignore_index=True, sort=False) if all_parts else pd.DataFrame()
combined.to_csv(out_csv, index=False)

with open(out_notable, "w", encoding="utf-8") as f:
    f.write("Pages with NO tables detected:\n")
    f.write(", ".join(map(str, no_table_pages)) if no_table_pages else "None")

# Minimal status (remove these two lines if you want total silence)
print("Saved CSV:", out_csv)
print("No-table pages:", no_table_pages)