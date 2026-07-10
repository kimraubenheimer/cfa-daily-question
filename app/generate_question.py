# import os
# import re
# import smtplib
# import html
# from datetime import date
# from email.message import EmailMessage
# import json



# import requests
# from bs4 import BeautifulSoup


# URL = "https://www.kaplanquizzes.com/cfa-level-2/"
# SITE_URL = "https://kimraubenheimer.github.io/cfa-daily-question/app"


# def scrape_kaplan():
#     page = requests.get(URL, timeout=20)
#     page.raise_for_status()

#     soup = BeautifulSoup(page.text, "html.parser")

#     # Options
#     form = soup.find("form", id="answer_form")
#     if form is None:
#         raise ValueError("Could not find answer form")

#     options = [
#         label.get_text(" ", strip=True)
#         for label in form.find_all("label")
#     ]

#     if len(options) != 3:
#         raise ValueError(f"Expected 3 options, found {len(options)}")

#     # Question
#     question_area = soup.find("div", class_="container insidecontainer")
#     if question_area is None:
#         raise ValueError("Could not find question container")

#     full_text = question_area.get_text("\n", strip=True)

#     start = full_text.find("Answers Today")
#     end = full_text.find(options[0])

#     if start == -1 or end == -1:
#         raise ValueError("Could not extract question text")

#     question_text = full_text[start + len("Answers Today"):end].strip()
#     question_text = " ".join(question_text.split())

#     # Answer explanation
#     answer_box = soup.find("div", id="answer")
#     print(f"Answer box: {answer_box.get_text()}")

#     if answer_box is None:
#         raise ValueError("Could not find answer box")

#     answer_p = answer_box.find("p")

#     if answer_p is None:
#         raise ValueError("Could not find answer paragraph")

#     full_answer_text = answer_p.get_text(strip=True)

#     print(f"Full answer text: {full_answer_text}")

#     match = re.match(
#         r"Correct Answer:\s*([ABC])\.\s*(.*)",
#         full_answer_text,
#         re.IGNORECASE | re.DOTALL
#     )

#     if match is None:
#         raise ValueError(
#             f"Could not extract correct answer from: {full_answer_text}"
#         )

#     correct_option = match.group(1).lower()
#     answer_text = match.group(2).strip()


#     return question_text, options, correct_option, answer_text



# def create_html(question_text, options, correct_option, answer_text):
#     today = date.today().isoformat()

#     option_a = html.escape(options[0])
#     option_b = html.escape(options[1])
#     option_c = html.escape(options[2])

#     question_text = html.escape(question_text)
#     answer_text = answer_text.replace("CORRECT", "").replace("INCORRECT", "").strip()
#     answer_js = json.dumps(answer_text)

#     page = f"""
# <!DOCTYPE html>
# <html lang="en">
# <head>
#     <meta charset="UTF-8">
#     <meta name="viewport" content="width=device-width, initial-scale=1.0">
#     <title>CFA Question {today}</title>
#     <link rel="preconnect" href="https://fonts.googleapis.com">
#     <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
#     <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
#     <style>
#         :root {{
#             --bg: #0f172a;
#             --card: #ffffff;
#             --ink: #0f172a;
#             --muted: #64748b;
#             --line: #e2e8f0;
#             --brand: #1e40af;
#             --brand-soft: #eff6ff;
#             --ok: #16a34a;
#             --ok-soft: #f0fdf4;
#             --bad: #dc2626;
#             --bad-soft: #fef2f2;
#         }}

#         * {{ box-sizing: border-box; }}

#         body {{
#             font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
#             background: linear-gradient(160deg, #0f172a 0%, #1e293b 100%);
#             color: var(--ink);
#             margin: 0;
#             min-height: 100vh;
#             display: flex;
#             align-items: flex-start;
#             justify-content: center;
#             padding: 48px 20px;
#         }}

#         .box {{
#             background: var(--card);
#             width: 100%;
#             max-width: 560px;
#             border-radius: 20px;
#             box-shadow: 0 20px 60px rgba(2, 6, 23, 0.45);
#             overflow: hidden;
#         }}

#         .header {{
#             padding: 28px 32px 20px;
#             border-bottom: 1px solid var(--line);
#         }}

#         .eyebrow {{
#             display: inline-flex;
#             align-items: center;
#             gap: 6px;
#             font-size: 12px;
#             font-weight: 600;
#             letter-spacing: 0.08em;
#             text-transform: uppercase;
#             color: var(--brand);
#             background: var(--brand-soft);
#             padding: 6px 12px;
#             border-radius: 999px;
#             margin: 0 0 16px;
#         }}

