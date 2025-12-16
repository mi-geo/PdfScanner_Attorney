# src/prompts.py

def generate_openai_prompt( txt_input, output_format):
    assert output_format in {"json", "csv"}
    schema_hint = "- Output ONLY CSV text. Anything else is invalid." if output_format == "csv" else "Output ONLY JSON text. Anything else is invalid."
    prompt = f"""
You are extracting structured data from ONE PAGE of a PDF report.

The page should only contain:
- county rows
- headers, footnotes, or repeated titles

INPUT (raw text from a single PDF page):
{txt_input}

TASK:
From this page, extract ONLY rows that represent:
- Texas counties
- Texas MSAs (ONLY if you are confident the row is an MSA)

For EACH extracted row, keep ONLY the following information:

REQUIRED FIELDS:
1. Name
   - Use the county name exactly as written
   - Do NOT invent or normalize names

2. Texas Attorneys
   - The number of active in-state Texas attorneys
   - Ignore the year/date in the column header
   - Keep the numeric value only

3. Texas Population
   - The Texas population value
   - Ignore the year/date in the column header
   - Keep the numeric value only

4. Ratio of Attorneys to Population
   - Preserve the ratio exactly as written (e.g., "1:2,705", "1:--")

5. Attorneys as a Percent of Total In-State Attorneys
   - Preserve the percentage exactly as written (e.g., "0.01%")

EXCLUSION RULES:
- Drop any columns not listed above
- Drop footnotes, notes, totals, or explanatory text
- Do NOT infer missing values
- If a required value is missing, use null (JSON) or empty (CSV)

OUTPUT FORMAT:
- First row MUST be the header
- One row per county
- No markdown
- No commentary
- No extra text

STRICT RULE:
{schema_hint}
"""
    return(prompt)

def generate_openai_prompt_doublecheck (page_text, target_counties, output_format, headers):
    county_list = ", ".join(target_counties)
    assert output_format in {"json", "csv"}
    schema_hint = "- Output ONLY CSV text. Anything else is invalid." if output_format == "csv" else "Output ONLY JSON text. Anything else is invalid."
    prompt = f"""
You are re-checking ONE PAGE of a PDF table.

TARGET COUNTIES (these may be missing or misread):
{county_list}

INPUT (raw text from the page):
{page_text}

TASK:
- Look ONLY for rows corresponding to the TARGET COUNTIES above.
- These rows may be:
  - split across lines
  - partially wrapped
  - misaligned
  - preceded by symbols or indentation

RULES:
- If a target county is present on this page, extract it.
- If it is NOT present, do not fabricate it.
- Only extract rows you are confident about.

OUTPUT:
- One row per county found
- If none are found, output an empty {output_format.upper()} (header only)
headers shoul have EXACT order, with EXACT spelling:
{headers}

STRICT RULE:
{schema_hint}
"""
    return(prompt)



class legacy_prompts: # aka prompts I tried but didn't work well 
    def generate_openai_prompt_legacy( txt_input, output_format):
        assert output_format in {"json", "csv"}
        schema_hint = "- Output format: CSV with header row." if output_format == "json" else "- Output format: JSON array of objects."
        prompt = f"""
    You are cleaning a table extracted from a PDF.
    
    INPUT (CSV-like rows, may be messy/wrapped):
    {txt_input}
    
    TASK:
    - Reconstruct a clean table with consistent columns.
    - If there is a clear header row, use it.
    - Remove obvious repeated header rows.
    - Preserve the exact row labels (e.g., county names) as they appear.
    - Only keep the rows with county name in it. 
    - If a value is missing, use null (for JSON) or empty (for CSV).
    
    OUTPUT REQUIREMENTS:
    {schema_hint}
    
    STRICT RULES:
    - Output ONLY the final {output_format.upper()}.
    - No explanations, no extra text, no markdown, no code fences.
    """
        return(prompt)
    
    COUNTY_TABLE_PROMPT = """
    Extract county-level tables from the provided PDF page.
    
    Rules:
    - Keep ONLY county rows
    - Exclude MSAs / CBSAs
    - Return structured JSON
    - Preserve numeric values exactly
    """
    
    COUNTY_TABLE_PROMPT2 =  """
    Extract tables from the PDF.
    
    Rules:
    - Keep ONLY rows that are counties, exclude MSAs and other non related rows
    - Ignore any MSA / Metro / CBSA rows.
    - Extract all 254 counties, each county as a row
    - Convert the result as a csv file so it is easy to convert
    - Use EXACTLY these keys for each record, leave the record as NA if you can not find the record
    [
      {
        "county name": "Hardin County",
        "active in state texas attorney": "59",
        "population": "1,275,648",       # here in the table in the pdf, Texas population means the population in that county
        "ratio of attorney to population": "1:508",
        "attorney as a percentage of total in state attorney",  "0.92%"
      }
    ]
    
    Notes:
    - “Texas population” in the table means the population in that county.
    
    """