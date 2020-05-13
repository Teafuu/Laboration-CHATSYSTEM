import commands

print(commands.commands)

for k, v in commands.commands.items():
    print(k, v)

print('/w' in commands.commands)