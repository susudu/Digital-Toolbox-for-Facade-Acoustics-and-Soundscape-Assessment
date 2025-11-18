import sys, json, pandas as pd, os
from fastapi.responses import JSONResponse
from datetime import datetime

def process_file(file_path):
    df = pd.read_csv(file_path)
    summary = df.describe(include='all').to_dict()
    
    result = {
        "filename": os.path.basename(file_path),
        "processed_at": datetime.now().isoformat(),
        "summary": summary
    }

    os.makedirs("results", exist_ok=True)
    result_path = os.path.join("results", os.path.basename(file_path) + ".json")

    with open(result_path, "w") as f:
        json.dump(result, f, indent=2)

    print(f"Processed {file_path}, saved to {result_path}")
    
    return JSONResponse({
        "message": "File uploaded and saved successfully.",
        "processed_path": file_path,
        "saved_path": result_path
    })

if __name__ == "__main__":
    process_file(sys.argv[1])
