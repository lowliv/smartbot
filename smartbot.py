import os
import sys
import re
import base64
import time
import cv2
import argparse as arg
import numpy as np
from openai import OpenAI
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

def on_ok_click(window):
  window.close()
  
def on_cancel_click(window):
  window.close()
  exit()

def get_confirmation():
  app = QApplication(sys.argv)
  window = QWidget()
  window.setWindowTitle("Smartbot")
  font = QFont("JetBrains Mono", 16, QFont.Weight.Bold)  # Set font to Arial, size 16, bold
  
  ok = QPushButton("OK")
  ok.setFont(font)

  ok.clicked.connect(lambda: on_ok_click(window))
  ok.setStyleSheet("""
    QPushButton {
      border-radius: 0px;
      background-color: #f93357;
      color: white;
      font-size: 16px;
      padding: 10px;
      border: none;
      }
    """)
  
  cancel = QPushButton("Cancel")
  cancel.setFont(font)

  cancel.clicked.connect(lambda: on_cancel_click(window))
  cancel.setStyleSheet("""
    QPushButton {
      border-radius: 0px;
      background-color: #f93357;
      color: white;
      font-size: 16px;
      padding: 10px;
      border: none;
      }
    """)

  # Set up layout and add button
  layout = QVBoxLayout()
  label = QLabel("Confirm smartbot usage")
  label.setFont(font)
  label.setAlignment(Qt.AlignmentFlag.AlignCenter)
  label.setStyleSheet(   
    """
    QLabel {
      color: white;
      font-weight: bold;
      background-color: transparent;
    }
    """)

  button_layout = QHBoxLayout()
  button_layout.addWidget(ok)
  button_layout.addWidget(cancel)
  
  main_layout = QVBoxLayout()
  main_layout.addWidget(label)
  main_layout.addLayout(button_layout)
  
  window.setLayout(main_layout)
  window.resize(200,200)
  window.setStyleSheet("background-color: rgba(26, 39, 58, 160)")
  window.show()
  app.exec()
  
def get_answer(prompt):
  output.append("get_answer")
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
            "text": f"{prompt}",
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
  output.append(f"correct_answer = {correct_answer}\n")
  os.system(f"notify-send -a 'smartbot:' '{correct_answer}'")
  return correct_answer
        
def click_answer(correct_answer):
  output.append("click_answer\n")
  output.append(f"int_correct_answer = {correct_answer}")
  screenscale = float(os.environ.get('SCREEN_SCALE',1))
  os.system("hyprshot -m active -m output -s -o $PWD -f screen.png")
  time.sleep(0.5)
  img = cv2.imread("screen.png", cv2.IMREAD_COLOR)
  template = cv2.imread("templates/circle.png", cv2.IMREAD_COLOR)
  h, w, p = template.shape[::-1]
  res = cv2.matchTemplate(img, template,getattr(cv2, 'TM_CCOEFF_NORMED'))
  loc = np.where( res >= 0.8)
  count = 0
  for pt in zip(*loc[::-1]):
    count += 1
    output.append(str(count) + "\n")
    if count != correct_answer:
      continue
    else:
      click_x = pt[0] + .5*w 
      click_y = pt[1] + .5*h + 10
      os.system('YDOTOOL_SOCKET="$HOME/.ydotool_socket" ydotool mousemove -a -x ' + str(int(click_x/(2*screenscale))) + "-y " + str(int(click_y/(2*screenscale))))
      os.system('YDOTOOL_SOCKET="$HOME/.ydotool_socket" ydotool click C0')
      
def type_answer(correct_answer):
  output.append("type_answer\n")
  os.system(f"notify-send -a 'smartbot:' 'typing answer in 3 seconds highlight input field'")
  time.sleep(3)
  os.system(f"wtype {correct_answer}")
      
if __name__ == "__main__":
  parser = arg.ArgumentParser()

  parser.add_argument("noconfirm", type=int)
  parser.add_argument("mcq_or_frq")

  args = parser.parse_args()

  if args.noconfirm == 0:
    get_confirmation()
    
  output = []
  output.append(f"arg.absnoconfirm = {args.noconfirm}\n")
  output.append(f"arg.mcq_or_frq = {args.mcq_or_frq}\n")
  
  home_path = os.environ.get('HOME')
  os.system("mkdir -p $HOME/.cache/smartbot/templates")
  os.chdir(f"{home_path}/.cache/smartbot")
  
  if args.mcq_or_frq == "mcq":
    if not os.path.isfile("templates/circle.png"):
      os.system(f"notify-send -a smartbot: no target circle at .cache/smartbot/templates/circle.png")
    else:
      time.sleep(3)
      prompt = "You are reviewing a multiple choice quiz. An answer may be pre-selected but it could be wrong, so you should ignore it. Answer the multiple choice question by saying the correct answer choice and the number corresponding this answer choice if they were labeled sequentially starting with 1 at the top. Do not use parentheses, or brackets.",
      answer_list = re.split(', *.', get_answer(prompt))
      # answer_list = "3 testing answer".split()
      for n in answer_list:
        try:
          number = int(n)
          if number >= 1 and number <= 5:
            click_answer(number)
            break
        except:
          continue
      
  elif args.mcq_or_frq == "frq":
    prompt = "Answer the question in a short sentence."
    correct_answer = get_answer(promp)
    # correct_answer = "testing"
    type_answer(correct_answer)
    
  file = open("output", "w+")
  file.writelines(output)
  file.close()
