from llmproxy import generate

import http.server
import socketserver
import urllib.parse
import requests
import json

PORT = 8000  # Runs on localhost:8000

GOOGLE_API_KEY = "AIzaSyDKNUeIRdGOIacjk--fNa2vcs00WHtqHIM"
SEARCH_ENGINE_ID = "945654d55c45d4da4"
# LLM_API_URL = "https://github.com/Tufts-University/LLMProxy"
LLM_API_KEY = "comp150-cdr-2025s-4srlRlceWnukwewcCw7vm7wLygCvdipGNEWgiRRs"

class MyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        """Handles GET requests (serves HTML and API responses)."""
        
        
        if "/search" in self.path:
            self.handle_search()
            return
        else:
            self.path = "index.html"  # Serve the HTML page
            return http.server.SimpleHTTPRequestHandler.do_GET(self)

    def handle_search(self):
        """Handles professor search requests"""
        query_params = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        professor_name = query_params.get("professor", [""])[0]
        
        google_search_url = f"https://www.googleapis.com/customsearch/v1?q={professor_name}+Tufts&key={GOOGLE_API_KEY}&cx={SEARCH_ENGINE_ID}"
        google_response = requests.get(google_search_url)

        if google_response.status_code != 200:
            self.send_response(500)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Google search failed"}).encode())
            return

        google_data = google_response.json()
        search_results = google_data.get("items", [])

        if not search_results:
            self.send_response(404)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "No Google search results found"}).encode())
            return
        
        # Create a query for the LLM to process
        top_result_snippet = search_results[0].get("snippet", "")
        query = f"Summarize this review: {top_result_snippet}"


        response = generate(
            model='4o-mini',
            system="Summarize the professor's review.",
            query=query,
            temperature=0.7,
            lastk=5,
            session_id='ProfessorRatingsSession'
            )

        # Extract star ratings if available
        star_ratings = None
        for item in search_results:
            if "rating" in item:
                star_ratings = item["rating"]
                break

        # Prepare the response with LLM data
        professor_data = {
            "title": f"Professor {professor_name} Ratings",
            "link": f"https://www.tufts.edu/faculty/{professor_name.replace(' ', '_')}",
            "star_ratings": star_ratings,
            "snippet": response
        }
        
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(professor_data).encode())
            
# Run the server
with socketserver.TCPServer(("", PORT), MyHandler) as httpd:
    print(f"Serving at http://127.0.0.1:{PORT}")
    httpd.serve_forever()
