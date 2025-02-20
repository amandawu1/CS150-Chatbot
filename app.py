# from llmproxy import generate
# import http.server
# import socketserver
# import urllib.parse
# import requests
# import json
# import yfinance as yf

# # PORT = 8000  # Runs on localhost:8000

# GOOGLE_API_KEY = "AIzaSyDKNUeIRdGOIacjk--fNa2vcs00WHtqHIM"
# SEARCH_ENGINE_ID = "945654d55c45d4da4" 
# LLM_API_KEY = "comp150-cdr-2025s-4srlRlceWnukwewcCw7vm7wLygCvdipGNEWgiRRs"

# class MyHandler(http.server.SimpleHTTPRequestHandler):
#     def do_GET(self):
#         """Handles GET requests (serves HTML and API responses)."""
        
#         if "/search" in self.path:
#             self.handle_query()
#             return
#         else:
#             self.path = "index.html"  
#             return http.server.SimpleHTTPRequestHandler.do_GET(self)

#     def handle_query(self):
#         """Handles stock market queries to fetch news, prices, and recommendations."""
#         query_params = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
#         query = query_params.get("stock", [""])[0]
        
#         # parsed_url = urllib.parse.urlparse(self.path)
#         # query_string = parsed_url.query
#         # full_query = query_string
        
#         # print(f"Full query string: {full_query}")
#         print(f"Stock query parameter: {query}")

#         # Step 1: Use RAG-based LLM to determine intent
#         classification_prompt = f"Is the following query asking for a stock recommendation? Answer 'yes' or 'no': \n{query}"
#         try:
#             classification_response = generate(
#                 model='4o-mini',
#                 system="Classify the query as asking for a stock recommendation or not.",
#                 query=classification_prompt,
#                 temperature=0.3,
#                 lastk=0,
#                 session_id='StockQueryClassificationSession',
#                 rag_usage=True,
#                 rag_threshold=0.2,
#                 rag_k=4)
#         except Exception as e:
#             self.send_error(500, "Failed to classify query")
#             print(f"Failed to classify query: {e}")
#             return
        
#         classification_text = classification_response.get('response', '')
#         classification_text = str(classification_text)
#         # print(f"\nClassification response: {classification_text}\n")
#         # classification_text = str(classification_response.get)
#         # print (classification_text)
#         is_stock_recommendation = classification_text.strip().lower() == "yes"
#         # print(f"Query: {query}, Is stock recommendation: {is_stock_recommendation}")
        
#         # Step 2: Fetch live information using Google Search API
#         search_query = query if not is_stock_recommendation else "stock recommendation"
#         google_search_url = f"https://www.googleapis.com/customsearch/v1?q={urllib.parse.quote(search_query)}&key={GOOGLE_API_KEY}&cx={SEARCH_ENGINE_ID}"
#         google_response = requests.get(google_search_url)

#         if google_response.status_code != 200:
#             self.send_error(500, "Google search failed")
#             print(f"Google search failed with status code: {google_response.status_code}")
#             return

#         google_data = google_response.json()
#         search_results = google_data.get("items", [])
        
#         if not search_results:
#             self.send_error(404, "No relevant information found")
#             print("No relevant information found")
#             return

#         # news_snippets = [item["snippet"] for item in search_results[:3]]
#         # news_text = "\n".join(news_snippets)

#         # Step 3: Generate response using RAG-based LLM
#         # llm_prompt = f"{query}\n\nRelevant information:\n{news_text}" if not is_stock_recommendation else \
#         #               f"Based on the following information, give 3 top stock recommendations with justification and provide sources. Please give options for low, medium, and high risk investments?\n{news_text}"
#         top_result_snippet = search_results[0].get("snippet", "")
#         query = f"Summarize this review: {top_result_snippet}"
        
#         # try:
#         response = generate(
#             model='4o-mini',
#             system="Provide an accurate response based on live information.",
#             query=query,
#             temperature=0.7,
#             lastk=0,
#             session_id='StockAnalysisSession',
#             rag_usage=True,
#             rag_threshold=0.2,
#             rag_k=4
#             )
            
#         # except Exception as e:
#         #     self.send_error(500, "Failed to generate LLM response")
#         #     print(f"Failed to generate LLM response: {e}")
#         #     return

#         # Step 4: Return JSON response
#         response_data = {
#             "query": query,
#             # "is_stock_recommendation": is_stock_recommendation,
#             "response": response
#         }
        
#         self.send_response(200)
#         self.send_header("Content-type", "application/json")
#         self.end_headers()
#         self.wfile.write(json.dumps(response_data).encode())

# # Run the server
# with socketserver.TCPServer(("", PORT), MyHandler) as httpd:
#     print(f"Serving at http://127.0.0.1:{PORT}")
#     httpd.serve_forever()





import requests
from flask import Flask, request, jsonify
from llmproxy import generate

app = Flask(__name__)

@app.route('/')
def hello_world():
   return jsonify({"text":'Hello from Koyeb - you reached the main page!'})

@app.route('/query', methods=['POST'])
def main():
    data = request.get_json() 

    # Extract relevant information
    user = data.get("user_name", "Unknown")
    message = data.get("text", "")

    print(data)

    # Ignore bot messages
    if data.get("bot") or not message:
        return jsonify({"status": "ignored"})

    print(f"Message from {user} : {message}")

    # Generate a response using LLMProxy
    response = generate(
        model='4o-mini',
        system="answer the question",
        query= message,
        temperature=0.0,
        lastk=0,
        session_id='GenericSession'
    )

    response_text = response['response']
    
    # Send response back
    print(response_text)

    return jsonify({"text": response_text})
    
@app.errorhandler(404)
def page_not_found(e):
    return "Not Found", 404

if __name__ == "__main__":
    app.run()