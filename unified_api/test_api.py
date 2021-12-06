import asyncio
from api import KafkaAPI, PubSubAPI, Streamer
from configx import cfx
import pandas as pd



StreamConnect = Streamer(app="pubsub").choose()

# Getting an image to classify 
test_images = pd.read_csv(
    r"C:\Users\mohdg\Desktop\vector.ai\classifier\fashion-mnist_test.csv")
test_images = test_images.drop("label", axis=1)

test_images = test_images.to_numpy()
test_images = test_images / 255.0
test_images = test_images.reshape(
    test_images.shape[0], cfx.classifier.IMG_ROWS, cfx.classifier.IMG_COLS, 1)
test_images = test_images.tolist()


async def main():
    data = {
        "id": 28,
        "test_image": test_images[28]
    }

    await StreamConnect.publish(data=data)
    print(await StreamConnect.subscribe())


if __name__ == '__main__':
    asyncio.run(main())