#         .question {{
#             font-size: 20px;
#             font-weight: 600;
#             line-height: 1.5;
#             margin: 0;
#             color: var(--ink);
#         }}

#         .options {{
#             padding: 24px 32px;
#             display: flex;
#             flex-direction: column;
#             gap: 12px;
#         }}

#         .option {{
#             display: flex;
#             align-items: center;
#             gap: 14px;
#             width: 100%;
#             text-align: left;
#             padding: 16px 18px;
#             border: 1.5px solid var(--line);
#             border-radius: 12px;
#             background: #fff;
#             cursor: pointer;
#             font-size: 15px;
#             font-weight: 500;
#             color: var(--ink);
#             transition: border-color .15s, background .15s, transform .1s, box-shadow .15s;
#         }}

#         .option:hover:not(:disabled) {{
#             border-color: var(--brand);
#             background: var(--brand-soft);
#         }}

#         .option:active:not(:disabled) {{ transform: scale(0.99); }}

#         .badge {{
#             flex-shrink: 0;
#             width: 28px;
#             height: 28px;
#             border-radius: 8px;
#             background: #f1f5f9;
#             color: var(--muted);
#             display: grid;
#             place-items: center;
#             font-weight: 700;
#             font-size: 13px;
#             transition: background .15s, color .15s;
#         }}

#         .option.correct {{
#             border-color: var(--ok);
#             background: var(--ok-soft);
#             color: var(--ok);
#         }}
#         .option.correct .badge {{ background: var(--ok); color: #fff; }}

#         .option.wrong {{
#             border-color: var(--bad);
#             background: var(--bad-soft);
#             color: var(--bad);
#         }}
#         .option.wrong .badge {{ background: var(--bad); color: #fff; }}

#         .option.dim {{ opacity: 0.5; }}
#         .option:disabled {{ cursor: default; }}

#         .explanation {{
#             margin: 0 32px 32px;
#             padding: 0 20px;
#             max-height: 0;
#             opacity: 0;
#             border-radius: 12px;
#             overflow: hidden;
#             transition: max-height .35s ease, opacity .3s ease, padding .35s ease;
#         }}

#         .explanation.show {{
#             max-height: 600px;
#             opacity: 1;
#             padding: 20px;
#         }}

#         .explanation.result-ok {{ background: var(--ok-soft); border: 1px solid #bbf7d0; }}
#         .explanation.result-bad {{ background: var(--bad-soft); border: 1px solid #fecaca; }}

#         .result-label {{
#             font-size: 14px;
#             font-weight: 700;
#             margin: 0 0 8px;
#             display: flex;
#             align-items: center;
#             gap: 8px;
#         }}
#         .result-ok .result-label {{ color: var(--ok); }}
#         .result-bad .result-label {{ color: var(--bad); }}

#         .explanation p {{
#             margin: 0;
#             font-size: 14.5px;
#             line-height: 1.65;
#             color: #334155;
#             white-space: pre-wrap;
#         }}
#     </style>
# </head>
# <body>

# <div class="box">
#     <div class="header">
#         <p class="eyebrow">Question of the Day &middot; {today}</p>
#         <h1 class="question">{question_text}</h1>
#     </div>

#     <div class="options" id="options">
#         <button class="option" data-choice="a" onclick="checkAnswer('a')">
#             <span class="badge">A</span><span>{option_a}</span>
#         </button>
#         <button class="option" data-choice="b" onclick="checkAnswer('b')">
#             <span class="badge">B</span><span>{option_b}</span>
#         </button>
#         <button class="option" data-choice="c" onclick="checkAnswer('c')">
#             <span class="badge">C</span><span>{option_c}</span>
#         </button>
#     </div>

#     <div class="explanation" id="explanation">
#         <p class="result-label" id="resultLabel"></p>
#         <p id="explanationText"></p>
#     </div>
# </div>

# <script>
#     const correctOption = "{correct_option}";
#     const answerText = {answer_js};
#     let answered = false;

# function checkAnswer(choice) {{
#     if (answered) return;
#     answered = true;

#     const buttons = document.querySelectorAll('.option');
#     buttons.forEach(btn => {{
#         const c = btn.dataset.choice;
#         btn.disabled = true;

#         if (c === correctOption) {{
#             btn.classList.add('correct');
#         }} else if (c === choice) {{
#             btn.classList.add('wrong');
#         }} else {{
#             btn.classList.add('dim');
#         }}
#     }});

