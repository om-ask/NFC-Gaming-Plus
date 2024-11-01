import logging
import asyncio

from amqtt.client import MQTTClient, ClientException
from amqtt.mqtt.constants import QOS_2
from amqtt.session import ApplicationMessage

logger = logging.getLogger(__name__)


async def uptime_coro():
    client = MQTTClient()

    await client.connect('mqtt://192.168.0.195:1883')
    print("Connected")

    await client.subscribe([
        ('nfc/writer1', QOS_2)])

    try:
        for i in range(1, 100):
            message: ApplicationMessage = await client.deliver_message()
            packet = message.publish_packet
            print("%d:  %s => %s" % (
                i,
                packet.variable_header.topic_name,
                str(packet.payload.data)))

        await client.unsubscribe(['nfc/writer1'])
        await client.disconnect()

    except ClientException as ce:
        logger.error("Client exception: %s" % ce)


if __name__ == '__main__':
    formatter = "[%(asctime)s] %(name)s {%(filename)s:%(lineno)d} %(levelname)s - %(message)s"
    logging.basicConfig(level=logging.DEBUG, format=formatter)
    asyncio.get_event_loop().run_until_complete(uptime_coro())
