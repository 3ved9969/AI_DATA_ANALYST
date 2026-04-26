import os
import pandas as pd
from werkzeug.utils import secure_filename

def allowed_file(filename: str, allowed_extensions: set[str]) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_extensions


def save_uploaded_file(file, upload_folder: str) -> str:
    filename = secure_filename(file.filename)
    os.makedirs(upload_folder, exist_ok=True)
    path = os.path.join(upload_folder, filename)
    file.save(path)
    return path


def load_dataset(file_path: str) -> pd.DataFrame:
    if file_path.lower().endswith(".csv"):
        return pd.read_csv(file_path)
    return pd.read_excel(file_path)


def preprocess_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]
    df = df.drop_duplicates()

    for col in df.columns:
        if df[col].dtype == "object":
            df[col] = df[col].astype(str).str.strip()

    for col in df.columns:
        if df[col].dtype == "object":
            converted = pd.to_datetime(df[col], errors="coerce")
            if converted.notna().sum() > max(3, int(0.6 * len(df))):
                df[col] = converted
                continue

            numeric = pd.to_numeric(df[col], errors="coerce")
            if numeric.notna().sum() > max(3, int(0.6 * len(df))):
                df[col] = numeric

    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            df[col] = df[col].fillna(df[col].median())
        else:
            mode = df[col].mode(dropna=True)
            if not mode.empty:
                df[col] = df[col].replace("nan", pd.NA).fillna(mode.iloc[0])

    return df


def dataset_schema(df: pd.DataFrame) -> dict:
    return {
        "columns": list(df.columns),
        "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
        "rows": int(df.shape[0]),
        "columns_count": int(df.shape[1]),
    }