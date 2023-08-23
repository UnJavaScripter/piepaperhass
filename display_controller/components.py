import logging
import math

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

class Gauge():
  def __init__(self, draw, width, height, font_large, font_small, border_width, needle_width, min_value=0, max_value=100):
    self.draw = draw
    self.font_small = font_small
    self.font_large = font_large
    self.needle_width = needle_width
    self.min_value = min_value

    self.center_x = width // 2
    self.center_y = height // 2
    self.radius = width // 4


    start_angle = -225  # Angle for 0 value
    end_angle = 45  # Angle for 100 value
    
    # The Gauge background
    shape = [(self.center_x - self.radius, self.center_y - self.radius), (self.center_x + self.radius, self.center_y + self.radius)]

    self.draw.pieslice(shape, start=start_angle, end=end_angle, fill = 255, outline=0, width=border_width)
    
    # Indicators angles
    angle_range = end_angle - start_angle - (end_angle * 1)
    self.angle_step = angle_range / (max_value - self.min_value)
    
    # Indicators offset
    self.offset_start = start_angle + ((end_angle / 2) / self.radius * 180 / math.pi)

    for indicator_value in range(self.min_value, max_value + 1, 10):
      angle = (self.offset_start + ((indicator_value - self.min_value) * self.angle_step)  ) + 4
      radian_angle = math.radians(angle)
      
      indicator_line_x1 = self.center_x + (self.radius) * math.cos(radian_angle)
      indicator_line_y1 = self.center_y + (self.radius) * math.sin(radian_angle)
      indicator_line_x2 = self.center_x + (self.radius - self.font_small.size * .3) * math.cos(radian_angle)
      indicator_line_y2 = self.center_y + (self.radius - self.font_small.size * .3) * math.sin(radian_angle)

      indicator_number_x2 = self.center_x + (self.radius - self.font_small.size * 1.4) * math.cos(radian_angle)
      indicator_number_y2 = self.center_y + (self.radius - self.font_small.size * 1.4) * math.sin(radian_angle)
      
      self.draw.line([(indicator_line_x1, indicator_line_y1), (indicator_line_x2, indicator_line_y2)], fill = 0, width=math.ceil(self.font_small.size * 0.1))
      
      indicator_label_text = str(indicator_value)
      (bbx, bby, label_width, label_height) = self.font_small.getbbox(indicator_label_text)
      label_x = (indicator_number_x2 - label_width // 2)
      label_y = (indicator_number_y2 - label_height // 2)
      self.draw.text((label_x, label_y), indicator_label_text, fill = 0, font=self.font_small)
        

  def set_value(self, value):
    needle_angle = (self.offset_start + (value - self.min_value) * self.angle_step) + 4
    needle_length = self.radius - self.font_small.size * 2
    needle_x = self.center_x + int(needle_length * math.cos(math.radians(needle_angle)))
    needle_y = self.center_y + int(needle_length * math.sin(math.radians(needle_angle)))
    
    # Draw needle
    self.draw.line([(self.center_x, self.center_y), (needle_x, needle_y)], fill = 0, width=self.needle_width)

    # Draw value
    label_text = str(value)
    (bbx, bby, label_width, label_height) = self.font_large.getbbox(label_text)
    label_x = self.center_x - label_width // 2
    label_y = self.center_y + self.radius / 3.3
    self.draw.rectangle([(label_x, label_y), (label_x + label_width, label_y + label_height)], fill = 255)
    self.draw.text((label_x, label_y), label_text, fill = 0, font=self.font_large)

    
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





