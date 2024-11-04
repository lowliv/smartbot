# Refrences: https://platform.openai.com/docs/guides/vision
# Run sudo -b ydotoold --socket-path="$HOME/.ydotool_socket" --socket-own="$(id -u):$(id -g)" before starting
# Put answer choice png in $HOME/.cache/smartbot/templates/cirle.png

import os
import base64
import time
import cv2
import numpy as np
from openai import OpenAI

def get_answer():
  os.system("hyprshot -m active -m window -s -o $PWD -f window.png")
  time.sleep(0.5)
  image_path = "window.png"
  image = cv2.imread(image_path)
  cv2.imwrite("window.jpg", image, [int(cv2.IMWRITE_JPEG_QUALITY), 100])
  image_path = "window.jpg"
  
  gpt_key = os.environ.get('GPT_KEY')
  client = OpenAI(api_key=gpt_key)
  
  # Function to encode the image
  def encode_image(image_path):
    with open(image_path, "rb") as image_file:
      return base64.b64encode(image_file.read()).decode('utf-8')
  
  # Getting the base64 string
  base64_image = encode_image(image_path)
  
  response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
      {
        "role": "user",
        "content": [
          {
            "type": "text",
            "text": "Answer the multiple choice question by saying only a number corresponding the correct option if they were labeled sequentially starting with 1 at the top.",
          },
          {
            "type": "image_url",
            "image_url": {
              "url":  f"data:image/jpeg;base64,{base64_image}"
            },
          },
        ],
      }
    ],
    max_tokens = 300,
  )
  
  correct_answer = response.choices[0].message.content.strip()
  output.append(correct_answer)
  
  try:
    return int(correct_answer)
  except:
    output.append("NOT INT")
    return 0
        
def click_answer(correct_answer):
  os.system("hyprshot -m active -m output -s -o $PWD -f screen.png")
  time.sleep(0.5)
  img = cv2.imread("screen.png", cv2.IMREAD_COLOR)
  template = cv2.imread("templates/circle.png", cv2.IMREAD_COLOR)
  h, w, p = template.shape[::-1]
  res = cv2.matchTemplate(img, template,getattr(cv2, 'TM_CCOEFF_NORMED'))
  loc = np.where( res >= 0.9)
  count = 0
  for pt in zip(*loc[::-1]):
    count += 1
    output.append(count)
    if count != correct_answer:
      continue
    else:
      click_x = pt[0] + .5*w 
      click_y = pt[1] + .5*h + 10
      os.system('YDOTOOL_SOCKET="$HOME/.ydotool_socket" ydotool mousemove -a -x ' + str(int(click_x)/4) + "-y " + str(int(click_y)/4))
      os.system('YDOTOOL_SOCKET="$HOME/.ydotool_socket" ydotool click C0')

output = []
home_path = os.environ.get('HOME')
os.system("mkdir -p $HOME/.cache/smartbot")

os.chdir(f"{home_path}/.cache/smartbot")
if os.path.isfile("templates/circle.png"):
  time.sleep(2)
  click_answer(get_answer())
  file = open("output", "w")
  file.writelines(output)
