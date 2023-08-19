import logging

logging.basicConfig(level=logging.DEBUG)

# https://levelup.gitconnected.com/how-to-properly-calculate-text-size-in-pil-images-17a2cc6f51fd
class TextHeight:
  def __init__(self, font):
    self.font = font

  def get(self, text_string):
    # https://stackoverflow.com/a/46220683/9263761
    ascent, descent = self.font.getmetrics()

    text_width = self.font.getmask(text_string).getbbox()[2]
    text_height = self.font.getmask(text_string).getbbox()[3] + descent

    return text_width, text_height, ascent, descent
  
  def get_header_height(self, margin_y):
    return self.font.size + (self.font.size / 4) + margin_y * 2

class Box:
  def __init__(self, draw, start_x, start_y, end_x, end_y, outline = 0, fill = 255):
    self.draw = draw
    self.start_x = start_x
    self.start_y = start_y
    self.end_x = end_x
    self.end_y = end_y
    self.outline = outline
    self.fill = fill

    self._draw_rectangle()

  def _draw_rectangle(self):
    return self.draw.rectangle((self.start_x, self.start_y, self.end_x, self.end_y), outline = self.outline, fill=self.fill)

class Label:
  def __init__(self, draw, container_x, container_y, header_width, header_height, margin_x, margin_y, text_width, text_height, ascent, descent, text, font=None, fill = 0):
    self.draw = draw
    self.container_x = container_x
    self.container_y = container_y
    self.header_width = header_width
    self.margin_x = margin_x
    self.margin_y = margin_y
    self.text_width = text_width
    self.text_height = text_height
    self.ascent = ascent
    self.descent = descent
    self.header_height= header_height
    self.text = text
    self.font = font
    self.fill = fill
    self._draw_label()

  def _draw_label(self):
    mid_x = self.container_x + ((self.header_width / 2) - (self.text_width / 2)) + (self.margin_x / 2)
    # https://levelup.gitconnected.com/how-to-properly-calculate-text-size-in-pil-images-17a2cc6f51fd
    if (self.font.size + 1 == self.text_height):
      mid_y = self.container_y + ((self.header_height / 2) - (self.text_height / 2)) 
    else:
      mid_y = self.container_y +((self.header_height / 2) - (self.text_height / 2)) + ((self.margin_y / 2)) - self.ascent / self.descent
    return self.draw.text((mid_x, mid_y), self.text, font=self.font, fill=self.fill)

class RoundIndicator:
  def __init__(self, draw, x, y, container_width, margin_x, margin_y, state):
    self.draw = draw
    self.x = x
    self.y = y
    self.container_width = container_width
    self.margin_x = margin_x
    self.margin_y = margin_y
    self.diameter = self.container_width / 2
    self.state = state
    
    self._draw_indicator()
  
  def _draw_indicator(self):
    mid_x = self.x + (self.container_width / 2)
    start_x = mid_x - self.diameter / 2
    end_x = mid_x + self.diameter / 2

    start_y = self.y + self.margin_y
    end_y = start_y + self.diameter

    self.draw.rectangle((start_x, start_y, end_x, end_y), fill=255)
    if (self.state):
      self.draw.chord((start_x, start_y, end_x, end_y), 0, 360, fill = 0)
    else:
      self.draw.arc((start_x, start_y, end_x, end_y), 0, 360)

class Card:
  def __init__(self, draw, x, y, width, label_text, font, margin_x, margin_y, state=False, auto_draw = True):
    self.draw = draw
    self.x = x
    self.y = y
    self.label_text = label_text
    self.font = font

    self.text_width, self.text_height, self.ascent, self.descent = TextHeight(font).get(self.label_text)
    self.margin_x = margin_x
    self.margin_y = margin_y
    self.state = state

    # logging.info("000000000000000000000")
    # logging.info(f"font.size: {self.font.size}")
    # # logging.info(f"text_width: {self.text_width}")
    # logging.info(f"text_height: {self.text_height}")
    # logging.info(f"ascent: {self.ascent}")
    # logging.info(f"descent: {self.descent}")
    # logging.info("_________________________")

    if width < self.text_width:
      self.width = self.text_width + (self.margin_x * 2)
    else:
      self.width = width 

    self.header_height = TextHeight(self.font).get_header_height(self.margin_y)
    
    if auto_draw:
      self.draw_card()

  def draw_card(self, new_state = None):
    state = new_state if new_state is not None else self.state
    Box(self.draw, self.x, self.y, self.x + self.width, self.y + self.header_height, fill = 0 if state else 255)
    Label(self.draw, self.x, self.y, self.width, self.header_height, self.margin_x, self.margin_y, self.text_width, self.text_height, self.ascent, self.descent, self.label_text, font=self.font, fill = 255 if state else 0)

  def set_state(self, state):
    self.draw_card(state) 

class CardWithStateIndicator(Card):
  def __init__(self, draw, x, y, width, height, label_text, font, margin_x, margin_y, state = False, auto_draw = True):
    super().__init__(draw, x, y, width, height, label_text, font, margin_x, margin_y, state=False, auto_draw = True)
    
    Box(self.draw, self.x, self.y + self.header_height, self.x + self.width, self.y + + self.height)
    self.set_state(state)

  def set_state(self, state):
    y = self.y + self.header_height
    RoundIndicator(self.draw, self.x, y, self.margin_x, self.margin_y, state)

# class Row():
#   def __init__(self, draw, x, y, image_size, margin_x, margin_y, font, children):
#     self.draw = draw
#     self.x = x
#     self.y = y
#     self.width = image_size[0]
#     self.height = image_size[1]
#     self.margin_x = margin_x
#     self.margin_y = margin_y
#     self.font = font
#     self.children = children

#   def draw_row(self):
#     next_child_start_x = self.x
#     for i, child in enumerate(self.children):
#       if next_child_start_x + (child["width"] + self.margin_x) <= self.width:
#         c = CardWithStateIndicator(self.draw, self.x if i == 0 else next_child_start_x, self.y, child["width"], child["height"], child["label"], self.font, child["margin_x"], child["margin_y"], False, False)        
        
#         next_child_start_x += (c.width + self.margin_x)
#       else:
#         next_child_start_x = self.x
#         c = CardWithStateIndicator(self.draw, self.x if i == 0 else next_child_start_x, self.y + child["height"] + self.margin_y, child["width"], child["height"], child["label"], self.font, child["margin_x"], child["margin_y"], False, False)        
#         next_child_start_x += (c.width + self.margin_x)

#       c.draw_card()
# ----------------------------- imp
            # r = Row(self.draw, 0, 0, self.the_image.size, 30,  0, self.font18, self.devices_json_data_list)
            # r.draw_row()
            # self.epd.display_1Gray(self.epd.getbuffer(self.the_image))    





