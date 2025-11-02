import smtplib
from email.message import EmailMessage
import time

# Sender account (a DIFFERENT gmail account than the one you're testing)
SENDER = "timemacx7@gmail.com"
SENDER_APP_PW = "eplipkmcwaptejnm"   # 16-char app password for sender
RECIPIENT = "67jackiechan@gmail.com"    # your test Gmail

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# Templates to send
messages = [
    # --- PRIMARY EMAILS ---
    ("Hello bro", "Hey! How are you doing? Let's meet tomorrow at the café."),
    ("Your OTP for login", "Your OTP is 123456. Do not share this code with anyone."),
    ("Account activity alert", "We noticed a sign-in from a new device. If it wasn’t you, please reset your password."),
    ("Invoice for your recent purchase", "Please find attached invoice for your recent order #12345."),
    ("Meeting reminder", "This is a reminder for your meeting scheduled at 4 PM today."),
    ("School project update", "Please submit your science project report by tomorrow."),
    ("Payment received", "Your payment of ₹1,200 has been received successfully."),
    ("Your Amazon order", "Your Amazon order #78965 has been shipped and will arrive tomorrow."),
    ("Flight ticket confirmation", "Your flight to Delhi is confirmed for 10th November at 6:00 AM."),
    ("Class schedule update", "The physics class will be held at 10:30 AM instead of 9 AM."),
    ("Password changed successfully", "You have successfully changed your password."),
    ("Meeting link from Zoom", "Join the meeting using this link: https://zoom.us/j/123456789"),
    ("Google verification code", "Your Google verification code is 987654."),
    ("Teacher shared notes", "Your teacher has shared class notes for chapter 5."),
    ("Library reminder", "Please return your library books before Friday."),
    ("Resume attached", "Please find my resume attached for your reference."),
    ("Thank you", "Thank you for your response. Looking forward to meeting you."),
    ("Project submission", "Please upload your final project by 11:59 PM tonight."),

    # --- SPAM EMAILS ---
    ("WIN a free iPhone now!!!", "Click here to claim your free iPhone today: http://spam-link.example"),
    ("You have won a lottery", "Congratulations! You have won ₹10,00,000. Claim your reward now."),
    ("Claim your prize", "Your prize is waiting! Verify your details to receive it."),
    ("Limited time offer", "Hurry! Get 90% discount on all products. Click here to buy now."),
    ("Urgent payment required", "Your parcel is waiting for payment confirmation. Click to pay now."),
    ("Bank alert", "Your account will be blocked. Verify immediately: http://fakebank.example"),
    ("Free recharge offer", "Get ₹100 free recharge by clicking this link now."),
    ("Crypto investment offer", "Invest ₹1000 today and earn ₹5000 in a week. Join our Telegram group."),
    ("Get rich quick", "Earn $1000 daily working from home. No skills required."),
    ("Account suspended", "Your account has been suspended. Click the link to verify your identity."),
    ("Final notice", "Your subscription will expire today. Renew now to continue."),
    ("Gift card for you", "Get a free Amazon gift card by filling this quick survey."),
    ("Work from home opportunity", "Join our affiliate program and start earning instantly."),
    ("Cheap medicines online", "Buy medicines at 80% off. Limited stock available!"),
    ("Special festive offer", "Buy one get one free! Offer ends tonight."),
    ("Weekly deals", "<html><body><h1>Big Sale</h1><p>Click <a href='http://spam.example'>here</a> for offers!</p></body></html>"),
    ("Congratulations winner!", "You are selected as the lucky winner! Claim your bonus now."),
]


def send_message(subject, body, subtype="plain"):
    msg = EmailMessage()
    msg["From"] = SENDER
    msg["To"] = RECIPIENT
    msg["Subject"] = subject
    if subtype == "html":
        msg.set_content("This is an HTML message; enable HTML to view")
        msg.add_alternative(body, subtype="html")
    else:
        msg.set_content(body)

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.login(SENDER, SENDER_APP_PW)
        smtp.send_message(msg)
        print(f"Sent: {subject}")

if __name__ == "__main__":
    for subj, body, *rest in messages:
        subtype = rest[0] if rest else "plain"
        send_message(subj, body, subtype)
        time.sleep(1)  # small pause
    print("All test emails sent.")
