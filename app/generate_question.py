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

# def create_html(question_text, options, correct_option, answer_text):
#     today = date.today().isoformat()

#     answer_js = json.dumps(answer_text)

#     option_a = html.escape(options[0])
#     option_b = html.escape(options[1])
#     option_c = html.escape(options[2])

#     question_text = html.escape(question_text)
#     # answer_text = html.escape(answer_text).replace("\n", "\\n")
#     answer_text = answer_text.replace("CORRECT", "").replace("INCORRECT", "").strip()
#     answer_js = json.dumps(answer_text)

#     page = f"""
# <!DOCTYPE html>
# <html>
# <head>
#     <title>CFA Question {today}</title>
#     <style>
#         body {{
#             font-family: Arial, sans-serif;
#             background: #f4f4f4;
#             display: flex;
#             justify-content: center;
#             padding-top: 80px;
#         }}

#         .box {{
#             background: white;
#             padding: 30px;
#             width: 520px;
#             border-radius: 12px;
#             box-shadow: 0 4px 14px rgba(0,0,0,0.15);
#             text-align: center;
#         }}

#         button {{
#             display: block;
#             width: 100%;
#             margin: 12px 0;
#             padding: 14px;
#             border: none;
#             border-radius: 8px;
#             background: #e8e8e8;
#             cursor: pointer;
#             font-size: 16px;
#         }}

#         button:hover {{
#             background: #d6d6d6;
#         }}
#     </style>
# </head>
# <body>

# <div class="box">
#     <h1>Question of the Day</h1>
#     <h2>{question_text}</h2>

#     <button onclick="checkAnswer('a')">A. {option_a}</button>
#     <button onclick="checkAnswer('b')">B. {option_b}</button>
#     <button onclick="checkAnswer('c')">C. {option_c}</button>
# </div>

# <script>
#     function checkAnswer(choice) {{
#         const correctOption = "{correct_option}";
#         const answerText = {answer_js};

#         if (choice === correctOption) {{
#             alert("Correct!\\n\\n" + answerText);
#         }} else {{
#             alert("Incorrect.\\n\\n" + answerText);
#         }}
#     }}
# </script>

# </body>
# </html>
# """

#     # os.makedirs("questions", exist_ok=True)
#     # os.makedirs("../questions", exist_ok=True)

#     # filename = f"questions/{today}.html"
#     os.makedirs("app/questions", exist_ok=True)

#     filename = f"app/questions/{today}.html"

#     with open(filename, "w", encoding="utf-8") as f:
#         f.write(page)

#     return today, filename

