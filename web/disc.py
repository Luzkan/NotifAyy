import discord
import time
import requests
import json

client = discord.Client()

botToken = ''.join(['N','z','E','w','M','T','U','1','M','T','U','4','N','T','I',
            'w','M','j','A','x','M','j','M','5','.','X','t','z','p','Y',
            'A','.','K','R','l','X','w','L','i','A','n','a','4','z','y',
            's','C','j','b','T','q','j','w','y','t','f','E','U','I'])
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
            response = requests.get(url + '/changes').json()
            if response['discid'] != -1:
                for member in members:
                    if member == client.user:
                        continue

                    if response['discid'] == member.id and response['change'] is not None:
                        print(response)
                        await member.create_dm()
                        await member.dm_channel.send(
                            'Recent changes: ' + response['change']
                        )
            # '''
            # for member in members:
            #     if member == client.user:
            #         continue
            #     response = requests.get(url + '/changes', params={'discordId': member.id}).json()
            #     if response != {}:
            #         print(response)
            #         if response['change'] is not None:
            #             await member.create_dm()
            #             await member.dm_channel.send(
            #                 'Recent changes: ' + response['change']
            #             )
            # '''
            else:
                print('Empty response')

        except requests.exceptions.RequestException as err:
            print(err)

        except TypeError as err:
            print(err)

        time.sleep(10)


client.run(botToken)

