from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration

processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")

def generate_caption(raw_image: Image) -> str:
    inputs = processor(raw_image, return_tensors="pt")
    outputs = model.generate(**inputs)
    caption = processor.decode(outputs[0], skip_special_tokens=True)
    return caption

# Khởi động Gradio demo
import gradio as gr

demo = gr.Interface(
    fn=generate_caption,
    inputs=gr.Image(type="pil"),
    outputs="text",
    title="Image Caption Generator"
)

if __name__ == "__main__":
    demo.launch()

import requests

# Tải ảnh về
image_url = 'https://storage.googleapis.com/petbacker/images/blog/2017/dog-and-cat-cover.jpg'
image = Image.open(requests.get(image_url, stream=True).raw)

# Chạy generate_caption và in ảnh ra
caption = generate_caption(image)
# Output: "a cat and dog are looking over a white sign"
print(caption)