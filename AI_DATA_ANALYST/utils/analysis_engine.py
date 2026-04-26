import pandas as pd
def _safe_col(df: pd.DataFrame, col: str | None) -> str | None:
    if col and col in df.columns:
        return col
    return None


def run_analysis(df: pd.DataFrame, intent_payload: dict) -> tuple[pd.DataFrame, dict]:
    intent = intent_payload.get("intent")
    target_columns = intent_payload.get("target_columns", [])
    group_by = _safe_col(df, intent_payload.get("group_by"))
    metric = intent_payload.get("metric")
    sort_order = intent_payload.get("sort_order")
    top_n = intent_payload.get("top_n", 5)

    result = df.copy()
    summary = {
        "intent": intent,
        "rows_before": int(df.shape[0]),
        "columns": list(df.columns),
    }

    if intent == "preview_data":
        result = df.head(10)
        summary["message"] = "Showing first 10 rows"
        return result, summary

    if intent == "describe_data":
        result = df.describe(include="all").fillna("")
        summary["message"] = "Dataset statistical summary"
        return result.reset_index(), summary

    if intent == "missing_values_check":
        result = df.isna().sum().reset_index()
        result.columns = ["column", "missing_count"]
        summary["message"] = "Missing values by column"
        return result, summary

    numeric_cols = [c for c in target_columns if c in df.columns and pd.api.types.is_numeric_dtype(df[c])]
    first_numeric = numeric_cols[0] if numeric_cols else None
    first_target = _safe_col(df, target_columns[0] if target_columns else None)

    if intent == "top_n" and first_target:
        counts = df[first_target].value_counts().head(top_n).reset_index()
        counts.columns = [first_target, "count"]
        result = counts
        summary["top_category"] = counts.iloc[0].to_dict() if not counts.empty else {}
        return result, summary

    if intent == "group_summary" and group_by:
        if first_numeric and metric in {"sum", "mean", "max", "min"}:
            grouped = getattr(df.groupby(group_by)[first_numeric], metric)().reset_index()
            grouped.columns = [group_by, f"{metric}_{first_numeric}"]
            result = grouped
        else:
            grouped = df.groupby(group_by).size().reset_index(name="count")
            result = grouped
        if sort_order in {"asc", "desc"}:
            result = result.sort_values(by=result.columns[-1], ascending=(sort_order == "asc"))
        summary["top_rows"] = result.head(5).to_dict(orient="records")
        return result, summary

    if intent == "filter_summary":
        summary_df = df.copy()
        result = summary_df.head(20)
        summary["message"] = "Basic filtered summary not fully parameterized; extend filters if needed"
        return result, summary

    if intent == "trend_over_time":
        date_cols = [c for c in df.columns if pd.api.types.is_datetime64_any_dtype(df[c])]
        date_col = date_cols[0] if date_cols else None
        if date_col and first_numeric:
            temp = df[[date_col, first_numeric]].dropna().copy()
            temp["period"] = temp[date_col].dt.to_period("M").astype(str)
    return result, summary