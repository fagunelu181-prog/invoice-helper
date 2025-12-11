from fastapi import FastAPI
from fastapi.responses import FileResponse # 這是新工具：用來傳送檔案
import uvicorn
import requests
import urllib3
import os

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = FastAPI()

# 注意：我們把 CORS 拿掉了，因為現在前端後端在同一個家，不需要跨域了

API_URL = "https://data.gcis.nat.gov.tw/od/data/api/9D17AE0D-09B5-4732-A8F4-81C2EE9DED26"

# 1. 這是首頁：當有人連線到網址，直接把 index.html 給他看
@app.get("/")
def read_root():
    return FileResponse('index.html')

# 2. 這是 API：原本的查詢功能
@app.get("/api/company/{ubn}")
def search_ubn(ubn: str):
    print(f"查詢統編：{ubn}")
    
    params = {
        "$format": "json",
        "$filter": f"Business_Accounting_NO eq {ubn}",
        "$top": 1
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "application/json"
    }

    try:
        response = requests.get(API_URL, params=params, headers=headers, verify=False, timeout=5)
        data = response.json()
        if len(data) > 0:
            return {"name": data[0]["Company_Name"]}
        else:
            return {"name": "查無此統編"}
    except Exception as e:
        # 備用資料庫
        backup_db = {
            "23300080": "台灣積體電路製造股份有限公司 (備用)",
            "04126516": "玉山商業銀行股份有限公司",
            "16606102": "網路家庭國際資訊股份有限公司"
        }
        if ubn in backup_db:
            return {"name": backup_db[ubn]}
        return {"name": "連線失敗且無備用資料"}

if __name__ == "__main__":
    # 這裡的 port 設定是給雲端用的
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)