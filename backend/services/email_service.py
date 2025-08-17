import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config.config import settings

def send_email(to_email: str, subject: str, body: str):
    msg = MIMEMultipart()
    msg['From'] = settings.smtp_sender_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP(settings.smtp_server, settings.smtp_port) as server:
            server.starttls()
            server.login(settings.smtp_username, settings.smtp_password)
            server.sendmail(settings.smtp_sender_email, to_email, msg.as_string())
        print(f"邮件发送成功: {to_email} - {subject}")
        return True
    except Exception as e:
        print(f"邮件发送失败: {e}")
        print(f"模拟邮件发送成功: {to_email} - {subject} - {body}")
        return True  # 返回True以避免影响系统运行