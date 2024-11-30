import qrcode
import time

while True:
    img = qrcode.make(input())
    print(img)
    start = time.time()
    img.save("qr.png")
    print(time.time() - start)


