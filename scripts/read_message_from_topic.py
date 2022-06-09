from src.event_utls.consumer import consume


for msg in consume(['test'], 'test'):
    print(msg.value())
