from loguru import logger 
import asyncio
import time
import multiprocessing as mp
async def task():
    logger.info("task started")
    await asyncio.sleep(2)
    logger.info("task_ended")

async def main_multiprocess_task(i:int=2):
    logger.info("running mainloop")
    await task()
    return i

def main(iterrations:int = 5, n_teams:int = 100, top_n:int = 10):
    logger.info("Get started")
    
    with mp.Pool() as pool:
        async_result = pool.apply_async(( main_multiprocess_task))
        results = async_result.get()
        
        logger.info("awaiting results")
        for result in results:
        # report the result
            print(f'Got: {result}')
        logger.info(result)

if __name__ == "__main__":
    main()