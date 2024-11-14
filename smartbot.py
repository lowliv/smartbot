import os
import sys
import re
import time
import json
import argparse as arg

def get_font_weight(weight_str):
  from PyQt6.QtGui import QFont
  weight_map = {
    "Thin": QFont.Weight.Thin,
    "ExtraLight": QFont.Weight.ExtraLight,
    "Light": QFont.Weight.Light,
    "Normal": QFont.Weight.Normal,
    "Medium": QFont.Weight.Medium,
    "DemiBold": QFont.Weight.DemiBold,
    "Bold": QFont.Weight.Bold,
    "ExtraBold": QFont.Weight.ExtraBold,
    "Black": QFont.Weight.Black
  }
  return weight_map.get(weight_str, QFont.Weight.Normal)
   
def on_ok_click(window):
  window.close()
  
def on_cancel_click(window):
  window.close()
  exit()

def get_confirmation(ok_button_label, cancel_button_label, ok_button_style, cancel_button_style, label_style, window_style, font_name, font_size, font_weight_str):
  from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
  from PyQt6.QtGui import QFont
  from PyQt6.QtCore import Qt
  
  app = QApplication(sys.argv)
  window = QWidget()
  window.setWindowTitle("Smartbot")
  
  font_weight = get_font_weight(font_weight_str)
  font = QFont(font_name, font_size, font_weight)
  
  ok = QPushButton(ok_button_label)
  ok.setFont(font)
  ok.clicked.connect(lambda: on_ok_click(window))
  ok.setStyleSheet(ok_button_style)
  
  cancel = QPushButton(cancel_button_label)
  cancel.setFont(font)
  cancel.clicked.connect(lambda: on_cancel_click(window))
  cancel.setStyleSheet(cancel_button_style)

  label = QLabel("Confirm smartbot usage")
  label.setFont(font)
  label.setAlignment(Qt.AlignmentFlag.AlignCenter)
  label.setStyleSheet(label_style)

  button_layout = QHBoxLayout()
  button_layout.addWidget(ok)
  button_layout.addWidget(cancel)
  
  main_layout = QVBoxLayout()
  main_layout.addWidget(label)
  main_layout.addLayout(button_layout)
  
  window.setLayout(main_layout)
  window.resize(200,200)
  window.setStyleSheet(window_style)
  window.show()
  app.exec()
  
def get_answer(prompt, model_str):
  from openai import OpenAI
  import base64
  import cv2
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
    model= f"{model_str}",
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
  import numpy as np
  import cv2
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
      
def copy_answer(correct_answer):
  import pyclip
  pyclip.copy(correct_answer)
  os.system(f"notify-send -a 'smartbot:' 'answer copied to clipboard'")
  output.append("copy_answer\n")
  
if __name__ == "__main__":
  parser = arg.ArgumentParser()

  parser.add_argument("noconfirm", type=int)
  parser.add_argument("mcq_or_frq")

  args = parser.parse_args()

  output = []
  output.append(f"arg.absnoconfirm = {args.noconfirm}\n")
  output.append(f"arg.mcq_or_frq = {args.mcq_or_frq}\n")
  
  home_path = os.environ.get('HOME')
  os.system("mkdir -p $HOME/.config/smartbot/templates")
  os.chdir(f"{home_path}/.config/smartbot")
  if not os.path.isfile("config.json"):
    file = open("config.json", "w+")
    default_config = ['{\n', '  "Prompts": {\n', '    "mcq_prompt": "You are reviewing a multiple choice quiz. An answer may be pre-selected but it could be wrong, so you should ignore it. Answer the multiple choice question by saying the correct answer choice and the number corresponding this answer choice if they were labeled sequentially starting with 1 at the top. Do not use parentheses, or brackets.",\n', '    "frq_prompt": "Answer the question in a short sentence."\n', '  },\n', '  "ButtonLabel": {\n', '    "ok_button": "OK",\n', '    "cancel_button": "Cancel"\n', '  },\n', '  "Style": {\n', '    "label": "QLabel { color: white; font-weight: bold; background-color: transparent; }",\n', '    "window": "background-color: #24273a",\n', '    "ok_button": "QPushButton { border-radius: 0px; background-color: #f93357; color: white; font-size: 16px; padding: 10px; border: none; }",\n', '    "cancel_button": "QPushButton { border-radius: 0px; background-color: #f93357; color: white; font-size: 16px; padding: 10px; border: none; }"\n', '  },\n', '  "Font": {\n', '    "font_name": "JetBrains Mono",\n', '    "font_size": 16,\n', '    "font_weight": "Bold"\n', '  },\n', '  "Model": "gpt-4o-mini"\n', '}\n']
    file.writelines(default_config)
    file.close()
    
  file = open("config.json", "r")
  config = json.load(file)
  file.close()
  ok_button_label = config["ButtonLabel"]["ok_button"]
  cancel_button_label = config["ButtonLabel"]["cancel_button"]
  label_style = config["Style"]["label"]
  window_style = config["Style"]["window"]
  ok_button_style = config["Style"]["ok_button"]
  cancel_button_style = config["Style"]["cancel_button"]
  mcq_prompt = config["Prompts"]["mcq_prompt"]
  frq_prompt = config["Prompts"]["frq_prompt"]
  font_name = config["Font"]["font_name"]
  font_size = config["Font"]["font_size"]
  font_weight_str = config["Font"]["font_weight"]
  model_str = config["Model"]
    
  if args.noconfirm == 0:
    get_confirmation(ok_button_label, cancel_button_label, ok_button_style, cancel_button_style, label_style, window_style, font_name, font_size, font_weight_str)
  if args.mcq_or_frq == "mcq":
    if not os.path.isfile("templates/circle.png"):
      os.system(f"notify-send -a smartbot: no target circle at .config/smartbot/templates/circle.png")
    answer_list = re.split(', *.', get_answer(mcq_prompt,model_str))
    for n in answer_list:
      try:
        number = int(n)
        if number >= 1 and number <= 5 and os.path.isfile("templates/circle.png"):
          click_answer(number)
          break
      except:
        continue
      
  elif args.mcq_or_frq == "frq":
    correct_answer = get_answer(frq_prompt,model_str)
    copy_answer(correct_answer)
    
  file = open("output", "w+")
  file.writelines(output)
  file.close()
  
# Generate new default_config:
# file = open("/home/lowliver/.config/smartbot/config.json", "r")
# o = file.readlines()
# output = open("/home/lowliver/.config/smartbot/output", "w+")
# output.write(str(o))

