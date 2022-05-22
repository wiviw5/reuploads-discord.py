from datetime import datetime
import os
from configparser import ConfigParser

config = ConfigParser()
keyFile = "config.txt"
botSettings = "botSettings"
botKey = 'botkey'
mainGuildID = 'mainguild'
defaultChannelID = 'defaultchannel'
deletePermsRoleID = 'deletepermsrole'
viewPermsRoleID = 'viewpermsrole'
adminPermsRoleID = 'adminpermsrole'
ownerID = 'ownerid'


def getTime():
    now = datetime.now()
    currentTime = now.strftime("%m/%d/%y | %H:%M:%S")
    return currentTime


def checkAndSetupConfigFile():
    if not os.path.exists(keyFile):
        print(f"First Time setup, Creating {keyFile}")
        open(keyFile, "x")
        config.read(keyFile)
        config.add_section(botSettings)
        config.set(botSettings, botKey, "Place Discord Bot Key Here.")
        config.set(botSettings, mainGuildID, "Place Guild ID Here.")
        config.set(botSettings, defaultChannelID, "Place Default Channel ID Here.")
        config.set(botSettings, deletePermsRoleID, "Place Delete Perms Role ID Here.")
        config.set(botSettings, viewPermsRoleID, "Place View Perms Role ID Here.")
        config.set(botSettings, adminPermsRoleID, "Place Admin Perms Role ID Here.")
        config.set(botSettings, ownerID, "Place Owner ID Here.")
        with open(keyFile, 'w') as f:
            config.write(f)
        print(f"Please Update {keyFile} with associated Settings listed in file.")
        exit()


def getBotKey():
    config.read(keyFile)
    return config.get(botSettings, botKey)


def getMainGuildID():
    config.read(keyFile)
    return config.get(botSettings, mainGuildID)


def getDefaultChannelID():
    config.read(keyFile)
    return config.get(botSettings, defaultChannelID)


def getDeletePermsRoleID():
    config.read(keyFile)
    return config.get(botSettings, deletePermsRoleID)


def getViewPermsRoleID():
    config.read(keyFile)
    return config.get(botSettings, viewPermsRoleID)


def getAdminPermsRoleID():
    config.read(keyFile)
    return config.get(botSettings, adminPermsRoleID)


def getOwnerID():
    config.read(keyFile)
    return config.get(botSettings, ownerID)
