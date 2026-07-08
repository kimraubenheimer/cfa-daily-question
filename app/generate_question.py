import os
import re
import smtplib
import html
from datetime import date
from email.message import EmailMessage
import json



import requests
from bs4 import BeautifulSoup


URL = "https://www.kaplanquizzes.com/cfa-level-2/"
SITE_URL = "https://kimraubenheimer.github.io/cfa-daily-question/app"


def scrape_kaplan():
    page = requests.get(URL, timeout=20)
    page.raise_for_status()

    soup = BeautifulSoup(page.text, "html.parser")

    form = soup.find("form", id="answer_form")

    if form is None:
        raise ValueError("Could not find answer form")

    # Get the options
    options = []

    for radio in form.find_all("input", {"name": "optionsRadios"}):
        label = radio.find_parent("label")
        option_text = label.get_text(" ", strip=True)
        options.append(option_text)

    if len(options) != 3:
        raise ValueError(f"Expected 3 options, found {len(options)}")

    # Get the question
    question_area = soup.find("div", id="questionspot")

    if question_area is None:
        raise ValueError("Could not find question area")

    full_text = question_area.get_text("\n", strip=True)

    first_option = options[0]
    start = full_text.find("Answers Today")
    end = full_text.find(first_option)

    if start == -1 or end == -1:
        raise ValueError("Could not extract question text")

    question_text = full_text[start:end]
    question_text = question_text.replace("Answers Today", "").strip()

    # Remove title line if present
    lines = [line.strip() for line in question_text.split("\n") if line.strip()]

    if lines and lines[0].startswith("CFA Level II Practice Question"):
        lines = lines[1:]

    question_text = " ".join(lines).strip()

    # Get the hidden answer block
    answer_container = soup.find("div", id="answer")

    if answer_container is None:
        raise ValueError("Could not find answer container")

    answer_div = answer_container.find("div", style=lambda s: s and "padding:30px" in s)

    if answer_div is None:
        raise ValueError("Could not find answer text div")

    answer_text = answer_div.get_text(" ", strip=True)
    # Clean out CORRECT / INCORRECT labels
    answer_text = answer_text.replace("CORRECT", "").replace("INCORRECT", "").strip()

    # Get correct answer letter
    match = re.search(r"Correct Answer:\s*([ABC])", answer_text, re.I)

    if not match:
        raise ValueError("Could not find correct answer letter")

    correct_option = match.group(1).lower()

    return question_text, options, correct_option, answer_text

def create_html(question_text, options, correct_option, answer_text):
    today = date.today().isoformat()

    answer_js = json.dumps(answer_text)

    option_a = html.escape(options[0])
    option_b = html.escape(options[1])
    option_c = html.escape(options[2])

    question_text = html.escape(question_text)
    # answer_text = html.escape(answer_text).replace("\n", "\\n")
    answer_text = answer_text.replace("CORRECT", "").replace("INCORRECT", "").strip()
    answer_js = json.dumps(answer_text)

    page = f"""
<!DOCTYPE html>
<html>
<head>
    <title>CFA Question {today}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            background: #f4f4f4;
            display: flex;
            justify-content: center;
            padding-top: 80px;
        }}

        .box {{
            background: white;
            padding: 30px;
            width: 520px;
            border-radius: 12px;
            box-shadow: 0 4px 14px rgba(0,0,0,0.15);
            text-align: center;
        }}

        button {{
            display: block;
            width: 100%;
            margin: 12px 0;
            padding: 14px;
            border: none;
            border-radius: 8px;
            background: #e8e8e8;
            cursor: pointer;
            font-size: 16px;
        }}

        button:hover {{
            background: #d6d6d6;
        }}
    </style>
</head>
<body>

<div class="box">
    <h1>Question of the Day</h1>
    <h2>{question_text}</h2>

    <button onclick="checkAnswer('a')">A. {option_a}</button>
    <button onclick="checkAnswer('b')">B. {option_b}</button>
    <button onclick="checkAnswer('c')">C. {option_c}</button>
</div>

<script>
    function checkAnswer(choice) {{
        const correctOption = "{correct_option}";
        const answerText = {answer_js};

        if (choice === correctOption) {{
            alert("Correct!\\n\\n" + answerText);
        }} else {{
            alert("Incorrect.\\n\\n" + answerText);
        }}
    }}
</script>

</body>
</html>
"""

    # os.makedirs("questions", exist_ok=True)
    os.makedirs("../questions", exist_ok=True)

    filename = f"questions/{today}.html"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(page)

    return today, filename


def send_email(today):
    email_address = os.environ["EMAIL_ADDRESS"]
    email_password = os.environ["EMAIL_PASSWORD"]
    recipient = os.environ["RECIPIENT_EMAIL"]

    link = f"{SITE_URL}/questions/{today}.html"

    msg = EmailMessage()
    msg["Subject"] = f"CFA Question of the Day - {today}"
    msg["From"] = email_address
    msg["To"] = recipient

    msg.set_content(f"""
Hi Grace,

Today's CFA question is ready:

{link}

Click an answer to reveal the explanation.
""")

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(email_address, email_password)
        smtp.send_message(msg)


def main():
    question_text, options, correct_option, answer_text = scrape_kaplan()
    today, filename = create_html(question_text, options, correct_option, answer_text)
    send_email(today)

    print(f"Created {filename}")
    print("Email sent")


if __name__ == "__main__":
    main()