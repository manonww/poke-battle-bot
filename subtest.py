import subprocess
team =  subprocess.check_output(f"pokemon-showdown generate-team gen7anythinggoes", shell=False)
print(team)