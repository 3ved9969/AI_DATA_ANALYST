import os
import uuid
import traceback
import pandas as pd
from flask import Flask, jsonify, render_template, request, send_from_directory, session

from config import Config
from utils.data_utils import (
    allowed_file,
    save_uploaded_file,
    load_dataset,
    preprocess_dataframe,
    dataset_schema,
)
from utils.analysis_engine import run_analysis
from utils.chart_utils import generate_chart
from utils.gemini_client import GeminiClient
from utils.report_utils import create_pdf_report

app = Flask(__name__)
app.config.from_object(Config)

os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
os.makedirs(app.config["CHART_FOLDER"], exist_ok=True)
os.makedirs("reports", exist_ok=True)

app.secret_key = app.config["SECRET_KEY"]

gemini = GeminiClient(app.config["GEMINI_API_KEY"])
DATASTORE: dict[str, pd.DataFrame] = {}


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload_file():
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file part provided"}), 400

        file = request.files["file"]

        if file.filename == "":
            return jsonify({"error": "No file selected"}), 400

        if not allowed_file(file.filename, app.config["ALLOWED_EXTENSIONS"]):
            return jsonify({"error": "Only CSV and Excel files are allowed"}), 400

        file_path = save_uploaded_file(file, app.config["UPLOAD_FOLDER"])
        df = load_dataset(file_path)
        df = preprocess_dataframe(df)

        dataset_id = uuid.uuid4().hex
        DATASTORE[dataset_id] = df
        session["dataset_id"] = dataset_id

        schema = dataset_schema(df)
        preview = df.head(10).fillna("").astype(str).to_dict(orient="records")

        return jsonify({
            "message": "File uploaded and processed successfully",
            "dataset_id": dataset_id,
            "schema": schema,
            "preview": preview,
        })

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": f"Upload failed: {str(e)}"}), 500


@app.route("/query", methods=["POST"])
def query_data():
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "Invalid JSON request"}), 400

        question = data.get("question", "").strip()
        dataset_id = session.get("dataset_id") or data.get("dataset_id")

        if not dataset_id or dataset_id not in DATASTORE:
            return jsonify({"error": "No dataset uploaded"}), 400

        if not question:
            return jsonify({"error": "Question is required"}), 400

        df = DATASTORE[dataset_id]
        schema = dataset_schema(df)

        try:
            intent_payload = gemini.get_intent(question, schema)
        except Exception as e:
            traceback.print_exc()
            return jsonify({"error": f"Gemini intent parsing failed: {str(e)}"}), 500

        result_df, computed_summary = run_analysis(df, intent_payload)

        chart_file = generate_chart(
            result_df,
            intent_payload.get("chart_type"),
            app.config["CHART_FOLDER"]
        )

        summary_payload = {
            **computed_summary,
            "intent_payload": intent_payload,
            "result_preview": result_df.head(10).fillna("").astype(str).to_dict(orient="records"),
        }

        try:
            insight = gemini.generate_insight(question, summary_payload)
        except Exception as e:
            traceback.print_exc()
            insight = {
                "headline": "Insight generation unavailable",
                "insight": f"Analysis completed, but Gemini insight generation failed: {str(e)}",
                "possible_reason": "API issue or invalid JSON returned by the model",
                "recommendation": "Check Gemini API key, model response, and prompt format",
            }

        report_name = f"report_{uuid.uuid4().hex}.pdf"
        report_path = os.path.join("reports", report_name)

        create_pdf_report(
            report_path=report_path,
            title="GenAI Data Analyst Report",
            summary=summary_payload,
            insight=insight,
        )

        return jsonify({
            "intent_payload": intent_payload,
            "result": result_df.head(50).fillna("").astype(str).to_dict(orient="records"),
            "columns": list(result_df.columns),
            "chart_url": f"/charts/{chart_file}" if chart_file else None,
            "insight": insight,
            "report_url": f"/reports/{report_name}",
        })

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": f"Query processing failed: {str(e)}"}), 500


@app.route("/charts/<path:filename>")
def serve_chart(filename):
    return send_from_directory(app.config["CHART_FOLDER"], filename)


@app.route("/reports/<path:filename>")
def serve_report(filename):
    return send_from_directory("reports", filename)


@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "ok",
        "gemini_key_loaded": bool(app.config["GEMINI_API_KEY"]),
        "datasets_in_memory": len(DATASTORE),
    })


if __name__ == "__main__":
    app.run(debug=True)