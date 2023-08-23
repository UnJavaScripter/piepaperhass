#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os
assets = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'assets')
libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)

import logging
from waveshare_epd import epd3in7
import time
import math
from PIL import Image,ImageDraw,ImageFont
import traceback
from .components import Box, Card, CardWithStateIndicator, TextHeight, Gauge

logging.basicConfig(level=logging.DEBUG)

class Display:
    def __init__(self, orientation, epd):
        self.orientation = orientation
        self.epd = epd

        if orientation == "horizontal":
            self.width = self.epd.height
            self.height = self.epd.width
            self.dimensions = (self.width, self.height)
        elif orientation == "vertical":
            self.width = self.epd.width
            self.height = self.epd.height
            self.dimensions = (self.height, self.width)

class DisplayHandler:
    
    def __init__(self, entities_json_arr):
        logging.info("epd3in7 Demo")
        
        self.epd = epd3in7.EPD()

        self.display = Display("horizontal", self.epd)

        self.font36 = ImageFont.truetype(os.path.join(assets, 'Font.ttc'), 36)
        self.font24 = ImageFont.truetype(os.path.join(assets, 'Font.ttc'), 24)
        self.font18 = ImageFont.truetype(os.path.join(assets, 'Font.ttc'), 18)
        self.font12 = ImageFont.truetype(os.path.join(assets, 'Font.ttc'), 12)

        self.card_settings = {
            "width": 100,
            "height": 100,
            "margin_x": 5,
            "margin_y": 7,
        }

        logging.info("init and Clear")
        self.epd.init(0)
        self.epd.Clear(0xFF, 0)
        self.epd.init(1)
        self.epd.Clear(0xFF, 1)
        
        self.the_image = Image.new('1', self.display.dimensions, 0xFF)  # 0xFF: clear the frame
        self.draw = ImageDraw.Draw(self.the_image)


        self.start()

    def start(self):
        try:

            for i in range(1, 100, 10):
                
                
                g = Gauge(self.draw, self.display.width, self.display.height, self.font24, self.font12, 1, 2, 0, 100)
                g.set_value(i)
                self.epd.display_1Gray(self.epd.getbuffer(self.the_image))
                time.sleep(2)

        except IOError as e:
            logging.info(e)
            
        except KeyboardInterrupt:    
            logging.info("ctrl + c:")
            epd3in7.epdconfig.module_exit()
            exit()
    
    def update_card_state(self, entity_id, state):
        self.devices_card_object_list[entity_id].set_state(state)
        self.epd.display_1Gray(self.epd.getbuffer(self.the_image))
