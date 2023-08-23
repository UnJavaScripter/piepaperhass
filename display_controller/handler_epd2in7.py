#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os
assets = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'assets')
libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)

import logging
from waveshare_epd import epd2in7
import time
import math
from PIL import Image,ImageDraw,ImageFont
import traceback
from .components import Box, Card, CardWithStateIndicator, TextHeight

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
        logging.info("epd2in7 Demo")
        self.devices_card_object_list = {}
        self.entities_json_arr = entities_json_arr
        self.epd = epd2in7.EPD()

        self.display = Display("horizontal", self.epd)

        self.font36 = ImageFont.truetype(os.path.join(assets, 'Font.ttc'), 36)
        self.font24 = ImageFont.truetype(os.path.join(assets, 'Font.ttc'), 24)
        self.font18 = ImageFont.truetype(os.path.join(assets, 'Font.ttc'), 18)

        self.card_settings = {
            "width": 100,
            "height": 100,
            "margin_x": 5,
            "margin_y": 7,
        }

        logging.info("init and Clear")
        self.epd.init()
        self.epd.Clear(0xFF)
        
        self.the_image = Image.new('1', self.display.dimensions, 0xFF)  # 0xFF: clear the frame
        self.draw = ImageDraw.Draw(self.the_image)

        self.start()

    def start(self):
        try:
            devices_len = len(self.entities_json_arr)
            x_starting_point = (self.display.width / 2) - ((self.card_settings["width"] / 2 ) * math.floor(self.display.width / self.card_settings["width"]) ) - 12
            y_starting_point = (self.display.height / 2) - ((self.card_settings["height"] / 2 ) * math.floor(self.display.height / self.card_settings["height"]) ) - self.card_settings["margin_y"] * 5
            current_start_x = x_starting_point
            current_start_y = y_starting_point
            for entity in self.entities_json_arr:
                logging.info(entity["state"])
                c = Card(self.draw, current_start_x, current_start_y, self.card_settings["width"], entity["label"], self.font18, self.card_settings["margin_x"], self.card_settings["margin_y"], entity["state"])
                self.devices_card_object_list[entity["entity_id"]] = c
                current_start_x += self.card_settings["width"] + self.card_settings["margin_x"]
                if current_start_x + self.card_settings["margin_x"] + self.card_settings["width"] > self.display.width:
                    current_start_x = x_starting_point
                    current_start_y = current_start_y + self.card_settings["margin_y"] + TextHeight(self.font18).get_header_height(self.card_settings["margin_y"])
            self.epd.display(self.epd.getbuffer(self.the_image))
            
        except IOError as e:
            logging.info(e)
            
        except KeyboardInterrupt:    
            logging.info("ctrl + c:")
            epd2in7.epdconfig.module_exit()
            exit()
    
    def update_card_state(self, entity_id, state):
        self.devices_card_object_list[entity_id].set_state(state)
        self.epd.display(self.epd.getbuffer(self.the_image))

