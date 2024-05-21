from PIL import Image, ImageDraw, ImageFilter
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
    result.rotate(45, resample=Image.Resampling.BILINEAR)
    result = result.filter(ImageFilter.SMOOTH)
    # result.rotate(45,resample=Image.Resampling.BICUBIC)
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


def draw_smooth_rounded_rectangle(draw, xy, corner_radius, fill=None, iterations=2):
    x1, y1, x2, y2 = xy
    for i in range(iterations):
        offset = i + 1
        color = (0, 0, 0, 255) if i == iterations - 1 else (0, 0, 0, int(255 * ((iterations - i) / iterations)))  # 透明度渐变模拟抗锯齿
        draw.rounded_rectangle((x1 + offset, y1 + offset, x2 - offset, y2 - offset), corner_radius, fill=color, width=offset)


def round_corners(image_path, radius):
    """给图像添加圆角并减少锯齿"""
    with Image.open(image_path) as image:
        mask = Image.new('RGBA', image.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(mask)

        draw_smooth_rounded_rectangle(draw, (0, 0, image.width, image.height), radius)
        mask.rotate(45, resample=Image.Resampling.BILINEAR)
        mask = mask.filter(ImageFilter.SMOOTH)
        result = Image.composite(image.convert("RGBA"), Image.new("RGBA", image.size, (0, 0, 0, 0)), mask)
        result.rotate(45, resample=Image.Resampling.BILINEAR)
        result = result.filter(ImageFilter.SMOOTH)
        # 将结果保存到BytesIO对象
        img_byte_arr = BytesIO()
        result.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        return img_byte_arr


# def round_corners(img_bytes_io, radii):
#     # 从BytesIO加载图像并转换为RGBA模式
#     img = Image.open(img_bytes_io).convert("RGBA")
#
#     # 画圆并应用轻微模糊以优化抗锯齿效果
#     circle = Image.new('L', (radii * 2, radii * 2), 0)  # 图像略大以容纳模糊效果
#     draw = ImageDraw.Draw(circle)
#     draw.ellipse((0, 0, radii * 2, radii * 2), fill=255)
#     # circle = circle.filter(ImageFilter.EDGE_ENHANCE)  # 应用模糊滤镜优化边缘
#
#
#     w, h = img.size
#
#     # 创建Alpha层并应用抗锯齿圆角，同时优化边缘透明度
#     # 直接使用裁剪的圆角，但需要进一步处理以去除模糊边缘的半透明像素
#     alpha = Image.new('L', img.size, 255)
#     alpha.paste(circle.crop((0, 0, radii, radii)), (0, 0))  # 左上角
#     alpha.paste(circle.crop((radii, 0, radii * 2, radii)), (w - radii, 0))  # 右上角
#     alpha.paste(circle.crop((radii, radii, radii * 2, radii * 2)), (w - radii, h - radii))  # 右下角
#     alpha.paste(circle.crop((0, radii, radii, radii * 2)), (0, h - radii))  # 左下角
#     # 通过mask参数精确粘贴，这样只有原始圆内的像素才会影响alpha通道
#     # 这将消除模糊边缘带来的半透明问题
#
#     # 应用Alpha层到原图
#     img.putalpha(alpha)  # 现在边缘应该是干净且透明的了
#
#     # 保存到新的BytesIO对象并返回
#     output_bytes_io = BytesIO()
#     img.save(output_bytes_io, format='PNG')  # 使用PNG格式以保留透明度和抗锯齿效果
#     output_bytes_io.seek(0)  # 将指针移回开始，以便读取
#
#     return output_bytes_io


# def round_corners(image_bytes, radius):
#     with Image.open(image_bytes) as original:
#         original = original.resize((original.height, original.height))
#         mask = Image.open('static/12345.png').resize((original.height, original.height))
#         img = Image.new('RGBA', mask.size, (0, 0, 0, 0))
#         # Save the image with transparency to BytesIO
#         img.paste(original, mask=mask)
#         # 将结果保存到BytesIO对象
#         img_byte_arr = BytesIO()
#         img.save(img_byte_arr, format='PNG')  # 以PNG格式保存，你可以根据需要更改格式
#         img_byte_arr.seek(0)  # 将指针移动到开头以便于读取
#         return img_byte_arr


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

# if __name__ == '__main__':
#     in_p = 'test2.jpg'
#     s_p = 'ava.jpg'
#     color_to_white(in_p, 'test_bw.png')  # need
#     # 圆角头像处理
#     source_img = s_p  # need
#     output_img_rounded = 'avatar_r.png'
#     round_corners(source_img, output_img_rounded, 60)
#     avatar_positions = origin_ava_positions('test_bw.png', )
#     resize_and_overlay(in_p, 'avatar_r.png', avatar_positions)
