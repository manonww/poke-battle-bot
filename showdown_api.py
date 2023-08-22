import asyncio
from loguru import logger
from config import Config

async def generate_random_team_showdown(battle_format:str = "gen1ou") ->str:
    ''' Generate a random team directly from showdown server '''
    #folder_path = r"C:\Users\diana\Documents\Python projects\pokemon\pokemon-showdown"
    folder_path = r"C:/Users/Robert/Downloads/Cheating is learning/pokemon-showdown"
    gen_node_command = f'node pokemon-showdown generate-team {battle_format}'
    val_node_command = f'node pokemon-showdown validate-team {battle_format} '
    
    while True:
        #generate team
        process = await asyncio.create_subprocess_shell(f'cd /d {folder_path} && {gen_node_command}',  stdout=asyncio.subprocess.PIPE)
        team, _ = await process.communicate()
        #check if team is valid
        val_process = await asyncio.create_subprocess_shell(
            f'cd /d {folder_path} && {val_node_command} ',
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        val_stdout, val_stderr = await val_process.communicate(input=team)
        #if valid return team
        if len(val_stderr) ==0:
            return team.decode()
        #else read error
        else:
            logger.info(val_stderr.decode())

async def validate_team(team:str, battle_format:str) ->bool:
    ''' Validate team with pokemon showdown server to ensure its allowed in format '''
    val_node_command = f'node pokemon-showdown validate-team {battle_format} '
    val_process = await asyncio.create_subprocess_shell(
            f'cd /d {Config.showdown_folder_path} && {val_node_command} ',
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
    val_stdout, val_stderr = await val_process.communicate(input=team.encode())
    #if valid return team
    if len(val_stderr) ==0:
        return True
    #else read error
    else:
        logger.info(team)
        logger.info(val_stderr.decode())
    
        return False
    

