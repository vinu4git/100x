# pip install requests   ·   export GROQ_API_KEY=gsk_...
import csv, io, json, os, requests

SHEET = "https://docs.google.com/spreadsheets/d/1Kg6T-dJWaYx_JCPiRk3u0nBuAQcsCVRDPj1NFKP4WzM/gviz/tq?tqx=out:csv&headers=0"
CARD = {
  "type": "function",
  "function": {
    "name": "get_lecture_details",
    "description": "when the user asks specific learnings of a lecture from 100xEngineers Cohort 8 or when the name is not mentioned assume its our course",
    "parameters": {
      "type": "object",
      "properties": {
        "number": {
          "type": "integer",
          "description": "number"
        }
      },
      "required": [
        "number"
      ]
    }
  }
}

def get_lecture(number: int) -> dict:
    """The tool: plain code, no model."""
    for row in csv.reader(io.StringIO(requests.get(SHEET).text)):
        if row[1].startswith(f"{number}. "):
            return {"lecture": number, "Date": row[0], "Lecture title": row[1], "Type": row[2], "Tools": row[3]}
    return {"error": f"There is no lecture {number}. Lectures run from 1 to 19."}

messages = [{"role": "user", "content": "When is Lecture 12 of 100xEngineers Cohort 8, and what is it about?"}]
for _ in range(3):                              # the server decides when the loop stops
    r = requests.post("https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": "Bearer " + os.environ["GROQ_API_KEY"]},
        json={"model": "openai/gpt-oss-120b", "messages": messages, "tools": [CARD]}).json()
    msg = r["choices"][0]["message"]
    if not msg.get("tool_calls"):               # no request: this is the answer
        print("answer", msg["content"])
        break
    call = msg["tool_calls"][0]                 # the model asked; the server acts
    messages.append({"role": "assistant", "content": msg.get("content"), "tool_calls": [call]})
    args = json.loads(call["function"]["arguments"])
    result = get_lecture(**args)
    print("call  ", call["function"]["name"], args)
    print("result", result)
    messages.append({"role": "tool", "tool_call_id": call["id"], "content": json.dumps(result)})