# -*- coding: utf-8 -*-

import os
import os.path as osp
from pkg_resources import resource_stream

import argparse

import numpy as np
from moviepy.editor import *
from PIL import Image, ImageFont, ImageDraw


class Converter:
    def __init__(self, video_input_path, video_output_path, chars_width, fps, isGray, time_start=0, time_end=None):
        self.video_path = video_input_path
        self.video_name = osp.basename(video_input_path).split('.')[0]
        self.output_path = video_output_path if video_output_path else osp.dirname(video_input_path)
        self.output_path = osp.join(self.output_path, self.video_name + "_char2.mp4")
        self.isGray = isGray
        self.vfc = VideoFileClip(self.video_path).subclip(time_start, time_end)
        self.fps = fps
        self.chars_width = chars_width
        self.chars_height = int(self.chars_width / self.vfc.aspect_ratio)
        self.vfc = self.vfc.resize((self.chars_width, self.chars_height))
        font_fp = "DroidSansMono.ttf"
        self.font = ImageFont.truetype(font_fp, size=14)
        self.font_width = sum(self.font.getsize('a')) // 2

        self.video_size = int(self.chars_width * self.font_width), int(self.chars_height * self.font_width)

        # 值越大，映射的字母越靠后，表示像素更"白"
        self.pixels = \
            "$#@&%ZYXWVUTSRQPONMLKJIHGFEDCBA098765432?][}{/)(><zyxwvutsrqponmlkjihgfedcba*+1-."
        #    "$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\|()1{}[]?-_+~<>i!lI;:,\"^`'. "

    def gray2char(self, gray):
        """通过灰度值获取当前像素的字符"""
        percent = float(gray) / 255
        index = int(percent * (len(self.pixels) - 1))
        return self.pixels[index]

    def frame2char(self, t):
        """
        将每一帧的图片转化为字符
        本函数作为 moviepy.editor.VideoClip 特效功能的入口参数
        相当于对时间 t 内的视频做转为字符的特效处理
        :return: numpy.array 类型字符列表
        """
        img_np = self.vfc.get_frame(t)
        img = Image.fromarray(img_np, 'RGB')
        img_gary = img.convert(mode='L')

        img_char = Image.new('RGB', self.video_size, color='white')
        brush = ImageDraw.Draw(img_char)

        white = (255, 255, 255)
        black = (0, 0, 0)

        for y in range(self.chars_height):
            for x in range(self.chars_width):
                r, g, b = img_np[y][x] if not self.isGray else black

                gray = img_gary.getpixel((x, y))
                char = self.gray2char(gray)

                position = x * self.font_width, y * self.font_width
                brush.text(position, char, fill=(r, g, b), font=self.font)

        # img_char = img_char if not self.isGray else img_char.convert(mode='L')
        return np.array(img_char)

    def generate(self):
        """生成字符对象"""
        clip = VideoClip(self.frame2char, duration=self.vfc.duration)
        clip = clip.set_fps(self.vfc.fps).set_audio(self.vfc.audio)
        clip.write_videofile(self.output_path)

def main():
    parser = argparse.ArgumentParser(description='Convert video to char-based video.')
    parser.add_argument('-i', type=str, help='the input path of source video, such as xx/xx/xx.mp4')
    parser.add_argument('-o', type=str, default=None, help='the output path of char-based video, default is input path')
    parser.add_argument('-fps', type=int, default=10, help='the frame per second of output video, default is 8')
    parser.add_argument('-cw', type=int, default=200, help='the chars width of chars in video, default is 80')
    parser.add_argument('-g', action='store_true', default=False, help='output the gray video, default is False')
    args = parser.parse_args()
    args.g = True
    converter = Converter(args.i, args.o, args.cw, args.fps, args.g)
    converter.generate()


if __name__ == '__main__':
    main()
