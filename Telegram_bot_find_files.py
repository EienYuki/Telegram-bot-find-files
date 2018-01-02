# coding: utf-8
# https://github.com/EienYuki

import dropbox
import hashlib
import os, random
from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters

class Telegram_bot_find_files():
    def access_check(self, input_id, id_list):
        print("access_check")
        if input_id in id_list:
            return True
        else:
            return False

    def get_file_list(self, root_path):
        print("get_file_list")
        out = []
        for root, dirs, files in os.walk(root_path):
            for r in files:
                out.append(root+"/"+r)
        return out

    def save_list(self, path, input_list):
        print("save_list")
        with open(path, "w") as f:
            for s in input_list:
                f.write(str(s) +"\n")

    def load_list(self, path):
        print("load_list")
        out = []
        with open(path, "r") as f:
            for line in f:
                out.append(line.strip())
        return out

    def upload_file(self, path):
        # dropbox-api – Uploading a file using the Dropbox Python SDK - CodeDay
        # https://www.codeday.top/2017/10/24/52483.html

        print("upload_file")
        dest_path = '/%s' % os.path.basename(path)
        dbx = dropbox.Dropbox(self.dropbox_token)

        f = open(path, "rb")
        file_size = os.path.getsize(path)
        CHUNK_SIZE = 4 * 1024 * 1024
        if file_size <= CHUNK_SIZE:
            dbx.files_upload(f.read(), dest_path)
        else:
            upload_session_start_result = dbx.files_upload_session_start(f.read(CHUNK_SIZE))
            cursor = dropbox.files.UploadSessionCursor(session_id=upload_session_start_result.session_id,
                                                    offset=f.tell())
            commit = dropbox.files.CommitInfo(path=dest_path)
            while f.tell() < file_size:
                if ((file_size - f.tell()) <= CHUNK_SIZE):
                    dbx.files_upload_session_finish(f.read(CHUNK_SIZE),
                                                    cursor,
                                                    commit)
                else:
                    dbx.files_upload_session_append(f.read(CHUNK_SIZE),
                                                    cursor.session_id,
                                                    cursor.offset)
                    cursor.offset = f.tell()
        f.close()
        result = dbx.files_get_temporary_link(dest_path)
        return result.link


    def _update(self, bot, update):
        print("_update")
        if self.access_check(update.message.chat_id, self.admin_list):
            self.tmp_all_file_list = self.get_file_list(self.find_dir_root)
            self.tmp_find_file_dict = {}
            self.tmp_find_csv_list = []
            update.message.reply_text('完成')
        else:
            bot.sendSticker(chat_id=update.message.chat_id, sticker=self.drop_sticker_id)

    def _save(self, bot, update):
        print("_save")
        if self.access_check(update.message.chat_id, self.admin_list):
            self.save_list("%s/file.list" % self.work_dir_root, self.tmp_all_file_list)
            update.message.reply_text('完成')
        else:
            bot.sendSticker(chat_id=update.message.chat_id, sticker=self.drop_sticker_id)

    def _load(self, bot, update):
        print("_load")
        if self.access_check(update.message.chat_id, self.admin_list):
            self.tmp_all_file_list = self.load_list("%s/file.list" % self.work_dir_root)
            update.message.reply_text('完成')
        else:
            bot.sendSticker(chat_id=update.message.chat_id, sticker=self.drop_sticker_id)
    
    def _get_chatid(self, bot, update):
        print("_get_chatid")
        bot.send_message(chat_id=update.message.chat_id, text=update.message.chat_id)

    def _help(self, bot, update):
        print("_help")
        if self.access_check(update.message.chat_id, self.access_list):
            Msg_text = "☆ ★ ☆ ★ 使用方式 ★ ☆ ★ ☆\n"
            Msg_text += "先使用 find_data 找尋檔案\n"
            Msg_text += "之後複製列表中 的資源編號\n"
            Msg_text += "最後使用 get_link 來得到檔案下載的連結\n"
            Msg_text += "get_link 可能會花很多時間 請耐心等候 謝謝！\n"

            Msg_text += "\n☆ ★ ☆ ★ 指令說明 ★ ☆ ★ ☆\n"
            Msg_text += "find_data 你要找的檔案名稱\n"
            Msg_text += "範例：find_data 來自深淵\n"
            Msg_text += "get_link 資源編號(經由find取得)\n"
            Msg_text += "範例：get_link 098f6bcd4621d373cade4e832627b4f6"
            bot.send_message(chat_id=update.message.chat_id, text=Msg_text)
        else:
            bot.sendSticker(chat_id=update.message.chat_id, sticker=self.drop_sticker_id)

    def _find_data(self, bot, update, args):
        print("_find_data")
        if self.access_check(update.message.chat_id, self.access_list):
            out_msg = ""
            count = 0
            text_caps = ' '.join(args)
            tp_path = "%s/find[%s].csv" % (self.work_dir_root, text_caps)

            if not text_caps in self.tmp_find_csv_list:
                sha_1 = hashlib.sha1()
                tp_now_find = ["ID,檔案"]
                for r in self.tmp_all_file_list:
                    if text_caps in r:
                        sha_1.update(r.encode())
                        tid = sha_1.hexdigest()
                        if not tid in self.tmp_find_file_dict:
                            self.tmp_find_file_dict[tid] = r
                        tp_now_find.append(tid+","+r.strip())
                        count +=1
                self.save_list(tp_path,tp_now_find)
                self.tmp_find_csv_list.append(text_caps)
            
            bot.send_document(chat_id=update.message.chat_id, document=open(tp_path, 'rb'))
        else:
            bot.sendSticker(chat_id=update.message.chat_id, sticker=self.drop_sticker_id)

    def _get_link(self, bot, update, args):
        print("_get_link")
        text_caps = ' '.join(args)
        if self.access_check(update.message.chat_id, self.access_list):
            if text_caps in self.tmp_find_file_dict:
                if os.path.isfile(self.tmp_find_file_dict[text_caps]):
                    link = self.upload_file(self.tmp_find_file_dict[text_caps])
                    update.message.reply_text(link)
                else:
                    update.message.reply_text('檔案遺失')
            else:
                update.message.reply_text('沒有此編號')
        else:
            bot.sendSticker(chat_id=update.message.chat_id, sticker=self.drop_sticker_id)

    def _test(self, bot, update):
        print("_test")
        sticker_list = [
            'CAADBQADPgIAAkpxYgrrtBKXMyXpZAI',
            'CAADBQADPwIAAkpxYgoDlPO5cfOM5gI',
            'CAADBQADQAIAAkpxYgrJjvslPudKXAI',
            'CAADBQADQgIAAkpxYgqdfXltSeQaSQI',
            'CAADBQADRAIAAkpxYgoqSxC6sJ6xQgI',
            'CAADBQADRgIAAkpxYgpyI057U7bl2wI',
            'CAADBQADSAIAAkpxYgrx8eXrsxb3sQI',
            'CAADBQADSgIAAkpxYgo_4ArvZA8jdwI',
            'CAADBQADTAIAAkpxYgpdr56IH4-e9gI',
            'CAADBQADTwIAAkpxYgoL37OO2La_1wI',
            'CAADBQADUgIAAkpxYgplByKEYErOPAI',
            'CAADBQADVAIAAkpxYgq4QDly8hiQJAI',
            'CAADBQADVwIAAkpxYgqczRho4u07_AI',
            'CAADBQADWQIAAkpxYgpM0sy4QlAwgQI',
            'CAADBQADWwIAAkpxYgoYdhJIkB9FhAI',
            'CAADBQADXQIAAkpxYgoFajuoPh2yXgI',
            'CAADBQADXwIAAkpxYgowSDcxLzqBOQI',
            'CAADBQADYQIAAkpxYgoM2gJH_fWoqQI',
            'CAADBQADYwIAAkpxYgpUCG5lsn3nvgI',
            'CAADBQADZQIAAkpxYgqzOa9HKo3-SwI',
            'CAADBQADxQIAAkpxYgohOqLzysYoEgI',
            'CAADBQADxwIAAkpxYgr3F9TBr9lSkQI',
            'CAADBQADyQIAAkpxYgq2fY5Utae6zAI'
        ]
        update.message.reply_text('嗨 你好！')
        bot.sendSticker(chat_id=update.message.chat_id, sticker=random.choice(sticker_list))
    
    
    def __init__(self, bot_token, dropbox_token, access_list, admin_list, find_dir_root, work_dir_root):
        self.dropbox_token = dropbox_token
        self.access_list = access_list
        self.admin_list = admin_list

        self.find_dir_root = find_dir_root
        self.work_dir_root = work_dir_root

        self.tmp_all_file_list = []
        self.tmp_find_csv_list = []
        self.tmp_find_file_dict = {}

        self.drop_sticker_id = 'CAADBQADlQIAAt3DvwhTu-o-F2gRBwI'

        self.updater = Updater(token=bot_token)
        dispatcher = self.updater.dispatcher

        dispatcher.add_handler( CommandHandler('get_chatid', self._get_chatid) )
        dispatcher.add_handler( CommandHandler('test', self._test) )

        dispatcher.add_handler( CommandHandler('help', self._help) )

        dispatcher.add_handler( CommandHandler('update', self._update) )
        dispatcher.add_handler( CommandHandler('save', self._save) )
        dispatcher.add_handler( CommandHandler('load', self._load) )

        dispatcher.add_handler( CommandHandler('find_data', self._find_data, pass_args=True) )
        dispatcher.add_handler( CommandHandler('get_link', self._get_link, pass_args=True) )

        self.updater.start_polling()
        print("start bot")

if __name__ == '__main__':
    Telegram_bot_find_files(
        bot_token = 'your bot_token',
        dropbox_token = 'your dropbox_token',
        access_list = [
            # chat_id list
            # your allow access list
        ],
        admin_list = [
            # chat_id list
            # your admin list
        ],
        find_dir_root = '/sample/data',
        work_dir_root = 'bot/work_dir'
    )