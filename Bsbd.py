import win32com.client

def open_outlook():
    """
    Opens Microsoft Outlook application
    """
    outlook = win32com.client.Dispatch("Outlook.Application")
    return outlook


def read_emails(limit=5):
    """
    Read latest emails from Inbox
    """
    outlook = open_outlook()
    namespace = outlook.GetNamespace("MAPI")
    inbox = namespace.GetDefaultFolder(6)  # 6 = Inbox

    messages = inbox.Items
    messages.Sort("[ReceivedTime]", True)

    emails = []
    count = 0

    for message in messages:
        try:
            email_data = {
                "subject": message.Subject,
                "sender": message.SenderName,
                "received": str(message.ReceivedTime),
                "body_preview": message.Body[:200]
            }
            emails.append(email_data)
            count += 1

            if count >= limit:
                break
        except Exception:
            continue

    return emails


if __name__ == "__main__":
    emails = read_emails(5)
    for i, mail in enumerate(emails, 1):
        print(f"\nEmail {i}")
        print(f"Subject: {mail['subject']}")
        print(f"From: {mail['sender']}")
        print(f"Received: {mail['received']}")
        print(f"Preview: {mail['body_preview']}")
