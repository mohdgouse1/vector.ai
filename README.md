# Vector AI Assignment

## Part 1
Fashion MNIST Classifier using CNN
- The folder "classifier" contains the necessary files to train and configure the CNN model inputs and outputs.
- The config.json file should be used to define some of the basic features of the dataset like IMG_ROWS, COLS etc.
- The "models" folder contains are trained FASHION MNIST classifier model which can be used with Tensorflow Serving.

## Part 2 and Part3

Unified API For Apache Kafka and Google Pub Sub
- config.json must be configured with necessary details before using the unified api.
- Modify the docker-compose file to mount the volume if data persistence is required and Tensorflow Model path and run "docker-compose up" command to start:
	* Zookeeper
	* Kafka
	* Tensorflow Serving
	* CMAK- Kafka Manager

- Streamer is the unified API which have very similar adn can be initilaized like below:
	```sh
	StreamConnect = Streamer(app="pubsub").choose()
	or 
	StreamConnect = Streamer(app="kafka").choose()
	```
- For pub and sub tasks:
	- Two topics have been created. fashion_mnist and fashion_mnist_ml. The producer and consumer can take two parameters, i.e. **"input"** and **"ml"**.
- 
	```sh
	await StreamConnect.pub(producer="input", data=data)
	or 
	await StreamConnect.pub(producer="ml", data=data)
	
	*****
	subscribed_result = await StreamConnect.sub(consumer="input")
	or 
	subscribed_result = await StreamConnect.sub(consumer="ml")
	```
- The fashionmnist test data file available in the classifier file. It can loaded as dentoed below or in the file "test_api.py"
	 ```sh
	test_images = pd.read_csv("fashion-mnist_test.csv")
	
	test_images = test_images.drop("label", axis=1)
	test_images = test_images.to_numpy()
	test_images = test_images / 255.0
	test_images = test_images.reshape(
	test_images.shape[0], cfx.classifier.IMG_ROWS, cfx.classifier.IMG_COLS, 1)
	test_images = test_images.tolist()
	```
- The publish and subscribe methods are a combination of pub and sub methods to perform the streaming tasks as required for the assignment.
	```sh
	async  def  main():
		data = {
			"id": 28,
			"test_image": test_images[28]
		}
		await  StreamConnect.publish(data=data)
		print(await  StreamConnect.subscribe())

	 
	if  __name__ == '__main__':
		asyncio.run(main())
	```
- The output of the above code would be like the following:
	```sh
	[{'id': 28, 'ml_response': 'Coat'}]
	```
