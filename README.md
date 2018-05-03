# Telegram File Sharing Robot
這是一個 Telegram bot 他可以尋找檔案 並將檔案上傳到 Dropbox 以便分享檔案

# 指令說明
- 更新檔案清單
    - /update

- 儲存檔案清單
    - /save

- 載入檔案清單
    - /load

以上這三個指令 預設是給管理員用的  (instruction_list 可修改不同身份可以使用的指令)

- 取得這次檔案更新的異動清單
    - /diff

- 取得userid可用於在程式碼中的 user_list ＆ admin_list
    - /get_uid

- 取得chatid可用於在程式碼中的 user_list ＆ admin_list
    - /get_chatid

- 找尋檔案 並回傳一個 csv檔
    - /find_data

- 上傳檔案到 Dropbox 並回傳一個下載的連結
    - /get_link

- 這純粹好玩用 會抽出赫蘿咬東西的貼圖
    - /test
