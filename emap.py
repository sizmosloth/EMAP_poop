import imaplib
import email
from email.header import decode_header
import re
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score
import joblib

# ---------- LOGIN ----------
USERNAME = "67jackiechan@gmail.com"
PASSWORD = "lobzjenfjohjcnqe"  # App password only!

# ---------- CLEAN TEXT ----------
def clean_text(text):
    text = re.sub(r"<.*?>", "", str(text))
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip().lower()

# ---------- CONNECT ----------
print("🔗 Connecting to Gmail...")
mail = imaplib.IMAP4_SSL("imap.gmail.com")
mail.login(USERNAME, PASSWORD)
mail.select("inbox")
print("📨 Fetching last 20 emails from inbox...")

# Fetch last 20 emails (read + unread)
status, messages = mail.search(None, "ALL")
email_ids = messages[0].split()[-20:]

emails = []
for idx, num in enumerate(email_ids, 1):
    print(f"📥 Fetching email {idx}/{len(email_ids)}...")
    status, data = mail.fetch(num, '(RFC822)')
    msg = email.message_from_bytes(data[0][1])

    # subject
    subject, encoding = decode_header(msg.get("Subject", ""))[0]
    if isinstance(subject, bytes):
        subject = subject.decode(encoding or "utf-8", errors="ignore")

    # date
    date = msg.get("Date", "Unknown date")

    # body
    content = ""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                try:
                    content += part.get_payload(decode=True).decode(errors="ignore")
                except:
                    pass
    else:
        try:
            content = msg.get_payload(decode=True).decode(errors="ignore")
        except:
            pass

    emails.append({
        "subject": clean_text(subject),
        "content": clean_text(content)[:500],
        "date": date
    })

mail.logout()
print(f"✅ Fetched {len(emails)} emails.\n")

if not emails:
    print("📭 No emails found.")
    exit()

# ---------- ENHANCED DATASET ----------
spam_samples = [
    "win a free iphone now", "you have won 10 lakh rupees lottery",
    "claim your reward", "urgent payment required", "limited offer get 90% off",
    "click the link to verify your account", "you are selected as a lucky winner",
    "free trial click here", "unsubscribe to stop receiving", "get rich quick deal",
    "investment opportunity earn money fast", "congratulations claim your bonus",
    "lottery winner announcement", "free bonus just for you",
    "buy now offer expires soon", "double your income fast", "loan approved instantly",
    "earn money from home", "free recharge offer", "make money online easily",
    "get your prize now", "special discount available", "urgent attention needed",
    "you have a parcel waiting", "click to activate reward",
    "get a free amazon gift card", "unbelievable deal for you"
]

primary_samples = [
    "your otp for login is 4321", "security alert for your account",
    "your amazon order has been shipped", "meeting scheduled at 4 pm",
    "payment received successfully", "invoice for your recent purchase",
    "update your password immediately", "project update from your teacher",
    "hello how are you", "family function invitation",
    "school assignment for tomorrow", "thank you for your message",
    "your subscription has been renewed", "login attempt detected",
    "password changed successfully", "sign in verification code",
    "bank transaction alert", "flight ticket booking confirmed",
    "your zomato order is out for delivery", "google verification code",
    "class timetable update", "college result declared",
    "friend shared a photo with you", "teacher shared notes",
    "your recharge is successful", "new message from support team",
    "github login detected", "microsoft account password reset",
    "meeting link from zoom", "otp for payment verification"
]

df = pd.DataFrame({
    "text": spam_samples + primary_samples,
    "label": ["spam"] * len(spam_samples) + ["primary"] * len(primary_samples)
})

# ---------- TRAIN MODEL ----------
X_train, X_test, y_train, y_test = train_test_split(df["text"], df["label"], test_size=0.25, random_state=42)
vectorizer = CountVectorizer()
X_train_vec = vectorizer.fit_transform(X_train)
model = MultinomialNB()
model.fit(X_train_vec, y_train)
X_test_vec = vectorizer.transform(X_test)
acc = accuracy_score(y_test, model.predict(X_test_vec))
print(f"🎯 Model trained successfully — Accuracy: {acc*100:.2f}%\n")

# ---------- KEYWORDS ----------
spam_keywords = [
    "win", "free", "offer", "buy", "discount", "deal", "click", "lottery",
    "cashback", "urgent", "reward", "bonus", "money", "unsubscribe", "investment"
]
primary_keywords = [
    "otp", "login", "security", "password", "account", "invoice", "order", "payment",
    "project", "meeting", "alert", "bank", "hello", "thank", "update", "verification",
    "teacher", "school", "result"
]

# ---------- CLASSIFICATION ----------
spam_file = open("spam_emails.txt", "w", encoding="utf-8")
primary_file = open("primary_emails.txt", "w", encoding="utf-8")

spam_count = 0
primary_count = 0

print("--- 📬 Gmail Email Classification Results ---\n")

for i, e in enumerate(emails, 1):
    text = f"{e['subject']} {e['content']}"
    text_lower = text.lower()
    label = None

    # Keyword logic first
    if any(word in text_lower for word in spam_keywords):
        label = "spam"
    elif any(word in text_lower for word in primary_keywords):
        label = "primary"
    else:
        # ML fallback
        new_vec = vectorizer.transform([text_lower])
        label = model.predict(new_vec)[0]

    # Print formatted result
    print(f"📧 Email {i} → [{label.upper()}]")
    print(f"Subject: {e['subject']}")
    print(f"Date: {e['date']}")
    print(f"Content Preview: {e['content'][:120]}...\n{'-'*60}")

    entry = (
        f"Email {i}: [{label.upper()}]\n"
        f"Subject: {e['subject']}\n"
        f"Date: {e['date']}\n"
        f"Content: {e['content']}\n\n"
    )

    if label == "spam":
        spam_file.write(entry)
        spam_count += 1
    else:
        primary_file.write(entry)
        primary_count += 1

spam_file.close()
primary_file.close()
joblib.dump((model, vectorizer), "spam_model.pkl")

print(f"\n📊 Summary:")
print(f"   Spam Emails: {spam_count}")
print(f"   Primary Emails: {primary_count}")
print("\n💾 Saved categorized emails into:")
print("   → spam_emails.txt")
print("   → primary_emails.txt")
print("✅ Model and vectorizer saved successfully.")
