import requests
from flask import Flask, request, jsonify
from llmproxy import generate

app = Flask(__name__)

GOOGLE_API_KEY = "AIzaSyDKNUeIRdGOIacjk--fNa2vcs00WHtqHIM"
SEARCH_ENGINE_ID = "945654d55c45d4da4"

########################
# Orchestrator Agent
########################
class OrchestratorAgent:
    def __init__(self):
        # Dictionary to hold session data for each user
        # Key: user_id (or user_name)
        # Value: { "history": [...], "has_introduced": bool, etc. }
        self.user_sessions = {}

    def handle_query(self, user_id, message):
        """
        Main entry point for orchestrating the chatbot’s behavior.
        Determines if the user is new, whether to ask follow-up questions,
        whether to do a Google search, and calls the LLM to generate a response.
        """
        # 1. Initialize session if not present
        if user_id not in self.user_sessions:
            self.user_sessions[user_id] = {
                "history": [],
                "has_introduced": False,
                "pending_followup": False,
            }

        session = self.user_sessions[user_id]

        # 2. Check if user is new to provide an introduction
        if not session["has_introduced"]:
            if msg_lower in ["hi", "hello", "hey", "hola"]:
                session["has_introduced"] = True
                # Save user’s message to history
                session["history"].append({"role": "user", "content": message})

                introduction = (
                    "Hello! I’m your financial assistant bot. "
                    "I can help summarize information, answer queries, and fetch live data. "
                    "How can I help you today?"
                )
                session["history"].append({"role": "assistant", "content": introduction})
                return introduction
            else:
                # If user is new but didn't explicitly say "hi", still introduce
                session["has_introduced"] = True
                session["history"].append({"role": "user", "content": message})

                introduction = (
                    "Hello! I’m your financial assistant bot. "
                    "I can help summarize information, answer queries, and fetch live data. "
                    "How can I help you today?"
                )
                session["history"].append({"role": "assistant", "content": introduction})
                return introduction

        # 3. Optionally ask follow-up questions if the last response indicated we needed more info
        if session["pending_followup"]:
            # This is placeholder logic to demonstrate how you might handle a follow-up
            # In a real scenario, you'd store what the follow-up question was about
            # and verify the new user input is sufficient to proceed.
            followup_response = self._call_llm(user_id, message, do_search=True)
            session["pending_followup"] = False
            return followup_response

        # 4. Otherwise, handle the normal query flow
        #    Decide if you want to do a Google search based on user input or system logic
        do_search = self._should_do_google_search(message)

        if do_search:
            search_results = self._google_search(message)
            # Summarize or pass the search results to LLM
            llm_response = self._call_llm(user_id, search_results, do_search=True)
        else:
            # If no search, just pass the user query directly to the LLM
            llm_response = self._call_llm(user_id, message, do_search=False)

        return llm_response

    def _call_llm(self, user_id, content, do_search=True):
        """
        Calls your LLM (via llmproxy.generate) with appropriate prompts.
        You can customize the system prompt or chain-of-thought logic here.
        """
        system_prompt = "Summarize the following information and answer the query:"
        if not do_search:
            system_prompt = (
                "You are a financial advice chatbot. "
                "Answer the user query to the best of your knowledge."
            )

        response = generate(
            model='4o-mini',
            system=system_prompt,
            query=content,
            temperature=0.0,
            lastk=0,
            session_id='GenericSession'  # You could also use user_id here if your LLM proxy supports it
        )
        response_text = response['response']

        # Update conversation history
        self.user_sessions[user_id]["history"].append({"role": "assistant", "content": response_text})
        return response_text

    def _should_do_google_search(self, message):
        """
        Decide if we want to perform a Google search. Here, we do a trivial check:
        if the message contains the word 'stock' or 'market', assume we need more data.
        """
        triggers = ["stock", "market", "finance", "price"]
        msg_lower = message.lower()
        return any(trig in msg_lower for trig in triggers)

    def _google_search(self, query):
        """
        Simple Google Search call. Returns a string containing combined snippets.
        """
        url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={GOOGLE_API_KEY}&cx={SEARCH_ENGINE_ID}"
        response = requests.get(url)

        if response.status_code == 200:
            results = response.json().get("items", [])
            summaries = [item["snippet"] for item in results[:5]]
            return " ".join(summaries)
        return "No relevant results found."


########################
# Flask App
########################
@app.route('/')
def hello_world():
    return jsonify({"text": "Hello from Koyeb - you reached the main page!"})

@app.errorhandler(404)
def page_not_found(e):
    return "Not Found", 404

# Instantiate the orchestrator agent
orchestrator = OrchestratorAgent()

@app.route('/query', methods=['POST'])
def main():
    data = request.get_json()

    # Extract relevant info
    user = data.get("user_name", "Unknown")
    message = data.get("text", "")

    print(f"Incoming data: {data}")

    # Ignore empty or bot messages
    if data.get("bot") or not message:
        return jsonify({"status": "ignored"})

    print(f"Message from {user} : {message}")

    # Use the orchestrator to handle the user's query
    response_text = orchestrator.handle_query(user, message)

    print(f"Response to {user} : {response_text}")
    return jsonify({"text": response_text})

if __name__ == "__main__":
    app.run(debug=True)