def create_html(question_text, options, correct_option, answer_text):
    today = date.today().isoformat()

    option_a = html.escape(options[0])
    option_b = html.escape(options[1])
    option_c = html.escape(options[2])

    question_text = html.escape(question_text)
    answer_text = answer_text.replace("CORRECT", "").replace("INCORRECT", "").strip()
    answer_js = json.dumps(answer_text)

    page = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CFA Question {today}</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg: #0f172a;
            --card: #ffffff;
            --ink: #0f172a;
            --muted: #64748b;
            --line: #e2e8f0;
            --brand: #1e40af;
            --brand-soft: #eff6ff;
            --ok: #16a34a;
            --ok-soft: #f0fdf4;
            --bad: #dc2626;
            --bad-soft: #fef2f2;
        }}

        * {{ box-sizing: border-box; }}

        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: linear-gradient(160deg, #0f172a 0%, #1e293b 100%);
            color: var(--ink);
            margin: 0;
            min-height: 100vh;
            display: flex;
            align-items: flex-start;
            justify-content: center;
            padding: 48px 20px;
        }}

        .box {{
            background: var(--card);
            width: 100%;
            max-width: 560px;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(2, 6, 23, 0.45);
            overflow: hidden;
        }}

        .header {{
            padding: 28px 32px 20px;
            border-bottom: 1px solid var(--line);
        }}

        .eyebrow {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            font-size: 12px;
            font-weight: 600;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            color: var(--brand);
            background: var(--brand-soft);
            padding: 6px 12px;
            border-radius: 999px;
            margin: 0 0 16px;
        }}

        .question {{
            font-size: 20px;
            font-weight: 600;
            line-height: 1.5;
            margin: 0;
            color: var(--ink);
        }}

        .options {{
            padding: 24px 32px;
            display: flex;
            flex-direction: column;
            gap: 12px;
        }}

        .option {{
            display: flex;
            align-items: center;
            gap: 14px;
            width: 100%;
            text-align: left;
            padding: 16px 18px;
            border: 1.5px solid var(--line);
            border-radius: 12px;
            background: #fff;
            cursor: pointer;
            font-size: 15px;
            font-weight: 500;
            color: var(--ink);
            transition: border-color .15s, background .15s, transform .1s, box-shadow .15s;
        }}

        .option:hover:not(:disabled) {{
            border-color: var(--brand);
            background: var(--brand-soft);
        }}

        .option:active:not(:disabled) {{ transform: scale(0.99); }}

        .badge {{
            flex-shrink: 0;
            width: 28px;
            height: 28px;
            border-radius: 8px;
            background: #f1f5f9;
            color: var(--muted);
            display: grid;
            place-items: center;
            font-weight: 700;
            font-size: 13px;
            transition: background .15s, color .15s;
        }}

        .option.correct {{
            border-color: var(--ok);
            background: var(--ok-soft);
            color: var(--ok);
        }}
        .option.correct .badge {{ background: var(--ok); color: #fff; }}

        .option.wrong {{
            border-color: var(--bad);
            background: var(--bad-soft);
            color: var(--bad);
        }}
        .option.wrong .badge {{ background: var(--bad); color: #fff; }}

        .option.dim {{ opacity: 0.5; }}
        .option:disabled {{ cursor: default; }}

        .explanation {{
            margin: 0 32px 32px;
            padding: 0 20px;
            max-height: 0;
            opacity: 0;
            border-radius: 12px;
            overflow: hidden;
            transition: max-height .35s ease, opacity .3s ease, padding .35s ease;
        }}

        .explanation.show {{
            max-height: 600px;
            opacity: 1;
            padding: 20px;
        }}

        .explanation.result-ok {{ background: var(--ok-soft); border: 1px solid #bbf7d0; }}
        .explanation.result-bad {{ background: var(--bad-soft); border: 1px solid #fecaca; }}

        .result-label {{
            font-size: 14px;
            font-weight: 700;
            margin: 0 0 8px;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .result-ok .result-label {{ color: var(--ok); }}
        .result-bad .result-label {{ color: var(--bad); }}

        .explanation p {{
            margin: 0;
            font-size: 14.5px;
            line-height: 1.65;
            color: #334155;
            white-space: pre-wrap;
        }}
    </style>
</head>
<body>

<div class="box">
    <div class="header">
        <p class="eyebrow">Question of the Day &middot; {today}</p>
        <h1 class="question">{question_text}</h1>
    </div>

    <div class="options" id="options">
        <button class="option" data-choice="a" onclick="checkAnswer('a')">
            <span class="badge">A</span><span>{option_a}</span>
        </button>
        <button class="option" data-choice="b" onclick="checkAnswer('b')">
            <span class="badge">B</span><span>{option_b}</span>
        </button>
        <button class="option" data-choice="c" onclick="checkAnswer('c')">
            <span class="badge">C</span><span>{option_c}</span>
        </button>
    </div>

    <div class="explanation" id="explanation">
        <p class="result-label" id="resultLabel"></p>
        <p id="explanationText"></p>
    </div>
</div>

<script>
    const correctOption = "{correct_option}";
    const answerText = {answer_js};
    let answered = false;

function checkAnswer(choice) {{
    if (answered) return;
    answered = true;

    const buttons = document.querySelectorAll('.option');
    buttons.forEach(btn => {{
        const c = btn.dataset.choice;
        btn.disabled = true;

        if (c === correctOption) {{
            btn.classList.add('correct');
        }} else if (c === choice) {{
            btn.classList.add('wrong');
        }} else {{
            btn.classList.add('dim');
        }}
    }});

    const isCorrect = choice === correctOption;
    const box = document.getElementById('explanation');
    const label = document.getElementById('resultLabel');

    box.classList.add('show');
    box.classList.add(isCorrect ? 'result-ok' : 'result-bad');

    label.textContent = 'Correct Answer: ' + correctOption.toUpperCase();
    document.getElementById('explanationText').textContent = answerText;

    box.scrollIntoView({{ behavior: 'smooth', block: 'nearest' }});
}}
</script>

</body>
</html>
"""

    os.makedirs("app/questions", exist_ok=True)
    filename = f"app/questions/{today}.html"

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

    # print(f"Created {filename}")
    # print("Email sent")


if __name__ == "__main__":
    main()