#     const isCorrect = choice === correctOption;
#     const box = document.getElementById('explanation');
#     const label = document.getElementById('resultLabel');

#     box.classList.add('show');
#     box.classList.add(isCorrect ? 'result-ok' : 'result-bad');

#     label.textContent = 'Correct Answer: ' + correctOption.toUpperCase();
#     document.getElementById('explanationText').textContent = answerText;

#     box.scrollIntoView({{ behavior: 'smooth', block: 'nearest' }});
# }}
# </script>

# </body>
# </html>
# """

#     os.makedirs("app/questions", exist_ok=True)
#     filename = f"app/questions/{today}.html"

#     with open(filename, "w", encoding="utf-8") as f:
#         f.write(page)

#     return today, filename

# def send_email(today):
#     email_address = os.environ["EMAIL_ADDRESS"]
#     email_password = os.environ["EMAIL_PASSWORD"]
#     recipient = os.environ["RECIPIENT_EMAIL"]

#     link = f"{SITE_URL}/questions/{today}.html"

#     msg = EmailMessage()
#     msg["Subject"] = f"CFA Question of the Day - {today}"
#     msg["From"] = email_address
#     msg["To"] = recipient

#     msg.set_content(f"""
# Hi Grace,

# Today's CFA question is ready:

# {link}

# Click an answer to reveal the explanation.
# """)

#     with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
#         smtp.login(email_address, email_password)
#         smtp.send_message(msg)


# def main():
#     question_text, options, correct_option, answer_text = scrape_kaplan()
#     today, filename = create_html(question_text, options, correct_option, answer_text)
#     # send_email(today)

#     # print(f"Created {filename}")
#     # print("Email sent")


# if __name__ == "__main__":
#     main()

#########################################

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

    options = [
        label.get_text(" ", strip=True)
        for label in form.find_all("label")
    ]

    if len(options) != 3:
        raise ValueError(f"Expected 3 options, found {len(options)}")

    question_area = soup.select_one("div.container.insidecontainer")
    if question_area is None:
        raise ValueError("Could not find question container")

    full_text = question_area.get_text("\n", strip=True)
    start = full_text.find("Answers Today")
    end = full_text.find(options[0])

    if start == -1 or end == -1:
        raise ValueError("Could not extract question text")

    question_text = full_text[start + len("Answers Today"):end].strip()
    question_text = " ".join(question_text.split())

    answer_box = soup.find("div", id="answer")
    if answer_box is None:
        raise ValueError("Could not find answer box")

    answer_p = answer_box.find("p")
    if answer_p is None:
        raise ValueError("Could not find answer paragraph")

    answer_text = answer_p.get_text(" ", strip=True)

    # Remove an answer-letter prefix when Kaplan includes one.
    # The program does not use the letter or decide whether the user was correct.
    # answer_text = re.sub(
    #     r'^(?:Correct Answer:\s*[ABC]\.?\s*|'
    #     r'Choice\s*["“”\']?[ABC]["“”\']?\s+is\s+correct\.?\s*|'
    #     r'The correct answer is\s*["“”\']?[ABC]["“”\']?\.?\s*)',
    #     "",
    #     answer_text,
    #     flags=re.IGNORECASE,
    # ).strip()

    return question_text, options, answer_text


def create_html(question_text, options, answer_text):
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

        .option.selected {{
            border-color: var(--brand);
            background: var(--brand-soft);
            color: var(--brand);
        }}
        .option.selected .badge {{ background: var(--brand); color: #fff; }}

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

        .explanation.result-neutral {{
            background: #f8fafc;
            border: 1px solid var(--line);
        }}

        .result-label {{
            font-size: 14px;
            font-weight: 700;
            margin: 0 0 8px;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .result-neutral .result-label {{ color: var(--brand); }}

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
    const answerText = {answer_js};
    let answered = false;

function checkAnswer(choice) {{
    if (answered) return;
    answered = true;

    const buttons = document.querySelectorAll('.option');

    buttons.forEach(btn => {{
        btn.disabled = true;

        if (btn.dataset.choice === choice) {{
            btn.classList.add('selected');
        }} else {{
            btn.classList.add('dim');
        }}
    }});

    const box = document.getElementById('explanation');
    const label = document.getElementById('resultLabel');

    box.classList.add('show', 'result-neutral');

    label.textContent = 'You selected ' + choice.toUpperCase();
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
    question_text, options, answer_text = scrape_kaplan()
    today, filename = create_html(question_text, options, answer_text)
    send_email(today)

    # print(f"Created {filename}")
    # print("Email sent")


if __name__ == "__main__":
    main()