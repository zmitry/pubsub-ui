from google.cloud import pubsub_v1
from google.api_core import retry
from typing import List, Dict, Optional


class PubSubClient:
    def __init__(self, emulator_host: str = "localhost:8681"):
        """Initialize PubSub client with emulator settings."""
        self.emulator_host = emulator_host
        import os
        os.environ["PUBSUB_EMULATOR_HOST"] = emulator_host
        
        self.publisher = pubsub_v1.PublisherClient(
            credentials=None,
            client_options={"api_endpoint": f"http://{emulator_host}"}
        )
        self.subscriber = pubsub_v1.SubscriberClient(
            credentials=None,
            client_options={"api_endpoint": f"http://{emulator_host}"}
        )

    def create_topic(self, project_id: str, topic_id: str) -> str:
        """Create a new topic."""
        topic_path = self.publisher.topic_path(project_id, topic_id)
        self.publisher.create_topic(request={"name": topic_path})
        return topic_id

    def list_topics(self, project_id: str) -> List[str]:
        """List all topics in a project."""
        project_path = f"projects/{project_id}"
        topics = self.publisher.list_topics(request={"project": project_path})
        return [
            topic.name.split('/')[-1] 
            for topic in topics
        ]

    def create_subscription(
        self, project_id: str, subscription_id: str, topic_path: str
    ) -> str:
        """Create a new subscription to a topic."""
        self.subscriber.create_subscription(
            request={"name": subscription_id, "topic": topic_path}
        )
        return subscription_id

    def list_subscriptions(self, project_id: str) -> List[str]:
        """List all subscriptions in a project."""
        project_path = f"projects/{project_id}"
        subscriptions = self.subscriber.list_subscriptions(
            request={"project": project_path}
        )
        return [
            sub.name.split('/')[-1] 
            for sub in subscriptions
        ]

    def publish_message(
        self, 
        topic_path: str, 
        message: str,
        attributes: Optional[Dict[str, str]] = None
    ) -> str:
        """Publish a message to a topic."""
        data = message.encode("utf-8")
        future = self.publisher.publish(topic_path, data, **attributes or {})
        return future.result()

    def pull_messages(
        self, subscription_path: str, max_messages: int = 100
    ) -> List[Dict]:
        """Pull all available messages from a subscription."""
        all_messages = []
        
        while True:
            response = self.subscriber.pull(
                request={
                    "subscription": subscription_path,
                    "max_messages": max_messages,
                    "return_immediately": True
                },
                retry=retry.Retry(deadline=10),
            )
            
            if not response.received_messages:
                break
            
            ack_ids = []
            for msg in response.received_messages:
                all_messages.append({
                    "message_id": msg.message.message_id,
                    "data": msg.message.data.decode("utf-8"),
                    "attributes": dict(msg.message.attributes),
                    "publish_time": msg.message.publish_time.isoformat(),
                })
                ack_ids.append(msg.ack_id)

            if ack_ids:
                self.subscriber.acknowledge(
                    request={
                        "subscription": subscription_path,
                        "ack_ids": ack_ids,
                    }
                )

        return all_messages

    def delete_subscription(self, subscription_path: str) -> None:
        """Delete a subscription."""
        self.subscriber.delete_subscription(
            request={"subscription": subscription_path}
        )

    def delete_topic(self, topic_path: str) -> None:
        """Delete a topic."""
        self.publisher.delete_topic(request={"topic": topic_path})
