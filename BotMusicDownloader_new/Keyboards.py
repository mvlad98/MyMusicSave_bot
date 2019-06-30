import codecs

from telebot import types
import configparser

class Keyboard:
    def __init__(self):
        self.conf=configparser.ConfigParser()
        self.conf.read_file(codecs.open('conf.ini','r','utf8'))

    def MainKeyboard(self,language):
        data={}
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)

        keyboard.row(f"{self.conf.get(f'Language {language}','language_key')}")
        #keyboard.row(f"{self.conf.get(f'Language {language}','FAQ_key')}")
        #keyboard.row(f"{self.conf.get(f'Language {language}','donate_key')}")

        data['text']=f"{self.conf.get(f'Language {language}','start')}"
        data['keyboard']=keyboard

        return data

    def SearchResult(self,music_list,start,end,lang,without_url=False):

        data = {}

        exept_start=start
        exept_end=end
        text=""

        data['send']=True
        try:
            while start<end:
                text=f"{text}[{start+1}]   <b>{music_list[start]['name']}</b>    <i>{music_list[start]['time']}</i>\n<a href='{music_list[start]['download']}'>{self.conf.get(f'Language {lang.upper()}','download')}</a>\n"
                start=start+1
        except Exception as e:
            print(f"Exeption in Keyboard -> SearchResult ---> {e}\n")
            if text=="":
                data['send']=False

        if without_url==True:
            start=exept_start
            end=exept_end
            text=""
            try:
                while start < end:
                    text = f"{text}[{start + 1}]   <b>{music_list[start]['name']}</b>    <i>{music_list[start]['time']}</i>\n\n"
                    start = start + 1
            except Exception as e:
                print(f"Exeption in Keyboard -> SearchResult ---> {e}\n")


        data['text']=f"{self.conf.get(f'Language {lang.upper()}','count')}    <b>{len(music_list)}</b>\n{text}\n{self.conf.get(f'Language {lang.upper()}','tip1')}"

        keyboard=types.InlineKeyboardMarkup()
        next=types.InlineKeyboardButton(text='->',callback_data='->')
        get=types.InlineKeyboardButton(text='GET',callback_data='get')
        prev = types.InlineKeyboardButton(text='<-', callback_data='<-')
        keyboard.add(prev,get,next)

        data['keyboard']=keyboard
        return  data


    def LanguageKeyboard(self):
        keyboard=types.InlineKeyboardMarkup()
        languages=f"{self.conf.get('Languages','languages')}".split(' ')
        for lang in languages:
            keyboard.add(types.InlineKeyboardButton(text=lang, callback_data=f"set_language {lang}"))
        return keyboard


    def UrlDownload(self,url,text):
        keyboard = types.InlineKeyboardMarkup()
        download_url = types.InlineKeyboardButton(text=text, url=url)
        keyboard.add(download_url)
        return keyboard





