import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Flatten, Conv2D, Dropout, MaxPooling2D
# Helper libraries
import numpy as np
import os
from configx import cfx
from pathlib import Path


fashion_mnist = keras.datasets.fashion_mnist
(train_images, train_labels), (test_images, test_labels) = fashion_mnist.load_data()

# scale the values to 0.0 to 1.0
train_images = train_images / 255.0
test_images = test_images / 255.0

# reshape for feeding into the model
train_images = train_images.reshape(train_images.shape[0], cfx.IMG_ROWS, cfx.IMG_COLS, 1)
test_images = test_images.reshape(test_images.shape[0], cfx.IMG_ROWS, cfx.IMG_COLS, 1)

class_names = ['T-shirt/top', 'Trouser', 'Pullover', 'Dress', 'Coat',
               'Sandal', 'Shirt', 'Sneaker', 'Bag', 'Ankle boot']

model = keras.Sequential([
  keras.layers.Conv2D(filters=32, input_shape=(cfx.IMG_ROWS, cfx.IMG_COLS, 1), kernel_size=3, 
                       activation='relu', kernel_initializer='he_normal'),
  keras.layers.MaxPooling2D(pool_size=(2,2)),
  keras.layers.Dropout(0.25),
  keras.layers.Conv2D(128, (3,3), activation="relu"),
  keras.layers.Flatten(),
  keras.layers.Dense(128, activation='relu'),
# Add dropouts to the model
  keras.layers.Dropout(0.3),
  keras.layers.Dense(cfx.NUM_CLASSES, activation='softmax')
])
model.summary()

testing = False
epochs = 5

model.compile(optimizer='adam', 
              loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=False),
              metrics=[keras.metrics.SparseCategoricalAccuracy()])
model.fit(train_images, train_labels, epochs=epochs)

test_loss, test_acc = model.evaluate(test_images, test_labels)
print('\nTest accuracy: {}'.format(test_acc))

# Save the model
export_path = Path.cwd() / "model"

tf.keras.models.save_model(
    model,
    export_path,
    overwrite=True,
    include_optimizer=True,
    save_format=None,
    signatures=None,
    options=None
)