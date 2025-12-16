# Score extracted tables
def table_score(table) -> dict:
    """Heuristic score for an extracted table (higher = likely cleaner)."""
    if not table:
        return {"rows": 0, "cols": 0, "cells": 0, "empty_frac": 1.0, "score": 0.0}
    rows = len(table)
    cols = max((len(r) for r in table), default=0)
    cells = sum(len(r) for r in table)
    empties = sum(1 for r in table for v in r if (v is None or str(v).strip() == ""))
    empty_frac = empties / max(cells, 1)
    # score favors reasonably wide tables with fewer empty cells
    score = (cols * rows) * (1 - empty_frac)
    return {"rows": rows, "cols": cols, "cells": cells, "empty_frac": empty_frac, "score": score}


