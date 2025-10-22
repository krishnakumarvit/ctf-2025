from flask import Flask, request, render_template, jsonify
import os
import re

app = Flask(__name__, template_folder='templates')

# Load the "system prompt" (contains the secret flag)
with open(os.path.join(os.path.dirname(__file__), "system_prompt.txt"), "r") as f:
    SYSTEM_PROMPT = f.read()

def naive_model(system_prompt: str, user_input: str) -> str:
    """
    A deliberately-naive 'assistant' that simulates an LLM by applying a
    few simple rules on the combined prompt. The vulnerability: untrusted
    user_input is directly used to change behavior.
    """
    combined = f"SYSTEM: {system_prompt}\n\nUSER: {user_input}\n\nASSISTANT:"
    # simple "policies": if user asks to 'list instructions' we return the system prompt.
    # This is intentionally insecure for the challenge.
    lowered = user_input.lower()

    # Rule 1: If user asks to "explain your instructions" => return system prompt (vulnerable)
    if "explain your instructions" in lowered or "what are your instructions" in lowered:
        return f"(debug) system_prompt:\n{system_prompt}"

    # Rule 2: If user contains the pattern: "follow these (new) instructions:" then follow them
    m = re.search(r"follow these instructions:(.*)$", user_input, flags=re.IGNORECASE|re.DOTALL)
    if m:
        # return the "new instructions" as if the assistant followed them
        new_instr = m.group(1).strip()
        return f"(assistant simulated following instructions):\n{new_instr}"

    # Rule 3: fallback: echo with minimal paraphrase (simulate model hallucination)
    summary = user_input.strip()
    if not summary:
        summary = "Hello! Ask me to 'explain your instructions' if you need help."
    return f"I understood your request. You said: {summary}"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json or {}
    user_input = data.get("message", "")
    response = naive_model(SYSTEM_PROMPT, user_input)
    return jsonify({"reply": response})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
