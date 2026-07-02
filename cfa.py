import requests
from bs4 import BeautifulSoup
import smtplib
from email.message import EmailMessage
import os

EMAIL = os.environ["GMAIL_USER"]
PASSWORD = os.environ["GMAIL_APP_PASSWORD"]
URL = "https://www.kaplanquizzes.com/cfa-level-2/"

def get_question(text):
    # html = requests.get(URL, timeout=20).text
    # soup = BeautifulSoup(html, "html.parser")
    # text = soup.get_text("\n", strip=True)

    # Simple extraction based on current page structure
    start = text.find("CFA Level II Practice Question")
    end = text.find("CORRECT")

    if start == -1 or end == -1:
        raise ValueError("Could not find question block")

    print("Extracted question text:", text[start:end].strip())
    return text[start:end].strip()

def get_answer(text):
    # html = requests.get(URL, timeout=20).text
    # soup = BeautifulSoup(html, "html.parser")
    # text = soup.get_text("\n", strip=True)

    # Simple extraction based on current page structure
    start = text.find("Choice ")
    end = text.find("WANT ANOTHER PRACTICE QUESTION?")

    if start == -1 or end == -1:
        raise ValueError("Could not find answer block")

    answer = text[start:end].strip()
    print("Extracted answer text:", answer)
    return answer

def send_email(body, q_or_a):
    msg = EmailMessage()
    if q_or_a == "question":
        msg["Subject"] = "Daily CFA Level II Question"
    elif q_or_a == "answer":
        msg["Subject"] = "Daily CFA Level II Answer"

    msg["From"] = "kimraubs@gmail.com"
    msg["To"] = "graceraubenheimer@gmail.com"
    msg.set_content(body)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        # smtp.login("kimraubs@gmail.com", "APP_KEY")
        smtp.login(EMAIL, PASSWORD)
        smtp.send_message(msg)

if __name__ == "__main__":
    html = requests.get(URL, timeout=20).text
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text("\n", strip=True)

    question = get_question(text)
    answer = get_answer(text)

    send_email(question, "question")
    send_email(answer, "answer")