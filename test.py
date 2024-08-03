
 
imgPath = "C:/Users/pedro/OneDrive/Área de Trabalho/djiTIFF/bne.jpg"

from PIL import Image
image = Image.open(imgPath)
print(list(image.info.keys()))
print(image.applist)