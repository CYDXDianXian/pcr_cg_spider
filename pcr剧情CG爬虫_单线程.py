import requests
from bs4 import BeautifulSoup
import time
from pathlib import Path
import sys

path_config = "img"  # 设置图片的保存地址

path = Path(__file__).parent / path_config # 拼接路径。__file__，是一个字符串，表示当前文件的绝对路径。若不进行该设置，直接运行py文件图片路径会存到C盘system32文件夹下
Path(path).mkdir(parents = True, exist_ok = True) # parents：如果父目录不存在，是否创建父目录。exist_ok：只有在目录不存在时创建目录，目录已存在时不会抛出异常。

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36 Edg/97.0.1072.76'
}

proxy = {}
# 若不用代理，将链接清空即可。

time_start = time.time()

url = "https://redive.estertion.win/card/story/"
resp = requests.get(url, headers = headers, proxies = proxy) # 以get方式请求url，得到响应赋值给resp。proxies = prox添加代理。verify = False跳过对具有无效证书的站点的验证
if resp.status_code == 404:
    print(f"网页请求错误，错误代码：404")
    sys.exit() # 结束程序
resp.encodin = 'utf-8'

# print(resp.text)
# 把源码交给bs
main_page = BeautifulSoup(resp.text, "html.parser")
alist = main_page.find("body").find_all("a")
print(f'共爬取到{len(alist)}个文件地址，即将开始下载')

img_url_num = 0
success_num = 0
error_num = 0
for a in alist:
    src = (url + a.get('href')) # 直接通过get就可以拿到属性的值(可点击的链接),若只有文件名，用url+ 去拼接链接
    img_name = src.split("/")[-1] # 拿到url中的最后一个/以后的内容(图片名)
    img_url_num += 1

    if not Path(path, img_name).exists(): 

        try:
            img_resp = requests.get(src, headers = headers, proxies = proxy, timeout = 30) # 以get方式请求url，得到响应赋值给img_resp。timeout=30，表示30秒后发出超时错误。
        except:
            error_num += 1
            print(f'第{img_url_num}个图片下载失败：{img_name}')
            continue

        Path(path, img_name).write_bytes(img_resp.content) # 图片内容写入文件 img_resp.content 这里拿到的是字节(二进制对象)
        
        success_num += 1
        print(f'第{img_url_num}个图片下载成功：{img_name}')
    else:
        print(f'文件 {img_name} 已存在，不再进行下载')

time_end = time.time()
use_time = int(time_end - time_start)
print(f'全部下载完成！共下载成功{success_num}个文件，失败{error_num}个文件，用时{use_time}秒')