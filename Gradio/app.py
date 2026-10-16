import os

import gradio as gr
import requests

DIAGNOSE_API_URL = os.getenv("DIAGNOSE_API_URL", "http://127.0.0.1:8000/diagnose")

 

def respond(message, history):
    try:
        response = requests.post(
            DIAGNOSE_API_URL,
            json={"workflow": message},
            timeout=65,
        )
        if not response.ok:
            try:
                detail = response.json().get("detail", response.text)
            except ValueError:
                detail = response.text
            raise gr.Error(
                f"Diagnosis service returned {response.status_code}: {detail}"
            )
        return response.json()["diagnosis"]
    except requests.RequestException as error:
        raise gr.Error(f"Could not reach the diagnosis service: {error}") from error


gr.ChatInterface(fn=respond).launch()