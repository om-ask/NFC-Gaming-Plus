from pipeline import PipeLine, Payload


async def process_logic_forever(pipeline: PipeLine):
    while True:
        # Get reading
        published_payload: Payload = await pipeline.get_reading()

        # TODO some custom quest logic
        published_payload.set_points(5)

        # Publish to processed queue
        await pipeline.add_processed_message(published_payload)
