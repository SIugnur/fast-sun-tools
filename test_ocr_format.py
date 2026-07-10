"""测试PaddleOCR返回格式"""
from PIL import Image
import numpy as np
from paddleocr import PaddleOCR

# 初始化OCR
ocr = PaddleOCR(
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=False,
    lang='ch',
)

# 创建一个简单的测试图片
test_img = Image.new('RGB', (200, 50), color='white')

# 模拟文字区域（添加一些黑色像素模拟文字）
for x in range(20, 180):
    for y in range(15, 35):
        test_img.putpixel((x, y), (0, 0, 0))

img_array = np.array(test_img)

# 测试OCR
result = ocr.ocr(img_array)

print("返回结果类型:", type(result))
print("返回结果内容:")
print(result)
print("\n")

# 尝试不同的解析方式
if result:
    print("Result[0] 类型:", type(result[0]) if len(result) > 0 else "N/A")
    if result and len(result) > 0:
        print("Result[0]:", result[0])
        if len(result[0]) > 0:
            print("Result[0][0]:", result[0][0])
            if len(result[0][0]) >= 2:
                print("Result[0][0][1]:", result[0][0][1])
