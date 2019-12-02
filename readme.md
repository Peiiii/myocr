### 1.测试data/imgs/yyzz下的图片
``` shell script
python3 main.py
```
### 2.使用示例
 ```python
from predict import Predictor,reciept
import cv2
P=Predictor()
img=cv2.imread('demo.jpg')
res=reciept.predict(P,img)
print(res)
```