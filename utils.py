from PIL import Image, ImageDraw
import cv2
import streamlit as st
from io import BytesIO
import numpy as np


# 将背景色
def color_to_white(input_path, target_color=(237, 237, 237), tolerance=10):
    # 定义颜色相似度阈值
    img = Image.open(input_path).convert("RGB")
    width, height = img.size

    # 创建一个新图用于绘制遮罩
    mask = Image.new('L', (width, height), 0)
    draw = ImageDraw.Draw(mask)

    # 遍历图片像素，找到接近目标颜色的像素，并在遮罩上标记为白色（255）
    for x in range(width):
        for y in range(height):
            r, g, b = img.getpixel((x, y))
            if all(abs(c1 - c2) <= tolerance for c1, c2 in zip((r, g, b), target_color)):
                draw.point((x, y), fill=255)

    # 使用遮罩进行颜色替换
    result = Image.new('RGB', img.size)
    white = (255, 255, 255)
    black = (0, 0, 0)
    result.paste(white, (0, 0), mask)
    result.paste(black, (0, 0), mask=mask.point(lambda p: p == 0))
    # result.save("white_background.png")
    # 将结果保存到BytesIO对象
    img_byte_arr = BytesIO()
    result.save(img_byte_arr, format='PNG')  # 以PNG格式保存，你可以根据需要更改格式
    img_byte_arr.seek(0)  # 将指针移动到开头以便于读取

    return img_byte_arr


def origin_ava_positions(input):
    # 加载图片
    # 假设image_bytes_io是你的BytesIO对象，其中包含图像数据
    image_pil = Image.open(input)

    # 将PIL图像转换为OpenCV格式（注意颜色通道顺序的转换，PIL是RGB，而OpenCV通常是BGR）
    img_cv = cv2.cvtColor(np.array(image_pil), cv2.COLOR_RGB2BGR)
    # img_cv = cv2.imread(input_path)

    # 获取图片尺寸
    height, width = img_cv.shape[:2]

    # 计算去除顶部和底部10%后的有效高度范围
    top_bound = int(height * 0.10)
    bottom_bound = int(height * 0.90)

    # 计算左右30%区域的边界（基于有效高度范围）
    # left_bound = int(width * 0.15)
    left_bound = int(1)
    right_bound = int(width * 0.8)

    # 截取有效高度范围内的左右两侧30%的区域进行后续处理
    img_left_gray = cv2.cvtColor(img_cv[top_bound:bottom_bound, :left_bound], cv2.COLOR_BGR2GRAY)
    img_right_gray = cv2.cvtColor(img_cv[top_bound:bottom_bound, right_bound:], cv2.COLOR_BGR2GRAY)

    # 简单的二值化处理
    _, binary_left = cv2.threshold(img_left_gray, 127, 255, cv2.THRESH_BINARY_INV)
    _, binary_right = cv2.threshold(img_right_gray, 127, 255, cv2.THRESH_BINARY_INV)

    # 寻找轮廓
    contours_left, _ = cv2.findContours(binary_left, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours_right, _ = cv2.findContours(binary_right, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # 假设头像区域大小范围
    min_size = (80, 80)
    max_size = (200, 200)
    possible_avatars = []

    # 调整轮廓坐标以反映原始图片中的位置
    def adjust_contour(coord):
        return (coord[0], coord[1] + top_bound, coord[2], coord[3])

    # 处理左侧轮廓
    for contour in contours_left:
        x, y, w, h = cv2.boundingRect(contour)
        if min_size[0] < w < max_size[0] and min_size[1] < h < max_size[1]:
            possible_avatars.append(adjust_contour((x, y, w, h)))

    # 处理右侧轮廓并调整坐标
    for contour in contours_right:
        x, y, w, h = cv2.boundingRect(contour)
        x += right_bound  # 修正右侧轮廓的x坐标
        if min_size[0] < w < max_size[0] and min_size[1] < h < max_size[1]:
            possible_avatars.append(adjust_contour((x, y, w, h)))

    # 绘制识别到的可能头像区域
    for x, y, w, h in possible_avatars:
        cv2.rectangle(img_cv, (x, y), (x + w, y + h), (0, 255, 0), 2)
    # cv2.imwrite("white_background_rectangle.png", img_cv)
    return possible_avatars


def round_corners(image_path, radius):
    """给图像添加圆角"""
    with Image.open(image_path) as image:
        mask = Image.new('RGBA', image.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(mask)
        draw.rounded_rectangle((0, 0, image.width, image.height), radius, fill=(0, 0, 0, 255))
        result = Image.new('RGBA', image.size)
        result.paste(image, (0, 0), mask=mask)
        # 将结果保存到BytesIO对象
        img_byte_arr = BytesIO()
        result.save(img_byte_arr, format='PNG')  # 以PNG格式保存，你可以根据需要更改格式
        img_byte_arr.seek(0)  # 将指针移动到开头以便于读取
        return img_byte_arr


def resize_and_overlay(background_path, overlay_path, avatar_positions):
    """调整圆角头像尺寸并贴到背景图片上"""
    with Image.open(background_path) as bg_img, Image.open(overlay_path) as overlay_img:
        bg_w, bg_h = bg_img.size
        ol_w, ol_h = overlay_img.size

        combined = Image.new('RGBA', bg_img.size, (0, 0, 0, 0))
        combined.paste(bg_img, (0, 0))

        for x, y, w, h in avatar_positions:
            # # 计算目标尺寸，保持原始头像的宽高比
            # aspect_ratio = ol_w / ol_h
            # desired_w = w
            # desired_h = int(desired_w / aspect_ratio)
            # if desired_h > h:
            #     desired_h = h
            #     desired_w = int(desired_h * aspect_ratio)

            resized_overlay = overlay_img.resize((w, h))

            paste_x = x
            paste_y = y
            # paste_x = max(0, min(paste_x, bg_w - desired_w))
            # paste_y = max(0, min(paste_y, bg_h - desired_h))

            combined.paste(resized_overlay, (paste_x, paste_y), resized_overlay)
        st.session_state.good = True
        # 将结果保存到BytesIO对象
        img_byte_arr = BytesIO()
        combined.save(img_byte_arr, format='PNG')  # 以PNG格式保存，你可以根据需要更改格式
        img_byte_arr.seek(0)  # 将指针移动到开头以便于读取
        return img_byte_arr


if __name__ == '__main__':
    in_p = 'test2.jpg'
    s_p = 'ava.jpg'
    color_to_white(in_p, 'test_bw.png')  # need
    # 圆角头像处理
    source_img = s_p  # need
    output_img_rounded = 'avatar_r.png'
    round_corners(source_img, output_img_rounded, 60)
    avatar_positions = origin_ava_positions('test_bw.png', )
    resize_and_overlay(in_p, 'avatar_r.png', avatar_positions)
