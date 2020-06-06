import discord
import time
import requests
import json

client = discord.Client()

botToken = 'NzEwMTU1MTU4NTIwMjAxMjM5.XrwVmw.5tHKA4YGSu8krNaM29JJ_3Ns_TQ'
serverName = 'NotifAyy test server'
url = 'http://localhost:5000'

members = []


@client.event
async def on_ready():
    for guild in client.guilds:
        if guild.name == serverName:
            break

    print(f'Connected as: {client.user}, to server: {guild.name} id: {guild.id}')
    global members
    members = guild.members
    await changes()


@client.event
async def on_member_join(member):
    await member.create_dm()
    await member.dm_channel.send(
        f'Hi {member.name}, welcome to NotifAyy server!'
    )
    global members
    members.append(member)


async def changes():
    global members
    while True:
        try:
            for member in members:
                response = requests.get(url + '/changes', params={'discordId': member.id})
                if response is not None and response['change'] is not None:
                    await member.create_dm()
                    await member.dm_channel.send(
                        'Recent changes: ' + response['change']
                    )

                else:
                    print('Empty response')

        except requests.exceptions.RequestException as err:
            print(err)

        except TypeError:
            print('idk')

        time.sleep(15)


client.run(botToken)

