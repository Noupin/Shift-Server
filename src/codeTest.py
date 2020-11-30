from PIL import Image
import cv2
import io
import base64
import numpy as np

def encodeRawImage(imgArr):
    """
    Takes in an image array then encodes it as a
    bytestring to be streamed through JSON to JavaScript
    """

    resize = cv2.resize(imgArr, (1024, 1024))
    resize = resize*255.
    img = resize.astype(np.uint8)
    img = Image.fromarray(img).convert("RGB")
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue())
    imgEnc = img_str.decode('utf-8')
    return imgEnc

with open("binImg.txt", "w") as fil:
    img = cv2.cvtColor(cv2.imread(r"C:\Coding\Python\ML\Shift\icon.png"), cv2.COLOR_BGR2RGB).astype('float32')/255.
    fil.write(encodeRawImage(img))