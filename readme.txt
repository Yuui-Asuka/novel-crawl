1. run:
python novel_crawl.py
====================================================================
参数：
concur_req: 并行度，越多下载得越快，但是对于网站的负担就越大，太快有可能对网站发起ddos攻击。
category: 小说种类 可选值为：
yanqing: 言情小说
xuanhuan: 玄幻奇幻
dushi: 都市青春
wuxia: 武侠仙侠
danmei: 唯美纯爱
kehuan: 科幻灵异
lightnovel: 轻小说
lishi: 历史军事
默认值为lightnovel
每次更换种类之后，按照1，2的步骤操作。
====================================================================
需要安装：
pip install bs4
pip install aiohttp
pip install requests
pip install lxml
