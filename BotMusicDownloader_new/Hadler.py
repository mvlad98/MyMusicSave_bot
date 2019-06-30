import codecs
from Keyboards import Keyboard
from DataBaseManager import DataBase
import configparser
import requests
from bs4 import BeautifulSoup
import youtube_dl
import os

class Handler:

    def __init__(self,bot):
        self.bot=bot
        self.db=DataBase()
        self.kb = Keyboard()
        self.conf = configparser.ConfigParser()
        self.conf.read_file(codecs.open('conf.ini', 'r', 'utf8'))
        self.start=-1
        self.end=-1
        self.music_list={}
        self.language='none'
        self.send=True

    def Restart(self):
        ids=self.db.GetAllUsersID()
        for id in ids:
            print(id)
            lang=(self.db.GetUserLanguage(id['id_user']))[0]['lang']
            data = self.kb.MainKeyboard(lang)
            self.bot.send_message(id['id_user'],f"{self.conf.get(f'Language {lang}','restart')}",reply_markup=data['keyboard'],parse_mode='html')


    def LanguageInit(self,id_user):
        try:
            self.language=(self.db.GetUserLanguage(id_user))[0]['lang']
        except:
            self.language='ENG'

    def Start(self,m):
        if self.db.CheckUserExsists(m.from_user.id)==False:
            self.db.AddUser(m.from_user.id,m.from_user.first_name,m.from_user.username)
            data = self.kb.MainKeyboard('ENG')
            self.bot.send_message(m.chat.id, f"{data['text']}",reply_markup=data['keyboard'], parse_mode='html')
        else:
            data = self.kb.MainKeyboard(f"{self.language}")
            self.bot.send_message(m.chat.id, f"{data['text']}",reply_markup=data['keyboard'],parse_mode='html')


    def Text(self,m):
        if m.text==self.conf.get(f"Language {self.language.upper()}",'language_key'):
            self.SetLanguage(m)
        elif m.text==self.conf.get(f"Language {self.language.upper()}",'FAQ_key'):
            pass
        elif m.text==self.conf.get(f"Language {self.language.upper()}",'donate_key'):
            pass
        elif '. https://www.shazam.com' in m.text:
            self.SearchMusicByShazam(m.text,m.chat.id)
        elif 'https://youtu.be' in m.text or 'https://www.youtube.com' in m.text:
            self.SendMusicByYouTube(m.text,m.chat.id)
        elif m.text[0]=='?' and len(m.text)>1:
            self.start=0
            self.end=10
            self.music_list=self.SearchMusicByQuery(m.text)
            self.SendMusicByQuery(self.start,self.end,m.chat.id,0,simple=True)



    def SearchMusicByQuery(self,text):
        res_send=[]
        search=text.replace('?','')
        query=f"https://music7s.cc/search.php?search={search}&count=300&sort=2"

        r = requests.get(query)
        soup = BeautifulSoup(r.content, 'html.parser')
        mydivs = soup.findAll("div", {"class": "row collection-item grey-text text-darken-4 item"})
        for block in mydivs:
            name = block.find('a', {'class': 'desc'})
            time = block.find('div', {'class': 'col m2'})
            url_download = block.find('a', {'class': 'download_link sp_notify_prompt'})
            res_send.append({'name': name.text, 'time': time.text, 'download': f"https://music7s.cc{url_download.attrs['href']}"})
        return res_send

    def SendMusicByQuery(self,start,end,id_user,id_message,simple=False):
        data=self.kb.SearchResult(self.music_list,start,end,self.language,)
        if data['send']==True:
            if simple==True:
                #print(len(data['text']))
                try:
                    temp_mes=self.bot.send_message(id_user,f"{self.conf.get(f'Language {self.language}','wait')}", parse_mode='html')
                    self.bot.delete_message(id_user,temp_mes.message_id)
                    self.bot.send_message(id_user, data['text'], reply_markup=data['keyboard'], parse_mode='html')
                except:
                    data=self.kb.SearchResult(self.music_list,start,end,self.language,without_url=True)
                    temp_mes = self.bot.send_message(id_user, f"{self.conf.get(f'Language {self.language}', 'wait')}",
                                                     parse_mode='html')
                    self.bot.delete_message(id_user, temp_mes.message_id)
                    self.bot.send_message(id_user, data['text'], reply_markup=data['keyboard'], parse_mode='html')
            else:
                try:
                    self.bot.edit_message_text(data['text'],id_user,id_message,parse_mode='html')
                    self.bot.edit_message_reply_markup(id_user, id_message,reply_markup=data['keyboard'])
                except:
                    data = self.kb.SearchResult(self.music_list, start, end, self.language, without_url=True)
                    self.bot.edit_message_text(data['text'], id_user, id_message, parse_mode='html')
                    self.bot.edit_message_reply_markup(id_user, id_message, reply_markup=data['keyboard'])

        else:
            if len(self.music_list)==0:
                self.bot.send_message(id_user,f"{self.conf.get(f'Language {self.language.upper()}','nothing')}",  parse_mode='html')
            self.end = self.start
            self.start = self.end - 10

    def ListIndexExists(self,index):
        if index.isdigit() :
            if int(index)>0 and int(index)<=len(self.music_list):
                r=requests.get(self.music_list[int(index)-1]['download'])
                title=self.music_list[int(index)-1]['name']
                return ['ok',r.content,title,int(index)-1]
            else:
                return ['index out']
        else:
            return ['index not digit']

    def GetMusicFromList(self,data):
        self.bot.delete_message(data.chat.id, data.message_id - 1)
        self.bot.delete_message(data.chat.id, data.message_id)
        temp = self.bot.send_message(data.chat.id, f"{self.conf.get(f'Language {self.language}', 'wait')}",
                                     parse_mode='html')

        music=self.ListIndexExists(data.text)
        if  music[0]=='ok':

            url_keybord=self.kb.UrlDownload(self.music_list[int(music[3])]['download'],self.conf.get(f'Language {self.language}','download'))
            try:
                self.bot.send_audio(data.chat.id,music[1],title=music[2],reply_markup=url_keybord)
            except:
                self.bot.send_message(data.chat.id, f"{self.conf.get(f'Language {self.language}', 'size_big')}",
                                    reply_markup=url_keybord,parse_mode='html')

        elif music[0]=='index out':
            self.bot.send_message(data.chat.id, f"{self.conf.get(f'Language {self.language.upper()}','error1')}",parse_mode='html')
        elif music[0] == 'index not digit':
            self.bot.send_message(data.chat.id, f"{self.conf.get(f'Language {self.language.upper()}','error2')}",parse_mode='html')

        self.bot.delete_message(temp.chat.id, temp.message_id)


    def SearchMusicByShazam(self,text,id_user):
        str = text.split('Shazam: ')
        url = str[1].split('. https://')
        url[0]=url[0].replace('- ','')
        print(url[0])
        self.start = 0
        self.end = 10
        self.music_list = self.SearchMusicByQuery(url[0])
        self.SendMusicByQuery( self.start, self.end, id_user, 0, simple=True)


    def SendMusicByYouTube(self,text,id_user):
        if self.send==True:
            temp_mes = self.bot.send_message(id_user, f"{self.conf.get(f'Language {self.language}', 'wait')}",
                                             parse_mode='html')

            self.send=False
            extract_path=f"{self.conf.get('Path','path')}\\temp\\"
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': f'{extract_path}{id_user}%(title)s.%(ext)s',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '320', }], }

            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                data = ydl.extract_info(text, download=False)
            #print(data['formats'][0]['filesize'])
            if data['duration'] <= 1800:
                with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                    ydl.extract_info(text, download=True)

                if os.stat(f"{extract_path}{id_user}{data['title']}.mp3").st_size<=50000000:
                    with open(f"{extract_path}{id_user}{data['title']}.mp3",'rb') as file:
                        music = file.read()
                        file.close()

                try:
                    self.bot.send_audio(id_user,music,title=data['title'])
                except:
                    self.bot.send_message(id_user,f"{self.conf.get(f'Language {self.language}','size_big')}")
                    print('file size > 50mb')

                os.remove(f"{extract_path}{id_user}{data['title']}.mp3")
                self.send=True
            else:
                self.bot.send_message(id_user,f"{self.conf.get(f'Language {self.language}','to_big')}",parse_mode='html')
            self.bot.delete_message(id_user, temp_mes.message_id)


    def SetLanguage(self,m):
        keyboard=self.kb.LanguageKeyboard()
        self.bot.send_message(m.chat.id,f"{self.conf.get(f'Language {self.language.upper()}','language_key_after')}",reply_markup=keyboard,parse_mode='html')



    def CallBacks(self,call):
        if call.data=="->" and self.end+10<=300:
            self.start = self.end
            self.end = self.start + 10
            self.SendMusicByQuery(self.start,self.end,call.message.chat.id,call.message.message_id)
        elif call.data=="<-" and self.end-10>=10:
            self.end = self.start
            self.start = self.end-10
            self.SendMusicByQuery(self.start,self.end,call.message.chat.id,call.message.message_id)
        elif call.data=="get":
            data=self.bot.send_message(call.message.chat.id,f"{self.conf.get(f'Language {self.language.upper()}','tip2')}",parse_mode='html')
            self.bot.register_next_step_handler(data, self.GetMusicFromList)
        elif "set_language" in call.data:
            lang=(call.data).replace('set_language ','')
            self.db.ChangeLanguage(call.message.chat.id,lang)
            self.language=lang
            keyboard=self.kb.MainKeyboard(lang)['keyboard']
            temp=self.bot.send_message(call.message.chat.id,f"{self.conf.get(f'Language {self.language.upper()}','language_set')}",reply_markup=keyboard,parse_mode='html')
            self.bot.delete_message(call.message.chat.id,temp.message_id-1)



