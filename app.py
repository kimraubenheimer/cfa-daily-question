from flask import Flask, render_template_string
import requests
from bs4 import BeautifulSoup
import re

app = Flask(__name__)

URL = "https://www.kaplanquizzes.com/cfa-level-2/"

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Question of the Day</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: #f4f4f4;
            display: flex;
            justify-content: center;
            padding-top: 80px;
        }

        .box {
            background: white;
            padding: 30px;
            width: 520px;
            border-radius: 12px;
            box-shadow: 0 4px 14px rgba(0,0,0,0.15);
            text-align: center;
        }

        .option {
            display: block;
            width: 100%;
            margin: 12px 0;
            padding: 14px;
            border: none;
            border-radius: 8px;
            background: #e8e8e8;
            cursor: pointer;
            font-size: 16px;
        }

        .option:hover {
            background: #d6d6d6;
        }
    </style>
</head>
<body>

<div class="box">
    <h1>Question of the Day</h1>
    <h2>{{ question.text }}</h2>

    {% for option in question.options %}
    <button class="option" onclick='checkAnswer({{ loop.index0 }})'>
        {% if loop.index0 == 0 %}
            A. {{ option }}
        {% elif loop.index0 == 1 %}
            B. {{ option }}
        {% else %}
            C. {{ option }}
        {% endif %}
    </button>
{% endfor %}
</div>

<script>
    const correctIndex = {{ question.correct_index }};
    const answerText = {{ question.answer_text | tojson }};

    function checkAnswer(selectedIndex) {
        if (selectedIndex === correctIndex) {
            alert("Correct!\\n\\n" + answerText);
        } else {
            alert("Incorrect.\\n\\n" + answerText);
        }
    }
</script>

</body>
</html>
"""


def scrape_question():
    html = requests.get(URL, timeout=20).text
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text("\n", strip=True)

    question_block = get_question_block(text)
    answer_block = get_answer_block(text)

    lines = [line.strip() for line in question_block.split("\n") if line.strip()]

    # Remove heading
    if lines[0] == "Answers Today":
        lines = lines[1:]

    question_text = lines[0]
    options = lines[1:4]

    correct_letter_match = re.search(r'Choice\s+"([abc])"\s+is correct', answer_block, re.I)

    if not correct_letter_match:
        raise ValueError("Could not find correct answer letter")

    correct_letter = correct_letter_match.group(1).lower()
    correct_index = {"a": 0, "b": 1, "c": 2}[correct_letter]

    return {
        "text": question_text,
        "options": options,
        "correct_index": correct_index,
        "answer_text": answer_block
    }


def get_question_block(text):
    start = text.find("Answers Today")
    end = text.find("CORRECT")

    if start == -1 or end == -1:
        raise ValueError("Could not find question block")

    return text[start:end].strip()


def get_answer_block(text):
    start = text.find("Choice ")
    end = text.find("WANT ANOTHER PRACTICE QUESTION?")

    if start == -1 or end == -1:
        raise ValueError("Could not find answer block")

    return text[start:end].strip()


@app.route("/")
def home():
    question = scrape_question()
    return render_template_string(HTML, question=question)


if __name__ == "__main__":
    app.run(debug=True)