import type { HotTopic } from '../types'

const now = new Date().toISOString()

export const demoTopics: HotTopic[] = [
  { id: 1, source: 'baidu', title: '城市更新让生活更有温度', url: 'https://top.baidu.com/board?tab=realtime', summary: '示例数据：连接数据库后将展示真实榜单。', coverUrl: null, rank: 1, hotScore: 7904847, capturedAt: now },
  { id: 2, source: 'weibo', title: '夏日里的普通人瞬间', url: 'https://s.weibo.com/top/summary', summary: '示例数据：微博公开热搜占位内容。', coverUrl: null, rank: 1, hotScore: 6248000, capturedAt: now },
  { id: 3, source: 'toutiao', title: '今天值得关注的五件事', url: 'https://www.toutiao.com/ch/news_hot/', summary: '示例数据：今日头条公开热榜占位内容。', coverUrl: null, rank: 1, hotScore: 5190000, capturedAt: now },
  { id: 4, source: 'xiaohongshu', title: '年轻人的周末松弛感清单', url: 'https://www.xiaohongshu.com/explore', summary: '示例数据：小红书公开热点占位内容。', coverUrl: null, rank: 1, hotScore: 3820000, capturedAt: now },
  { id: 5, source: 'tencent', title: '新技术正在改变日常生活', url: 'https://news.qq.com/', summary: '示例数据：腾讯新闻公开热点占位内容。', coverUrl: null, rank: 1, hotScore: 3190104, capturedAt: now },
  { id: 6, source: 'baidu', title: '多地迎来新一轮文旅热潮', url: 'https://top.baidu.com/board?tab=realtime', summary: null, coverUrl: null, rank: 2, hotScore: 2980000, capturedAt: now },
  { id: 7, source: 'tencent', title: '夜间经济释放城市新活力', url: 'https://news.qq.com/', summary: null, coverUrl: null, rank: 2, hotScore: 2750000, capturedAt: now },
  { id: 8, source: 'weibo', title: '把生活过成自己喜欢的样子', url: 'https://s.weibo.com/top/summary', summary: '示例数据：用于展示热点卡片网格。', coverUrl: null, rank: 2, hotScore: 2460000, capturedAt: now },
  { id: 9, source: 'toutiao', title: '新消费场景折射生活新变化', url: 'https://www.toutiao.com/ch/news_hot/', summary: '示例数据：连接数据库后将自动替换。', coverUrl: null, rank: 2, hotScore: 2280000, capturedAt: now },
  { id: 10, source: 'xiaohongshu', title: '城市漫步路线火了', url: 'https://www.xiaohongshu.com/explore', summary: '示例数据：公开热点占位内容。', coverUrl: null, rank: 2, hotScore: 2050000, capturedAt: now },
  { id: 11, source: 'baidu', title: '科技创新带来哪些新体验', url: 'https://top.baidu.com/board?tab=realtime', summary: '示例数据：公开热搜占位内容。', coverUrl: null, rank: 3, hotScore: 1920000, capturedAt: now },
  { id: 12, source: 'weibo', title: '今日份治愈小事', url: 'https://s.weibo.com/top/summary', summary: null, coverUrl: null, rank: 3, hotScore: 1810000, capturedAt: now },
  { id: 13, source: 'toutiao', title: '公共文化空间越来越有活力', url: 'https://www.toutiao.com/ch/news_hot/', summary: null, coverUrl: null, rank: 3, hotScore: 1760000, capturedAt: now },
  { id: 14, source: 'xiaohongshu', title: '普通人的一百种松弛感', url: 'https://www.xiaohongshu.com/explore', summary: null, coverUrl: null, rank: 3, hotScore: 1640000, capturedAt: now },
  { id: 15, source: 'tencent', title: '博物馆夜游成为暑期新选择', url: 'https://news.qq.com/', summary: null, coverUrl: null, rank: 3, hotScore: 1580000, capturedAt: now },
  { id: 16, source: 'baidu', title: '身边的小变化映照发展新气象', url: 'https://top.baidu.com/board?tab=realtime', summary: null, coverUrl: null, rank: 4, hotScore: 1490000, capturedAt: now },
  { id: 17, source: 'baidu', title: '全民健身打开夏日新方式', url: 'https://top.baidu.com/board?tab=realtime', summary: null, coverUrl: null, rank: 5, hotScore: 1410000, capturedAt: now },
  { id: 18, source: 'weibo', title: '这个夏天被晚风治愈了', url: 'https://s.weibo.com/top/summary', summary: null, coverUrl: null, rank: 4, hotScore: 1380000, capturedAt: now },
  { id: 19, source: 'weibo', title: '年轻人开始重新发现附近', url: 'https://s.weibo.com/top/summary', summary: null, coverUrl: null, rank: 5, hotScore: 1320000, capturedAt: now },
  { id: 20, source: 'toutiao', title: '县城文旅有了更多新玩法', url: 'https://www.toutiao.com/ch/news_hot/', summary: null, coverUrl: null, rank: 4, hotScore: 1260000, capturedAt: now },
  { id: 21, source: 'toutiao', title: '绿色出行成为城市日常', url: 'https://www.toutiao.com/ch/news_hot/', summary: null, coverUrl: null, rank: 5, hotScore: 1190000, capturedAt: now },
  { id: 22, source: 'xiaohongshu', title: '周末短途旅行灵感清单', url: 'https://www.xiaohongshu.com/explore', summary: null, coverUrl: null, rank: 4, hotScore: 1130000, capturedAt: now },
  { id: 23, source: 'xiaohongshu', title: '下班后的两小时怎么过', url: 'https://www.xiaohongshu.com/explore', summary: null, coverUrl: null, rank: 5, hotScore: 1080000, capturedAt: now },
  { id: 24, source: 'tencent', title: '清洁能源应用加速走进生活', url: 'https://news.qq.com/', summary: null, coverUrl: null, rank: 4, hotScore: 1020000, capturedAt: now },
  { id: 25, source: 'tencent', title: '城市公共空间释放更多可能', url: 'https://news.qq.com/', summary: null, coverUrl: null, rank: 5, hotScore: 980000, capturedAt: now },
]
