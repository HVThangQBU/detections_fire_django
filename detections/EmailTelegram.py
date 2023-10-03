

import asyncio
import cv2
import telegram
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from twilio.rest import Client
from detections.readConfig import args
from PIL import Image
import io
import numpy as np

class SendWarning:
  def __init__(self):
    pass
  # def sendEmail(self, toaddr,time_detect,location, frame):
  #   try:
  #     email_address = args["EMAIL_ADDRESS"]
  #     email_password = args["EMAIL_PASSWORD"]
  #     if email_address is None or email_password is None:
  #       # no email address or password
  #       # something is not configured properly
  #       print("Did you set email address and password correctly?")
  #       return False
  #     msg = MIMEMultipart()
  #     msg['From'] = email_address
  #     msg['To'] = toaddr
  #     msg['Subject'] = "CẢNH BÁO CHÁY KHU VỰC ĐỒNG HỚI"
  #     body = "Tình trạng: Hiện tại đang có cháy Địa điểm: Khu vực: " + location + "Thời gian: "+ time_detect + "Hệ thống đính kèm hình ảnh chụp được tại hiện trường để bạn có thể đánh giá và xử lý kịp thời. Xin cảm ơn!"
  #     msg.attach(MIMEText(body, 'plain'))
  #     attachment = frame
  #     p = MIMEBase('application', 'octet-stream')
  #     p.set_payload((attachment).read())
  #     encoders.encode_base64(p)
  #     p.add_header('Content-Disposition', "attachment; frame= %s" % frame)
  #     msg.attach(p)
  #     s = smtplib.SMTP('smtp.gmail.com', 587)
  #     s.starttls()
  #     s.login(email_address, email_password)
  #     text = msg.as_string()
  #     s.sendmail(email_address, toaddr, text)
  #     print("===================================================333333333333333333333333333333333333333333333333")
  #     s.quit()

  #   except Exception as e:
  #     print("Problem during send email", email_address, toaddr, str(e))
     
  def sendEmail(self, toaddr, time_detect, location, frame):
    try:
        email_address = args["EMAIL_ADDRESS"]
        email_password = args["EMAIL_PASSWORD"]
        if email_address is None or email_password is None:
            # no email address or password
            # something is not configured properly
            print("Did you set email address and password correctly?")
            return False
        msg = MIMEMultipart()
        msg['From'] = email_address
        msg['To'] = toaddr
        msg['Subject'] = "CẢNH BÁO CHÁY KHU VỰC ĐỒNG HỚI"
        body = "Chào bạn! \n\nTình trạng: Hiện tại đang có cháy \nĐịa điểm: Khu vực: " + location + "\nThời gian: "+ time_detect + "\nHệ thống đính kèm hình ảnh chụp được tại hiện trường để bạn có thể đánh giá và xử lý kịp thời. \n\nXin cảm ơn!"
        msg.attach(MIMEText(body, 'plain'))
        
        # Convert the NumPy array to a bytes object
        frame_bytes = cv2.imencode('.jpg', frame)[1].tostring()
        
        p = MIMEBase('application', 'octet-stream')
        p.set_payload(frame_bytes)
        encoders.encode_base64(p)
        p.add_header('Content-Disposition', "attachment; filename=frame.jpg")
        msg.attach(p)
        
        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.starttls()
        s.login(email_address, email_password)
        text = msg.as_string()
        s.sendmail(email_address, toaddr, text)
        print("Email sent successfully!")
        s.quit()
    except Exception as e:
        print("Problem during send email", email_address, toaddr, str(e))
  



  # def sendTelegram(self, chat_id, location, time_detect, frame):
  #   try:
  #       my_token = args["MY_TOKEN"]
  #       bot = telegram.Bot(token=my_token)
  #       text = f"Tình trạng: Hiện tại đang có cháy \nĐịa điểm: Khu vực {location} \nThời gian: {time_detect} \nXem hình ảnh để đánh giá và xử lý kịp thời."
  #       caption = "Hình ảnh đám cháy"
  #       bot.send_message(chat_id=chat_id, text=text)
  #       bot.send_photo(chat_id=chat_id, photo=frame, caption=caption)
  #       print("Send success")
  #   except Exception as ex:
  #       print("Can not send message telegram ", ex)



 
  async def send_message_async(self, text, photo):
      bot = telegram.Bot(token='6172070800:AAH2ErADahQRbboQbJcoD2FUNph7MeOBNbA')
      chat_id = '5150505079'
    
      # Convert the image to a numpy array
      image_np = np.array(photo)

# Convert the color space from RGB to BGR
      image_np_bgr = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)

# Convert the numpy array back to image Pil

      image_pil = Image.fromarray(np.uint8(image_np_bgr))

      

      # create a byte buffer to hold the image data
      with io.BytesIO() as buffer:
          # save the Pillow Image object to the buffer in JPEG format
          image_pil.save(buffer, format='PNG')
          # get the byte data from the buffer
          buffer.seek(0)
          photo_bytes = buffer.read()
      try:
        # Tăng thời gian chờ (timeout) lên 60 giây (hoặc tùy chỉnh thời gian cần thiết)
        img = await asyncio.wait_for(bot.send_photo(chat_id=chat_id, photo=photo_bytes, caption="Hình ảnh đám cháy"), timeout=60)
        message = await asyncio.wait_for(bot.send_message(chat_id=chat_id, text=text), timeout=60)
         
        return message, img
      except telegram.error.TimedOut:
        return

  def sendSMS(self, body):
    # Your Account Sid and Auth Token from twilio.com / console
    account_sid = 'AC4ee5b584a317a57b13408c3a0d55f8de'
    auth_token = '6d9836581a2d23e64756a506b3763998'
    client = Client(account_sid, auth_token)
    message = client.messages.create(
      from_='+12765319021',
      body=body,
      to='+84862427726'
    )
    print(message.sid)

