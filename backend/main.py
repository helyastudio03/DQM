import io
import uuid
from typing import Dict, List, Optional

import pandas as pd
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from engine import run_matching

app = FastAPI(title="DQM — Data Matching Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory session store
sessions: Dict[str, pd.DataFrame] = {}


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    content = await file.read()
    filename = file.filename or ""

    try:
        if filename.endswith(".csv"):
            df = pd.read_csv(io.BytesIO(content))
        elif filename.endswith(".xlsx"):
            df = pd.read_excel(io.BytesIO(content))
        elif filename.endswith(".parquet"):
            df = pd.read_parquet(io.BytesIO(content))
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type. Use .csv, .xlsx, or .parquet")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse file: {str(e)}")

    session_id = str(uuid.uuid4())
    sessions[session_id] = df

    return {
        "session_id": session_id,
        "columns": df.columns.tolist(),
        "row_count": len(df),
    }


class FieldPair(BaseModel):
    col1: str
    col2: str


class MatchRequest(BaseModel):
    session_id_1: str
    session_id_2: str
    id_col_1: str
    id_col_2: str
    field_pairs: List[FieldPair]
    same_source: bool = False


@app.post("/match")
async def match(req: MatchRequest):
    if req.session_id_1 not in sessions:
        raise HTTPException(status_code=404, detail="Session 1 not found")
    if req.session_id_2 not in sessions:
        raise HTTPException(status_code=404, detail="Session 2 not found")

    df1 = sessions[req.session_id_1]
    df2 = sessions[req.session_id_2]

    pairs = [{"col1": fp.col1, "col2": fp.col2} for fp in req.field_pairs]

    results = run_matching(
        df1, df2,
        req.id_col_1, req.id_col_2,
        pairs,
        req.same_source,
    )

    # Sort by score descending
    results.sort(key=lambda x: x["match_score"], reverse=True)

    return {"results": results, "total_count": len(results)}


@app.post("/export")
async def export_results(req: MatchRequest):
    if req.session_id_1 not in sessions:
        raise HTTPException(status_code=404, detail="Session 1 not found")
    if req.session_id_2 not in sessions:
        raise HTTPException(status_code=404, detail="Session 2 not found")

    df1 = sessions[req.session_id_1]
    df2 = sessions[req.session_id_2]

    pairs = [{"col1": fp.col1, "col2": fp.col2} for fp in req.field_pairs]

    results = run_matching(
        df1, df2,
        req.id_col_1, req.id_col_2,
        pairs,
        req.same_source,
    )
    results.sort(key=lambda x: x["match_score"], reverse=True)

    # Flatten for export
    rows = []
    for r in results:
        row = {
            "id_source_1": r["id1_val"],
            "id_source_2": r["id2_val"],
            "match_score": r["match_score"],
        }
        for k, v in r["fields1_vals"].items():
            row[f"src1_{k}"] = v
        for k, v in r["fields2_vals"].items():
            row[f"src2_{k}"] = v
        rows.append(row)

    df_out = pd.DataFrame(rows)
    buf = io.StringIO()
    df_out.to_csv(buf, index=False)
    buf.seek(0)

    return StreamingResponse(
        io.BytesIO(buf.getvalue().encode("utf-8")),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=match_results.csv"},
    )


@app.delete("/session/{session_id}")
async def delete_session(session_id: str):
    if session_id in sessions:
        del sessions[session_id]
    return {"status": "ok"}
