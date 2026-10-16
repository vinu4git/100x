import os

import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

PROMPT = (
    "You are an AI automation consultant. Read the workflow below, point out "
    "the bottlenecks, and suggest which steps could be automated with AI.\n\n"
    "Workflow: "
)


def diagnose(workflow: str) -> str:
    api_key = os.getenv("XAI_API_KEY") or os.getenv("GROQ_API_KEY")
    if not api_key:
        raise KeyError("XAI_API_KEY")

    r = requests.post(
        "https://api.x.ai/v1/chat/completions",
        headers={"Authorization": f"Bearer {api_key}"},
        json={
            "model": "grok-3-latest",
            "messages": [{"role": "user", "content": PROMPT + workflow}],
        },
        timeout=60,
    )
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]


app = FastAPI()


class DiagnoseRequest(BaseModel):
    workflow: str


class DiagnoseResponse(BaseModel):
    diagnosis: str


@app.post("/diagnose", response_model=DiagnoseResponse)
def diagnose_endpoint(req: DiagnoseRequest):
    try:
        return {"diagnosis": diagnose(req.workflow)}
    except KeyError:
        raise HTTPException(status_code=500, detail="XAI_API_KEY is not set")
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"xAI request failed: {e}")
