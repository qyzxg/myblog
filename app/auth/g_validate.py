#!/usr/bin/python
# -*- coding:utf-8 -*-

import random
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from string import ascii_letters
import platform

_str = ascii_letters
_nums = '0123456789'

chars = ''.join((_str, _nums))
sys_tem = platform.system()
if sys_tem == 'Linux':
    default_font = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
else:
    default_font = "../static/fonts/arialbd.ttf"


def generate_verify_image(size=(110, 39),
                          chars=chars,
                          img_type='gif',
                          mode='RGB',
                          bg_color=(255, 255, 255),
                          fg_color=(212, 193, 175),
                          font_size=25,
                          font_type=default_font,
                          length=4,
                          draw_lines=True,
                          n_line=(3, 5),
                          draw_dotts=True,
                          dotts_chance=2,
                          save_img=False):
    """
    生成验证码图片
    :param size: 图片的大小，格式（宽，高），默认为(120, 30)
    :param chars: 允许的字符集合，格式字符串
    :param img_type: 图片保存的格式，默认为GIF，可选的为GIF，JPEG，TIFF，PNG
    :param mode: 图片模式，默认为RGB
    :param bg_color: 背景颜色，默认为白色
    :param fg_color: 前景色，验证码字符颜色，默认为蓝色#0000FF
    :param font_size: 验证码字体大小
    :param font_type: 验证码字体，默认为 DejaVuSans.ttf
    :param length: 验证码字符个数
    :param draw_lines: 是否划干扰线
    :param n_line: 干扰线的条数范围，格式元组，默认为(1, 2)，只有draw_lines为True时有效
    :param draw_dotts: 是否画干扰点
    :param dotts_chance: 干扰点出现的概率，大小范围[0, 100]
    :param save_img: 是否保存为图片
    :return: [0]: 验证码字节流, [1]: 验证码图片中的字符串
    """
    width, height = size
    img = Image.new(mode, size, bg_color)
    draw = ImageDraw.Draw(img)

    def get_strs():
        """生成随机字符"""
        return random.sample(chars, length)

    def create_lines():
        """生成干扰线"""
        line_num = random.randint(*n_line)
        for i in range(line_num):
            begin = (random.randint(0, size[0]), random.randint(0, size[1]))
            end = (random.randint(0, size[0]), random.randint(0, size[1]))
            draw.line([begin, end], fill=(255, 0, 0), width=3)

    def create_dotts():
        """生成干扰点"""
        chance = min(100, max(0, int(dotts_chance)))  # 大小限制在[0, 100]
        for w in range(width):
            for h in range(height):
                tmp = random.randint(0, 100)
                if tmp > 100 - chance:
                    draw.point((w, h), fill=(0, 0, 0))

    def create_strs():
        c_chars = get_strs()
        strs = '  %s ' % (''.join(c_chars))
        font = ImageFont.truetype(font_type, font_size)
        draw.text((0, 0), strs, font=font, fill=fg_color)
        return ''.join(c_chars)

    if draw_lines:
        create_lines()
    if draw_dotts:
        create_dotts()
    code_str = create_strs()

    params = [1 - float(random.randint(1, 2)) / 100, 0, 0, 0,
              1 - float(random.randint(1, 10)) / 100,
              float(random.randint(1, 2)) / 200,
              0.001,
              float(random.randint(1, 2)) / 300
              ]
    img = img.transform(size, Image.PERSPECTIVE, params)  # 创建扭曲

    img = img.filter(ImageFilter.EDGE_ENHANCE_MORE)  # 滤镜，边界加强（阈值更大）
    return img, code_str

# if __name__ == '__main__':
#     img_str, code_str = generate_verify_image()
#     print(img_str, code_str)
