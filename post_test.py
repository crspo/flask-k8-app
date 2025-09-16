import requests, json, base64, time
url='http://127.0.0.1:5000/api/upload'
for i in range(10):
    try:
        resp = requests.post(url, data={'serials':'ABC123\nDEF456\nGHI789','size':'medium'}, timeout=120)
        print('Status', resp.status_code)
        j = resp.json()
        print('img_base64 length:', len(j.get('img_base64','')))
        print('pdf_b64 length:', len(j.get('pdf_b64','')))
        with open('out_dm.png','wb') as f:
            f.write(base64.b64decode(j.get('img_base64')))
        with open('out_dm.pdf','wb') as f:
            f.write(base64.b64decode(j.get('pdf_b64')))
        print('Wrote out_dm.png and out_dm.pdf')
        break
    except Exception as e:
        print('Attempt', i, 'failed:', e)
        time.sleep(1)
