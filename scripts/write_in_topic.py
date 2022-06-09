import json

from src.event_utls.producer import Producer
from src.service_iface.message import Headers

producer = Producer()

producer.async_produce('test', json.dumps({'data': [i for i in range(1000000)]}), Headers('write_in_topic'))
