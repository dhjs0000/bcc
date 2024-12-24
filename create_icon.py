from PIL import Image, ImageDraw, ImageFont

def create_icon():
    # 创建一个 256x256 的图像
    size = 256
    image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    
    # 绘制圆形背景
    circle_color = (79, 70, 229)  # 主题色 --primary-color
    draw.ellipse([20, 20, size-20, size-20], fill=circle_color)
    
    # 添加文字
    try:
        font = ImageFont.truetype("arial.ttf", 120)
    except:
        font = ImageFont.load_default()
        
    # 绘制 "BCC" 文字
    text = "BCC"
    text_color = (255, 255, 255)  # 白色
    
    # 计算文字位置使其居中
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    x = (size - text_width) // 2
    y = (size - text_height) // 2
    
    draw.text((x, y), text, font=font, fill=text_color)
    
    # 保存为 ICO 文件
    image.save('docs/assets/bcc.ico', format='ICO', sizes=[(256, 256)])

if __name__ == '__main__':
    create_icon() 