import imaplib
import email
from email.header import decode_header
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score
import joblib

# --- Gmail Login Details ---
USERNAME = "67jackiechan@gmail.com"       # your Gmail
PASSWORD = "lobzjenfjohjcnqe"             # your Gmail App Password

# --- Connect to Gmail ---
print("🔗 Connecting to Gmail...")
mail = imaplib.IMAP4_SSL("imap.gmail.com")
mail.login(USERNAME, PASSWORD)
mail.select("inbox")

# --- Fetch all emails ---
print("📨 Fetching emails from inbox...")
status, messages = mail.search(None, 'ALL')
email_ids = messages[0].split()
emails = []

# --- Get last 20 emails for testing ---
for num in email_ids[-20:]:
    status, data = mail.fetch(num, '(RFC822)')
    msg = email.message_from_bytes(data[0][1])

    # Decode subject
    subject, encoding = decode_header(msg["Subject"])[0]
    if isinstance(subject, bytes):
        subject = subject.decode(encoding or "utf-8", errors="ignore")

    # Extract plain-text email body
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))
            try:
                if content_type == "text/plain" and "attachment" not in content_disposition:
                    body += part.get_payload(decode=True).decode("utf-8", errors="ignore")
            except:
                pass
    else:
        try:
            body = msg.get_payload(decode=True).decode("utf-8", errors="ignore")
        except:
            body = ""

    # Combine subject + body
    full_text = f"{subject}\n{body}"
    emails.append(full_text)

mail.logout()
print(f"✅ Fetched {len(emails)} emails.")

# --- Sample Training Data ---
data = {
    "text": [
        "Win a free iPhone now!!!",
        "Your OTP for login is 4321",
        "You have won 10 lakh rupees lottery!",
        "Meeting scheduled at 4 PM tomorrow",
        "Claim your prize by clicking this link!",
        "Your Amazon order has been shipped",
        "Congratulations, you are selected!",
        "Please verify your bank account now",
        "Invoice for your recent purchase",
        "Earn money fast by signing up here!",
        "Let's meet for the project discussion",
        "Reminder: Pay your electricity bill",
        "Limited time offer, click to claim reward",
        "Re: Regarding tomorrow’s homework submission",
        "Urgent: Your account will be blocked soon!",
        "Thanks for your help today",
        "Download attachment for job offer details"
    ],
    "label": [
        "spam","ham","spam","ham","spam","ham","spam","spam","ham","spam",
        "ham","ham","spam","ham","spam","ham","spam"
    ]
}
df = pd.DataFrame(data)

# --- Train the Model ---
X_train, X_test, y_train, y_test = train_test_split(df["text"], df["label"], test_size=0.3, random_state=42)
vectorizer = CountVectorizer()
X_train_vec = vectorizer.fit_transform(X_train)
model = MultinomialNB()
model.fit(X_train_vec, y_train)

# --- Evaluate Model Accuracy ---
X_test_vec = vectorizer.transform(X_test)
y_pred = model.predict(X_test_vec)
accuracy = accuracy_score(y_test, y_pred) * 100
print(f"🎯 Model trained. Accuracy: {accuracy:.2f}%")

# --- Predict on Real Gmail Emails ---
if len(emails) == 0:
    print("⚠️ No emails found in your inbox.")
else:
    new_vec = vectorizer.transform(emails)
    predictions = model.predict(new_vec)

    print("\n--- 📬 Gmail Email Classification ---")
    for i, (mail_text, label) in enumerate(zip(emails, predictions), 1):
        subject_line = mail_text.split("\n")[0][:100]
        preview = mail_text[:200].replace("\n", " ")
        print(f"\nEmail {i}: [{label.upper()}]")
        print(f"Subject: {subject_line}")
        print(f"Preview: {preview}...")

    # --- Save to Files ---
    with open("spam_emails.txt", "w", encoding="utf-8") as spam_file, \
         open("primary_emails.txt", "w", encoding="utf-8") as ham_file:
        for mail_text, label in zip(emails, predictions):
            if label == "spam":
                spam_file.write(mail_text + "\n\n---\n\n")
            else:
                ham_file.write(mail_text + "\n\n---\n\n")

    print("\n💾 Saved categorized emails into:")
    print("   → spam_emails.txt")
    print("   → primary_emails.txt")

# --- Save the trained model for reuse ---
joblib.dump((model, vectorizer), "spam_model.pkl")
print("✅ Model and vectorizer saved successfully.")
