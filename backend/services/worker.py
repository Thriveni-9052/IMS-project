import asyncio

async def worker(queue, processor, stores):

    while True:
        signal = await queue.get()

        retries = 3

        while retries > 0:
            try:

                # simulate DB failure
                raise Exception("Database Down")

                # process signal
                incident_id = processor(signal)

                stores["incident_store"].append(signal)

                print("Processed:", incident_id)

                break

            except Exception as e:
                print("DB DOWN RETRYING...", e)

                retries -= 1
                await asyncio.sleep(2)

        queue.task_done()
