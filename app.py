# app.py
# app.py
import html
import io
import csv
from typing import List

from fastapi import FastAPI, Form, UploadFile, File, Request
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# Use your prediction component - ensure path is correct
from src.summarizer.components.model_prediction import ModelPrediction

app = FastAPI(title="TextSummarizer UI")

# Instantiate model predictor once (loads model into memory)
predictor = ModelPrediction(model_path="artifacts/model")

# Serve a static directory if you want (optional)
# app.mount("/static", StaticFiles(directory="static"), name="static")


# ---------- Frontend: modern single-page UI ----------
@app.get("/", response_class=HTMLResponse)
async def home():
    # Simple modern UI using Bootstrap 5 CDN and small JS
    return HTMLResponse(
        """
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8"/>
    <meta name="viewport" content="width=device-width, initial-scale=1"/>
    <title>TextSummarizer — Demo</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
      body { background: #f7fafc; }
      .card { border-radius: 12px; box-shadow: 0 6px 20px rgba(15,23,42,0.06); }
      .textarea { min-height: 180px; resize: vertical; }
      .spinner-border { width: 1.2rem; height: 1.2rem; }
      .footer { font-size: .85rem; color: #6b7280; }
      pre { white-space: pre-wrap; word-wrap: break-word; }
    </style>
  </head>
  <body>
    <div class="container py-5">
      <div class="row justify-content-center">
        <div class="col-lg-8">
          <div class="card p-4 mb-4">
            <h3 class="mb-1">📝 Text Summarizer</h3>
            <p class="text-muted mb-3">Paste text below, click <strong>Summarize</strong> — or upload a CSV with a <code>dialogue</code> column for batch summarization.</p>

            <div class="mb-3">
              <textarea id="inputText" class="form-control textarea" placeholder="Paste or type your text to summarize..."></textarea>
            </div>

            <div class="d-flex gap-2 mb-3">
              <button id="summarizeBtn" class="btn btn-primary">Summarize</button>
              <button id="clearBtn" class="btn btn-outline-secondary">Clear</button>
              <div id="spinner" style="display:none;" class="align-self-center">
                <div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div>
              </div>
            </div>

            <div id="resultCard" class="mt-3" style="display:none;">
              <div class="card p-3 bg-white">
                <h6 class="mb-2">Summary</h6>
                <pre id="summaryText" class="mb-0"></pre>
              </div>
            </div>
          </div>

          <div class="card p-4 mb-4">
            <h5 class="mb-2">Batch CSV Summarization</h5>
            <p class="text-muted">Upload a CSV file with a <code>dialogue</code> column. The server returns a CSV with a new <code>summary</code> column.</p>
            <form id="csvForm">
              <div class="mb-3">
                <input class="form-control" type="file" id="csvFile" accept=".csv"/>
              </div>
              <button class="btn btn-success" type="submit">Upload & Summarize</button>
            </form>
            <div id="downloadLink" class="mt-3" style="display:none;"></div>
          </div>

          <div class="card p-3 footer">
            <div>Local demo • Model loaded from <code>artifacts/model</code></div>
            <div class="mt-2">API: <code>POST /api/summarize</code> (JSON) • <code>POST /api/summarize_file</code> (multipart CSV)</div>
          </div>
        </div>
      </div>
    </div>

    <script>
      const summarizeBtn = document.getElementById("summarizeBtn");
      const clearBtn = document.getElementById("clearBtn");
      const inputText = document.getElementById("inputText");
      const spinner = document.getElementById("spinner");
      const resultCard = document.getElementById("resultCard");
      const summaryText = document.getElementById("summaryText");
      const csvForm = document.getElementById("csvForm");
      const csvFile = document.getElementById("csvFile");
      const downloadLink = document.getElementById("downloadLink");

      async function summarizeText() {
        const text = inputText.value.trim();
        if (!text) return alert("Please enter some text first.");
        spinner.style.display = "inline-block";
        summarizeBtn.disabled = true;
        try {
          const resp = await fetch("/api/summarize", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text })
          });
          const data = await resp.json();
          summaryText.textContent = data.summary;
          resultCard.style.display = "block";
        } catch (err) {
          alert("Error: " + (err.message || err));
        } finally {
          spinner.style.display = "none";
          summarizeBtn.disabled = false;
        }
      }

      summarizeBtn.addEventListener("click", summarizeText);
      clearBtn.addEventListener("click", () => {
        inputText.value = "";
        resultCard.style.display = "none";
      });

      csvForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        if (!csvFile.files.length) return alert("Please select a CSV file first.");
        const f = csvFile.files[0];
        const form = new FormData();
        form.append("file", f);
        downloadLink.style.display = "none";
        try {
          const resp = await fetch("/api/summarize_file", { method: "POST", body: form });
          if (!resp.ok) { const txt = await resp.text(); throw new Error(txt || "Upload failed"); }
          const blob = await resp.blob();
          const url = URL.createObjectURL(blob);
          downloadLink.innerHTML = `<a class="btn btn-outline-primary" href="${url}" download="summaries.csv">Download summaries.csv</a>`;
          downloadLink.style.display = "block";
        } catch (err) {
          alert("Error: " + (err.message || err));
        }
      });
    </script>

  </body>
</html>
"""
    )


# ---------- API: JSON summarize ----------
class SummarizeRequest(BaseModel):
    text: str


@app.post("/api/summarize")
async def api_summarize(req: SummarizeRequest):
    text = req.text.strip()
    if not text:
        return JSONResponse({"error": "Empty text"}, status_code=400)
    summary = predictor.summarize(text)
    return {"summary": summary}


# ---------- API: CSV file upload and batch summarize ----------
@app.post("/api/summarize_file")
async def api_summarize_file(file: UploadFile = File(...)):
    # Expect CSV with 'dialogue' column
    content = await file.read()
    try:
        text_io = io.StringIO(content.decode("utf-8"))
    except UnicodeDecodeError:
        # try alternative encodings if necessary
        text_io = io.StringIO(content.decode("latin-1"))

    reader = csv.DictReader(text_io)
    if "dialogue" not in reader.fieldnames:
        return JSONResponse({"error": "CSV must contain 'dialogue' column"}, status_code=400)

    rows = list(reader)
    # Summarize each dialogue
    out_rows = []
    for r in rows:
        dialogue_text = r.get("dialogue", "") or ""
        summary = predictor.summarize(dialogue_text)
        out_r = dict(r)
        out_r["summary"] = summary
        out_rows.append(out_r)

    # Create CSV output in-memory
    out_io = io.StringIO()
    fieldnames = list(out_rows[0].keys()) if out_rows else ["dialogue", "summary"]
    writer = csv.DictWriter(out_io, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(out_rows)
    out_io.seek(0)

    return StreamingResponse(io.BytesIO(out_io.getvalue().encode("utf-8")),
                             media_type="text/csv",
                             headers={"Content-Disposition": "attachment; filename=summaries.csv"})
