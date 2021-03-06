import asyncio
import time
import aiohttp
import requests
from pathlib import Path
from lxml import etree
import sys

path = "img"  # 设置图片的保存地址

Path(path).mkdir(parents = True, exist_ok = True) # parents：如果父目录不存在，是否创建父目录。exist_ok：只有在目录不存在时创建目录，目录已存在时不会抛出异常。

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36 Edg/97.0.1072.76'
}

proxy = {}
# 若不用代理，将链接清空即可。

def get_urls():
    '''
    图片下载链接获取
    '''
    global get_urls_msg
    start_time = time.time()
    base = "https://redive.estertion.win/card/story/"
    print('开始进行爬取，请稍后......\n')
    try:
        resp = requests.get(base, headers = headers, proxies = proxy, timeout = 30) # 以get方式请求url，得到响应赋值给resp。proxies = prox添加代理
    except:
        print('请求超时，请检查网络连接')
        sys.exit() # 结束程序
    resp.encoding = 'utf-8'

    tree = etree.HTML(resp.text)
    result = tree.xpath("/html/body/span/a/@href") # 通过xpath提取链接列表

    urls = [base + i for i in result] # 将result中的数据依次放入i中，然后将base与i依次拼接，放入列表urls中。
    end_time = time.time()
    use_time = int(end_time - start_time)
    print(f'共爬取到{len(urls)}个文件地址，即将开始下载\n')
    get_urls_msg = f'\n共爬取到{len(urls)}个文件，爬取用时{use_time}秒'
    time.sleep(3)
    return urls

async def aiodownload(url):
    '''
    图片下载（异步）
    '''
    global success_download, error_download # 必须加全局声明，否则下载计数会出现错误
    success_download = 0
    error_download = 0
    name = url.split("/")[-1] # 拿到url中的最后一个/以后的内容(图片名)
    try:
        if not Path(path, name).exists(): # 文件不存在则进行下载。Path(path, name)拼接路径与文件名
            async with aiohttp.ClientSession(headers = headers) as session: # aiohttp.ClientSession()等价于requests。headers上下都可以放，放一个地方就好
                async with session.get(url) as resp: # session.get()等价于requests.get()。以get方式请求url，得到响应赋值给resp。proxy来指明代理。timeout默认5分钟
                    Path(path, name).write_bytes(await resp.content.read()) # Path.write_bytes(data)，将文件以二进制模式打开，写入二进制data并关闭。一个同名的现存文件将被覆盖。同时该方法完美解决图片出现0kb的bug
                        # resp.content.read()得到字节(二进制)对象，resp.text()得到字符串(文本)对象，resp.json()得到json对象。异步读取文件需要await挂起
                        # resp.content和resp.text只适用于requests.get().content和requests.get().text。resp.json()两种请求方式都一样
                    print("ok", name)
                    success_download += 1
        else:
            print(f'文件 {name} 已存在，不再进行下载')
    except:
        error_download += 1
        print(f'图片下载失败{error_download}个：{name}')

async def main():
    '''
    主协程对象
    '''
    urls = get_urls() #后续需要调用两次urls，这样做只需调用一次get_urls函数，节省资源
    start = time.time() 
    tasks = [aiodownload(url) for url in urls] # 生成执行任务的列表
    await asyncio.wait(tasks)
    end = time.time()

    print(get_urls_msg)
    print(f'共下载成功{success_download}个文件，失败{error_download}个，下载用时{int(end - start)}秒\n')
    print('程序将在10秒后结束......')
    await asyncio.sleep(10)

if __name__ == "__main__":
    asyncio.run(main()) # asyncio.run()，创建事件循环，运行一个协程，关闭事件循环。
# if __name__ == '__main__':的作用
# 一个python文件通常有两种使用方法，第一是作为脚本直接执行，第二是 import 到其他的 python 脚本中被调用（模块重用）执行。
# 因此 if __name__ == 'main': 的作用就是控制这两种情况执行代码的过程，
# 在 if __name__ == 'main': 下的代码只有在第一种情况下（即文件作为脚本直接执行）才会被执行，
# 而 import 到其他脚本中是不会被执行的。