import pdfplumber
import pandas as pd
import re
# Detect tables in PDFs
# def scan_pdf_for_tables(pdf_path: str, max_pages: int | None = None):
#     """Extract rough tables using pdfplumber and score pages."""
#     results = []
#     with pdfplumber.open(pdf_path) as pdf:
#         pages = pdf.pages[:max_pages] if max_pages else pdf.pages
#         for i, page in enumerate(pages):
#             try:
#                 tables = page.extract_tables() or []
#             except Exception as e:
#                 results.append({"page": i, "n_tables": 0, "best_table_score": 0, "error": str(e)})
#                 continue

#             scored = [table_score(t) for t in tables]
#             best = max((s["score"] for s in scored), default=0)
#             results.append({
#                 "page": i,
#                 "n_tables": len(tables),
#                 "best_table_score": best,
#                 "best_rows": max((s["rows"] for s in scored), default=0),
#                 "best_cols": max((s["cols"] for s in scored), default=0),
#                 "note": "higher best_table_score usually means easier cleanup"
#             })
#     return pd.DataFrame(results).sort_values(["best_table_score", "n_tables"], ascending=False)

# def extract_tables_from_pages(pdf_path: str, pages: list[int]): 
#     extracted = []
#     with pdfplumber.open(pdf_path) as pdf:
#         for p in pages:
#             page = pdf.pages[p]
#             tables = page.extract_tables() or []
#             for ti, t in enumerate(tables):
#                 meta = table_score(t)
#                 extracted.append({
#                     "page": p,
#                     "table_index": ti,
#                     **meta,
#                     "table": t
#                 })
#     df = pd.DataFrame(extracted).sort_values("score", ascending=False)
#     return df

# set up what kinda table will be extracted:
table_settings_list = [{
    "vertical_strategy": "text",
    "horizontal_strategy": "text",
    },
# to detect the county names only...
     {
    "vertical_strategy": "lines",
    "horizontal_strategy": "text",
    # "intersection_tolerance": 5,
    # "snap_tolerance": 3,
    # "join_tolerance": 6,
    # "edge_min_length": 3,
    }]

def page_keep(page): # page is a pdfplumber page
    # there are many many tables, but luckily the county table are mostly concentrated, so we need to find them first. 
    # if there are more than three 'county' detected, then it might be a page that we want to keep....
    # pdf = pdfplumber.open(PDF1_PATH)
    # page = pdf.pages[p]
    county_counts = []   # we will simply see how many counties were detected, and then use this method to decide if we
                         # are going to send this page to OpenAI
    for table_setting in table_settings_list:
        tables = page.extract_tables(table_settings=table_setting) or []
        tables_df = pd.DataFrame(tables) if tables else pd.DataFrame()
        county_count = (    
             tables_df.stack(future_stack= True)
                 # or, .where(s.notna(), "")   , but not nessesary after 'future_stack'   # replace NaN/None with empty string 
                    .astype(str)
                    .str.contains(r"\bCounty\b", na=False)
                    .sum()
        )
        county_counts.append(county_count)
        #print('I find',county_count,' "County"s on this page using this method')
    county_number = max(county_counts)
    #print("There are",county_number, "detected on this page, so it is legit")
    return( int(county_number))

def select_page_numbers(pdf_path: str, county_n_threshold:int = 3) -> dict: 
    pdf = pdfplumber.open(pdf_path)
         # pdf = pdfplumber.open(PDF1_PATH)
    selected_pages = {}
    for pi, page in enumerate(pdf.pages):
        # print(pi)
        county_n_mentioned = page_keep(page)
        if county_n_mentioned >= county_n_threshold:
            selected_pages[pi] = county_n_mentioned
            print("There are",county_n_mentioned, "detected on page", pi, "so it is legit")
    total_n_detected = sum(selected_pages.values())
    print(
        f"Detected {total_n_detected} counties — "
        f"{'meets' if total_n_detected >= 254 else 'below'} threshold (254), the total number of Texan counties."
    )
    return(selected_pages) # python index, start with 0


def extract_begin_year(filename) -> int:
    s = filename.name if isinstance(filename, Path) else str(filename)

    # find digits before "-" 
    left = s.split("-", 1)[0]
    year  = int(re.findall(r'(\d+)', left)[-1])  # or [0]
    if year < 100:
        year += 2000
    return year
