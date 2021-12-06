import asyncio
import sys

from kafka.producer.future import FutureRecordMetadata
from configx import cfx
from kafka import KafkaConsumer, KafkaProducer
from kafka.admin import KafkaAdminClient, NewTopic
from google.cloud import pubsub
import os
from concurrent.futures import TimeoutError
import json
import numpy as np
import httpx


def json_serializer(data):
    return json.dumps(data).encode("utf-8")


def json_deserializer(data):
    return json.loads(data)

# Implementing Kafka Class


async def get_classification(data):
    async with httpx.AsyncClient() as client:
        send_data = json.dumps({
            "inputs": [data["test_image"]]
        })
        ml_response = await client.post(cfx.ml_server.url, data=send_data)

    if ml_response.status_code == 400:
        raise Exception

    final_data = {
        "id": data["id"],
        "ml_response": cfx.classifier.class_names[np.argmax(ml_response.json()["outputs"][0])]
    }

    return final_data


class KafkaAPI:
    def __init__(self):
        self.topic = cfx.kafka.topic
        self.bootstrap_servers = cfx.kafka.bootstrap
        try:
            self.producer = KafkaProducer(bootstrap_servers=self.bootstrap_servers,
                                          value_serializer=json_serializer,
                                          acks=1)
            # self.producer_ml = KafkaProducer(bootstrap_servers=self.bootstrap_servers,
            #                               value_serializer=json_serializer, key_serializer=json_serializer)

            self.admin = KafkaAdminClient(
                bootstrap_servers=self.bootstrap_servers)
            try:
                self.admin.create_topics(new_topics=[NewTopic(
                    name=self.topic, num_partitions=cfx.kafka.num_partitions, replication_factor=cfx.kafka.replication_factor)])
                self.admin.create_topics(new_topics=[NewTopic(
                    name=self.topic+"_ml", num_partitions=cfx.kafka.num_partitions, replication_factor=cfx.kafka.replication_factor)])
            except:
                pass

            self.consumer = KafkaConsumer(self.topic, bootstrap_servers=self.bootstrap_servers,
                                          group_id=cfx.kafka.consumer_group,
                                          auto_offset_reset='earliest',
                                          # max_poll_records=1,
                                          consumer_timeout_ms=5000
                                          )

            # self.consumer.subscribe(topics=[self.topic])

            self.consumer_ml = KafkaConsumer(self.topic+"_ml", bootstrap_servers=self.bootstrap_servers,
                                             group_id=cfx.kafka.consumer_group+"_ml",
                                             auto_offset_reset='earliest',
                                             #  max_poll_records =1,
                                             consumer_timeout_ms=5000
                                             )

            # self.consumer_ml.subscribe(topics=[self.topic+ "_ml"])
        except Exception as e:
            sys.exit(f"error occured: {e}")

    def __str__(self) -> str:
        return f"Kafka broker connection alive: {self.producer.bootstrap_connected()}"

    async def pub(self, producer, data):
        try:
            if producer == "input":
                self.producer.send(self.topic, data)
                self.producer.flush()

            elif producer == "ml":
                self.producer.send(str(self.topic + "_ml"), data)
                self.producer.flush()

        except Exception as e:
            sys.exit(f"error occured:{e}")

    async def sub(self, consumer):
        res = []
        if consumer == "input":
            for msg in self.consumer:
                # print(json.loads(msg.value))
                res.append(json.loads(msg.value))
        elif consumer == "ml":
            for msg in self.consumer_ml:
                # print(json.loads(msg.value))
                res.append(json.loads(msg.value))
        return res

    async def publish(self, data) -> None:
        await self.pub(producer="input", data=data)
        get_data = await self.sub(consumer="input")
        new_data = await get_classification(get_data[0])
        await self.pub(producer="ml", data=new_data)

    async def subscribe(self) -> list:
        retrieve_data = await self.sub(consumer="ml")
        return retrieve_data


class PubSubAPI:
    def __init__(self) -> None:
        self.topic = cfx.pubsub.topic
        self.topic_name = f"projects/{cfx.pubsub.project_id}/topics/{cfx.pubsub.topic}"
        self.topic_name_ml = f"projects/{cfx.pubsub.project_id}/topics/{cfx.pubsub.topic}_ml"
        self.subscription = cfx.pubsub.subscription
        self.subscription_path = f"projects/{cfx.pubsub.project_id}/subscriptions/{cfx.pubsub.subscription}"
        self.subscription_path_ml = f"projects/{cfx.pubsub.project_id}/subscriptions/{cfx.pubsub.subscription}_ml"
        self.auth_file = cfx.pubsub.auth_file
        self.project_id = cfx.pubsub.project_id

        try:
            self.auth()
            self.publisher = pubsub.PublisherClient()
            self.subscriber = pubsub.SubscriberClient()
            try:
                self.publisher.create_topic(name=self.topic_name)
                self.publisher.create_topic(name=self.topic_name_ml)
            except Exception:
                pass

        except Exception as e:
            sys.exit(f"error occured: {e}")

    def __str__(self) -> str:
        return f"Pubsub connection"

    def auth(self):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = self.auth_file

    async def pub(self, producer, data):
        try:
            if producer == "input":
                future = self.publisher.publish(
                    self.topic_name, json_serializer(data))
                return future.result()

            elif producer == "ml":
                future = self.publisher.publish(
                    self.topic_name_ml, json_serializer(data))
                return future.result()

        except Exception as e:
            sys.exit(f"error occured:{e}")

    async def sub(self, consumer):
        self.subscriber = pubsub.SubscriberClient()
        res = []
        if consumer == "input":
            sub_path = self.subscription_path
        elif consumer == "ml":
            sub_path = self.subscription_path_ml

        def callback(message):
            res.append(json.loads(message.data.decode()))
            message.ack()

        with self.subscriber as subscriber:
            future = subscriber.subscribe(sub_path, callback)
            with subscriber:
                try:
                    future.result(timeout=5)
                except Exception:
                    future.cancel()
        return res

    async def publish(self, data) -> None:
        await self.pub(producer="input", data=data)
        get_data = await self.sub(consumer="input")
        new_data = await get_classification(get_data[0])
        await self.pub(producer="ml", data=new_data)

    async def subscribe(self) -> list:
        retrieve_data = await self.sub(consumer="ml")
        return retrieve_data


class Streamer:
    def __init__(self, app) -> None:
        self.app = app

    def choose(self):
        if self.app == "kafka":
            return KafkaAPI()
        elif self.app == "pubsub":
            return PubSubAPI()
        else:
            return f"Invalid app selected"
