from os.path import join
import logging
import os,json

# -----------------------------------System Setting---------------------------------------
Market_Maker_Dir = os.path.dirname(os.path.abspath(__file__))

# Available levels: logging.(DEBUG|INFO|WARN|ERROR)
LOG_LEVEL = logging.INFO


# If any of these files (and this file) changes, reload the bot.ll
# WATCHED_FILES = [os.path.join(Market_Maker_Dir,'market_maker_inner.py'), os.path.join(Market_Maker_Dir,'gateio.py'),\
#                   os.path.join(Market_Maker_Dir,'settings.py')]

WATCHED_FILES = []



DryRun=True
# -----------------------------------LocalPriceData  Setting---------------------------------------




class Setting():
    def __init__(self,setting_dic):

        self.setting_dic=setting_dic

    def __getattr__(self, item):

        return self.setting_dic[item]

with open("./settings.json","r",encoding="UTF-8") as f:
    setting_dic=json.load(f)
    print(setting_dic)


settings=Setting(setting_dic)


settings.Market_Maker_Dir= Market_Maker_Dir
settings.LOG_LEVEL=LOG_LEVEL
settings.WATCHED_FILES=WATCHED_FILES
settings.DryRun=DryRun