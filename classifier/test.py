# import tensorflow as tf
# from tensorflow import keras
# Helper libraries
import numpy as np
import pandas as pd
import os
from configx import cfx
from pathlib import Path
import requests
import json

# fashion_mnist = keras.datasets.fashion_mnist
# (train_images, train_labels), (test_images, test_labels) = fashion_mnist.load_data()

class_names = ['T-shirt/top', 'Trouser', 'Pullover', 'Dress', 'Coat',
               'Sandal', 'Shirt', 'Sneaker', 'Bag', 'Ankle boot']
# test_images = test_images / 255.0

# test_images = test_images.reshape(test_images.shape[0], cfx.IMG_ROWS, cfx.IMG_COLS, 1)

# test_images = test_images.tolist()
test_images = pd.read_csv(r"C:\Users\mohdg\Desktop\vector.ai\classifier\fashion-mnist_test.csv")
test_images = test_images.drop("label", axis=1)

test_images = test_images.to_numpy()
test_images = test_images /255.0
test_images = test_images.reshape(
        test_images.shape[0], cfx.IMG_ROWS, cfx.IMG_COLS, 1)
test_images = test_images.tolist()


print(test_images[4])
data = json.dumps({
    "inputs": [test_images[10]]
})
response = requests.post("http://localhost:8501/v1/models/fashion_mnist:predict", data=data)
# print(response.json())


print(response.json()["outputs"][0])
print(class_names[np.argmax(response.json()["outputs"][0])])