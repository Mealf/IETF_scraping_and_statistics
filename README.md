# IETF_scraping_and_statistics

使用爬蟲蒐集IETF組織相關資料(ex. WG、RFC、draft)，並進行資料的統計



## 目前完成項目
- 取得WG清單 (ietf_info.py / get_working_groups_list)
- 取得關鍵字清單 (file_ops.py / update_keyword_list)
- 取得RFC之官方關鍵字 (get_keyword.py / get_RFC_keyword)
- 從文字中去比對關鍵字清單並取得關鍵字 (keyword_handld.py / get_keyword_from_text)
- 從RFC與draft的標題中進行關鍵字蒐集 (get_keyword.py / get_keyword_from_title)
- 對目前的 RFC 依 WG 進行數量統計 (ietg_info.py / get_RFCs_order_by_WGs)
- 根據WG取得文件(RFC、draft)的清單，包含id、名稱與網址資訊 (ietf_info.py / get_doc_list)
- 對關鍵字進行正規化(轉小寫、去連接符號與去掉前後空白) (keyword_normalize.py / keyword_normalize)
- 分析過往IETF會議或mail list，來分析該WG的活躍度 (maillist.py / rank_wg_by_maillist)
---

## 快取檔案
因有大量的檔案要經過爬蟲蒐集，每次執行時都要花費大量時間在抓取檔案的部分

因此建立了快取的機制，每次爬蟲時都會順便將爬下來的內容存在檔案中，若快取檔案的修改時間為執行當天，就會使用快取檔案進行統計與分析，可以加快執行的時間。

使用 `file_ops / is_cache_file_available` 函式來判斷是否有快取檔案可供使用，在可用快取檔案的函式中，有對應的參數可以將快取的功能給關閉。

---

## TODO
- 使用關鍵字的關聯表對關鍵字進行擴充
- 使用多執行緒或非同步的方式進行爬蟲