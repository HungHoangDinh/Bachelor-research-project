import fitz
from PIL import Image
import io
import base64
from io import BytesIO
import requests
import time
import re
import os
from dotenv import load_dotenv
from openai import OpenAI
load_dotenv()


class ParseHandler():
    def __call__(self):
        self.prompt_medical = """Bạn là một trợ lý AI chuyên xử lý hình ảnh chứa nội dung y tế. Nhiệm vụ của bạn là trích xuất và chuyển nội dung từ hình ảnh thành định dạng Markdown theo các quy tắc sau:
            1. Dùng `#` cho **chủ đề chính** (ví dụ: tên sách y khoa, tên bệnh, chuyên ngành y).
            2. Dùng `##` cho **phần** (ví dụ: "Chương 1", "Phần Lâm sàng", "Mục 3").
            3. Dùng `###` cho **tiểu mục** (ví dụ: "Triệu chứng", "Chẩn đoán", "Điều trị", "Cận lâm sàng").
            4. Dùng `####` cho **điểm cụ thể** (ví dụ: "Bước 1", "Chỉ định", "Phác đồ A").
            5. Dùng `-` cho **danh sách không thứ tự** và `1.`, `2.`, `3.` cho **danh sách có thứ tự**.
            6. Nếu có công thức hoặc biểu thức y học (ví dụ: công thức tính chỉ số BMI, liều thuốc), hãy trình bày bằng cú pháp LaTeX trong `$$ ... $$`.
            7. Nếu có bảng (table), hãy định dạng bằng Markdown, giữ nguyên nội dung đúng ô tương ứng.
            8. Chỉ trả về nội dung Markdown, không thêm giải thích hay mô tả gì khác.
            9. Không thêm ```markdown\n vào đầu câu trả lời.
            """
        self.api_key=os.environ.get("OPENAI_API_KEY")
        self.client= OpenAI(api_key=self.api_key)
    def pdf_to_images(self, file_stream, zoom_x=2.0, zoom_y=2.0):
        pdf_document = fitz.open(stream=file_stream, filetype="pdf")
        images = []
        for page_num in range(len(pdf_document)):
            page = pdf_document.load_page(page_num)
            mat = fitz.Matrix(zoom_x, zoom_y)
            pix = page.get_pixmap(matrix=mat)
            img = Image.open(io.BytesIO(pix.tobytes("png")))
            images.append(img)
        image_base64s = []

        for image in images:
            buffered = BytesIO()
            image.save(buffered, format="PNG")
            image_bytes = buffered.getvalue()
            image_base64s.append(base64.b64encode(image_bytes).decode("utf-8"))
        print("số trang: ",len(image_base64s))
        return image_base64s

    def parse_pdf(self, image_base64s, file_name):
        content=""
        for i in range(0, len(image_base64s)):
            messages=[
                    {
                        "role": "system",
                        "content": [
                            {
                                "type": "text",
                                "text": self.prompt_medical
                            },
                        ]
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Transcribe the content from this image into markdown format"
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_base64s[i]}"
                                }
                            }
                        ]
                    }
                ]

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                stream=False
            )
            content+="\n"
            content+=response

            print(content)
        return content