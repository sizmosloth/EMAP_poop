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
print("📨 Fetching last 100 emails from inbox...")

# Fetch last 20 emails (read + unread)
status, messages = mail.search(None, "ALL")
email_ids = messages[0].split()[-1:]
email_ids = list(reversed(email_ids))

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
# ---------- ENHANCED DATASET ----------
spam_samples = [

    "win a free iphone now", "you have won 10 lakh rupees lottery",
    "claim your reward before it expires", "congratulations you are a lucky winner",
    "your number has been selected for cash prize", "get your free amazon gift card",
    "exclusive offer claim 100% bonus now", "congratulations you have won a reward",
    "lottery winner announcement click to claim", "you are chosen for a special reward",


    "limited time offer get 90% off", "buy one get one free deal today",
    "unbelievable discount only for you", "click to activate your offer",
    "get rich quick offer start earning instantly", "investment opportunity earn money fast",
    "instant loan approval available now", "earn money from home without effort",
    "get your prize now hurry up", "work from home and earn ₹5000 per day",
    "apply for easy personal loan", "exclusive deal ends today", "increase your followers instantly",
    "free recharge offer click now", "special festive discount available", 
    "get instant cashback on registration", "new crypto investment scheme join now",


    "your account has been suspended click here", "verify your account immediately",
    "bank alert your card will be blocked", "your paypal account is limited click to restore",
    "click the link to verify your account", "urgent payment required for your parcel",
    "update your billing details to continue", "your subscription is expiring click to renew",
    "final notice pending payment", "your account detected suspicious activity",
    "urgent attention required verify details now", "reset your password immediately here",
    "delivery failed click to reschedule", "you have a parcel waiting for confirmation",


    "free trial click here to start", "double your income fast with our plan",
    "buy now limited stock remaining", "new investment plan earn 50% monthly",
    "earn $500 daily with our system", "cheap medicines available online",
    "your loan approved instantly apply now", "claim your bonus before midnight",
    "download this app to win gifts", "join our affiliate program and earn money",
    "unbelievable deal for you act now", "best trading signals join free today",
    "crypto investment double your profit now"
]

primary_samples = [

    "hello how are you", "thank you for your message", "see you at the meeting tomorrow",
    "family function invitation", "let's meet for lunch tomorrow", "school project discussion today",
    "birthday wishes from your friend", "congratulations on your result",
    "teacher shared notes with you", "friend shared a photo with you",


    "project update from your teacher", "meeting scheduled at 4 pm", "assignment due tomorrow",
    "college result declared today", "class timetable update", "new schedule for exam released",
    "update on your internship application", "college admission confirmation letter",
    "invitation to online seminar", "homework submission reminder",


    "your otp for login is 4321", "security alert for your account", 
    "your amazon order has been shipped", "payment received successfully",
    "invoice for your recent purchase", "your subscription has been renewed successfully",
    "login attempt detected", "password changed successfully",
    "sign in verification code", "bank transaction alert of ₹5000",
    "flight ticket booking confirmed", "your zomato order is out for delivery",
    "google verification code 349521", "order delivered successfully",
    "your recharge is successful", "thank you for your payment",
    "payment confirmed from phonepe", "bill payment successful",


    "meeting link from zoom", "team meeting scheduled today", "daily attendance report",
    "project status updated successfully", "github login detected from new device",
    "microsoft account password reset confirmation", "school circular for parents",
    "reminder for tomorrow's parent meeting", "library book return reminder",
    "assignment marks uploaded", "new announcement from principal",


    "please find attached document", "here is the report you requested",
    "let's finalize the presentation slides", "thank you for your cooperation",
    "i have received your email", "we will discuss it in the next meeting",
    "congratulations on your selection", "wish you all the best for exam"
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