import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr

sender_add="noreply@umall.one"

# test pw
sender_pw="gZdQaba5j8SqDBa7"



def send_mail(subject, content, receiver_add, receiver_name, content_type='html'):
    """
    Send email
    Parameters:
        subject: subject of the email
            string
        content: content of the email
            string
            html or text
        receiver_add: email address of the receiver
            string
        receiver_name: name of the receiver
            string
        content_type: type of the content
            string
            html or plain
    
    Returns:
        1: if success
        0: if failed
    """
    msg = MIMEText(content, content_type, 'utf-8')
    msg['From'] = formataddr(["UMALL", sender_add])
    msg['To'] = formataddr([receiver_name, receiver_add])
    msg['Subject'] = subject
    try:
        server = smtplib.SMTP_SSL("smtp.exmail.qq.com", 465) 
        server.login(sender_add, sender_pw)
        server.sendmail(sender_add, [receiver_add], msg.as_string())
        server.quit()
        return 1
    except Exception as e:
        print(e)
        return 0




if __name__ == '__main__':
    content="asd"
    send_mail("Hello From UM ALL", content, 'me@boxz.dev' ,"Box")