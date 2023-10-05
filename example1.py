"""
    Source: https://www.youtube.com/watch?v=Lk78xP6VMGA
"""
from loguru import logger
import multiprocessing
import asyncio

class MultiprocessingAsync(multiprocessing.Process):
    def __init__(self):
        super(MultiprocessingAsync, self).__init__()

    async def task(self, j):
        logger.info("task started")
        await asyncio.sleep(2)
        logger.info("task_ended")
        return j

    async def main_multiprocess_task(self, i: int = 10):
        logger.info("running mainloop")
        pending = set()
        for j in range(i):
            pending.add(asyncio.create_task(self.task(j)))

        while len(pending) > 0:
            done, pending = await asyncio.wait(pending, timeout=1)
            for done_task in done:
                print(await done_task)

    def run(self) -> None:
        asyncio.run(self.main_multiprocess_task())

if __name__ == '__main__':
    processes = [MultiprocessingAsync() for _ in range(2)]

    for p in processes:
        p.start()

    for p in processes:
        p.join()
