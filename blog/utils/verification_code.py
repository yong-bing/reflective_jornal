import random
from io import BytesIO

from PIL import Image, ImageDraw, ImageFont


def create_code(request):
    img = Image.new('RGB', (120, 40), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype('blog/static/blog/fonts/kumo.ttf', 40)
    code = ''
    for i in range(4):
        random_num = str(random.randint(0, 9))
        random_lower = chr(random.randint(97, 122))
        random_upper = chr(random.randint(65, 90))
        random_char = random.choice([random_num, random_lower, random_upper])
        draw.text((i * 30 + random.randint(0, 10), 0), random_char, (0, 0, 0), font=font)
        code += random_char
    # 将验证码保存到session中
    request.session['code'] = code
    # 生成干扰点
    for i in range(100):
        draw.point((random.randint(0, 270), random.randint(0, 40)), fill=(0, 0, 0))
    # 生成干扰线
    for i in range(5):
        draw.line((random.randint(0, 270), random.randint(0, 40), random.randint(0, 270), random.randint(0, 40)),
                  fill=(0, 0, 0))

    io_obj = BytesIO()
    img.save(io_obj, 'png')
    request.session['verification_code'] = code

    return io_obj.getvalue()
