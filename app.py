from flask import Flask, request, render_template_string
from recommend import recommend

app = Flask(__name__)

HTML_TEMPLATE = """
<!doctype html>
<title>Book Recommendations</title>
<h1>Top Book Recommendations</h1>
<form action="" method="get">
  <label for="num">Number of recommendations:</label>
  <input type="number" id="num" name="num" value="{{ num }}" min="1" max="20">
  <input type="submit" value="Get Recommendations">
</form>
<ul>
{% for b in books %}
  <li>{{ loop.index }}. {{ b.title }} ({{ b.author }}) - Rank {{ b.rank }} | {{ b.discount }}折 {{ b.price }}元</li>
{% endfor %}
</ul>
"""

@app.route("/")
def index():
    num = request.args.get("num", default=5, type=int)
    books = recommend(num)
    return render_template_string(HTML_TEMPLATE, books=books, num=num)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
