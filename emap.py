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
USERNAME = "67jackiechan@gmail.com"       # <-- your Gmail
PASSWORD = "lobzjenfjohjcnqe"             # <-- your App Password

# --- Connect to Gmail using IMAP ---
mail = imaplib.IMAP4_SSL("imap.gmail.com")
mail.login(USERNAME, PASSWORD)
mail.select("inbox")

# --- Fetch ALL Emails (not just unread) ---
status, messages = mail.search(None, 'ALL')
email_ids = messages[0].split()
emails = []

# --- Fetch limited emails for testing (e.g., 20 latest) ---
for num in email_ids[-20:]:  # last 20 emails
    status, data = mail.fetch(num, '(RFC822)')
    msg = email.message_from_bytes(data[0][1])
    subject, encoding = decode_header(msg["Subject"])[0]
    if isinstance(subject, bytes):
        subject = subject.decode(encoding or "utf-8", errors="ignore")
    emails.append(subject)

mail.logout()

# --- Sample Training Data (Spam/Ham examples) ---
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
        "Earn money fast by signing up here!"
    ],
    "label": ["spam", "ham", "spam", "ham", "spam", "ham", "spam", "spam", "ham", "spam"]
}
df = pd.DataFrame(data)

# --- Train Model ---
X_train, X_test, y_train, y_test = train_test_split(df["text"], df["label"], test_size=0.3, random_state=42)
vectorizer = CountVectorizer()
X_train_vec = vectorizer.fit_transform(X_train)
model = MultinomialNB()
model.fit(X_train_vec, y_train)

# --- Evaluate Accuracy ---
X_test_vec = vectorizer.transform(X_test)
y_pred = model.predict(X_test_vec)
print(f"Model Accuracy: {accuracy_score(y_test, y_pred)*100:.2f}%")

# --- Predict on Fetched Gmail Subjects ---
if len(emails) == 0:
    print("⚠️ No emails found.")
else:
    new_vec = vectorizer.transform(emails)
    predictions = model.predict(new_vec)

    print("\n--- Gmail Classification Results ---")
    for subject, label in zip(emails, predictions):
        print(f"[{label.upper()}]  {subject}")

# --- Save model for future use ---
joblib.dump((model, vectorizer), "spam_model.pkl")
print("\n✅ Model and vectorizer saved successfully.")
