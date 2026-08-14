import { useCallback, useEffect, useMemo, useState } from 'react'
import { ArrowUpRight, CalendarDays, Flame, RefreshCw, Search, TrendingUp } from 'lucide-react'
import { fetchHotTopics } from './data/api'
import { fallbackSearchUrl, primaryTopicUrl } from './topicLinks'
import { SOURCES, type HotTopic, type SourceKey, type SourceSummary } from './types'

const SOURCE_META: Record<SourceKey, { label: string; short: string; tone: string }> = {
  baidu: { label: '百度', short: '百', tone: 'blue' },
  weibo: { label: '微博', short: '微', tone: 'red' },
  toutiao: { label: '头条', short: '头', tone: 'orange' },
  xiaohongshu: { label: '小红书', short: '红', tone: 'rose' },
  tencent: { label: '腾讯', short: '腾', tone: 'green' },
}

function localDate(): string {
  const now = new Date()
  const offset = now.getTimezoneOffset() * 60_000
  return new Date(now.getTime() - offset).toISOString().slice(0, 10)
}

function compactNumber(value: number | null): string {
  if (value === null) return '热度未公布'
  if (value >= 10_000_000) return `${(value / 10_000_000).toFixed(1)}千万`
  if (value >= 10_000) return `${(value / 10_000).toFixed(1)}万`
  return value.toLocaleString('zh-CN')
}

function formatDate(value: string): { day: string; month: string } {
  const date = new Date(`${value}T00:00:00`)
  return {
    day: String(date.getDate()).padStart(2, '0'),
    month: new Intl.DateTimeFormat('zh-CN', { month: 'short' }).format(date),
  }
}

function SignalTicker({ topics }: { topics: HotTopic[] }) {
  const tickerTopics = topics.filter((topic) => topic.rank <= 2).slice(0, 10)
  if (tickerTopics.length === 0) return null
  const group = (hidden: boolean) => (
    <div className="ticker-group" aria-hidden={hidden}>
      {tickerTopics.map((topic) => (
        <a key={`${hidden ? 'copy' : 'main'}-${topic.source}-${topic.id}`} href={`#topic-${topic.source}-${topic.id}`} tabIndex={hidden ? -1 : 0}>
          <span className={`ticker-source ${SOURCE_META[topic.source].tone}`}>{SOURCE_META[topic.source].short}</span>
          <strong>{topic.title}</strong>
          <i>#{topic.rank}</i>
        </a>
      ))}
    </div>
  )
  return (
    <div className="signal-ticker" aria-label="正在滚动的重点热讯">
      <span className="ticker-label"><TrendingUp size={14} />热讯</span>
      <div className="ticker-window">
        <div className="ticker-track">{group(false)}{group(true)}</div>
      </div>
    </div>
  )
}

function SourceLegend({ summary }: { summary: SourceSummary[] }) {
  return (
    <div className="source-legend" aria-label="平台采集概览">
      {SOURCES.map((source) => {
        const meta = SOURCE_META[source]
        const item = summary.find((row) => row.source === source)
        return (
          <span key={source}>
            <i className={meta.tone} />
            {meta.label}
            <b>{item?.itemCount ?? 0}</b>
          </span>
        )
      })}
    </div>
  )
}

function BentoCard({ topic, index }: { topic: HotTopic; index: number }) {
  const meta = SOURCE_META[topic.source]
  const lead = index === 0
  const featured = index < 5
  const primaryUrl = primaryTopicUrl(topic)
  const searchUrl = fallbackSearchUrl(topic)
  return (
    <article
      id={`topic-${topic.source}-${topic.id}`}
      className={`bento-card ${lead ? 'lead-card' : featured ? 'featured-card' : ''} pattern-${index % 4}`}
    >
      <div className="card-glow" aria-hidden="true" />
      <div className="card-meta">
        <span className={`source-badge ${meta.tone}`}>{meta.short}</span>
        <span>{meta.label}</span>
        <span className="rank-chip">TOP {String(topic.rank).padStart(2, '0')}</span>
      </div>
      <h2>{topic.title}</h2>
      <p>{topic.summary ?? '点击查看原平台的完整内容与最新讨论。'}</p>
      <div className="card-footer">
        <span className="heat-value"><Flame size={14} fill="currentColor" />{compactNumber(topic.hotScore)}</span>
        <div className="card-actions">
          <a href={primaryUrl} target="_blank" rel="noreferrer">原平台 <ArrowUpRight size={13} /></a>
          <a className="fallback-link" href={searchUrl} target="_blank" rel="noreferrer">备用搜索 <Search size={12} /></a>
        </div>
      </div>
    </article>
  )
}

export default function App() {
  const [date, setDate] = useState(localDate())
  const [query, setQuery] = useState('')
  const [topics, setTopics] = useState<HotTopic[]>([])
  const [summary, setSummary] = useState<SourceSummary[]>([])
  const [demo, setDemo] = useState(false)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const load = useCallback(async () => {
    setLoading(true)
    setError('')
    try {
      const page = await fetchHotTopics(date, 'all')
      setTopics(page.topics)
      setSummary(page.summary)
      setDemo(page.demo)
    } catch (reason) {
      setTopics([])
      setSummary([])
      setError(reason instanceof Error ? reason.message : '热点加载失败')
    } finally {
      setLoading(false)
    }
  }, [date])

  useEffect(() => { void load() }, [load])

  const ordered = useMemo(() => {
    const keyword = query.trim().toLocaleLowerCase('zh-CN')
    const visible = keyword
      ? topics.filter((topic) => `${topic.title} ${topic.summary ?? ''}`.toLocaleLowerCase('zh-CN').includes(keyword))
      : topics
    return [...visible].sort((a, b) => a.rank - b.rank || SOURCES.indexOf(a.source) - SOURCES.indexOf(b.source))
  }, [query, topics])

  const displayDate = formatDate(date)

  return (
    <div className="site-shell">
      <header className="topbar">
        <a className="brand" href="./" aria-label="桃影热点首页">
          <span className="brand-mark"><Flame size={18} fill="currentColor" /></span>
          <span>桃影热点</span>
        </a>
        <span className="topbar-edition">DAILY SIGNAL / 网络热点编辑台</span>
        <a className="github-link" href="https://github.com/fanxu1218/TaoYingHotPoint" target="_blank" rel="noreferrer">开源项目 <ArrowUpRight size={15} /></a>
      </header>

      <main>
        <section className="editorial-hero">
          <div className="hero-index">
            <span>NO.</span>
            <strong>{displayDate.day}</strong>
            <small>{displayDate.month}刊</small>
          </div>
          <div className="hero-copy">
            <span className="eyebrow"><i />LIVE NETWORK PULSE</span>
            <h1>网络此刻的<br /><em>情绪与脉搏</em></h1>
            <p>五个平台，不做机械堆叠。我们把热度重新编排成一张每天更新的数字头版。</p>
          </div>
          <div className="pulse-seal" aria-hidden="true">
            <span className="pulse-ring ring-one" />
            <span className="pulse-ring ring-two" />
            <strong>HOT<br />NOW</strong>
            <small>{topics.length}</small>
          </div>
        </section>

        {demo && <div className="demo-banner">当前展示示例数据 · 接入 Supabase 后自动切换真实榜单</div>}

        <SignalTicker topics={topics} />

        <section className="board-tools">
          <div>
            <span className="section-kicker">TODAY'S FRONT PAGE</span>
            <h2>今日热浪</h2>
          </div>
          <div className="tool-actions">
            <label className="search-control"><Search size={16} /><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="搜索全部热点" aria-label="搜索全部热点" /></label>
            <label className="date-control"><CalendarDays size={16} /><input type="date" value={date} max={localDate()} onChange={(event) => setDate(event.target.value)} aria-label="选择热点日期" /></label>
            <button className="refresh-button" onClick={() => void load()} disabled={loading} aria-label="刷新热点"><RefreshCw size={16} className={loading ? 'spinning' : ''} /></button>
          </div>
        </section>

        <SourceLegend summary={summary} />

        <section className="signal-board" aria-live="polite" aria-busy={loading}>
          {loading && <div className="state-card">正在编排今天的数字头版…</div>}
          {!loading && error && <div className="state-card error-state">{error}<button onClick={() => void load()}>重新加载</button></div>}
          {!loading && !error && ordered.length === 0 && <div className="state-card">这一天还没有符合条件的热点。</div>}
          {!loading && !error && ordered.map((topic, index) => <BentoCard key={`${topic.source}-${topic.id}`} topic={topic} index={index} />)}
        </section>
      </main>

      <footer>
        <span>桃影热点 · 数据来自各平台公开榜单</span>
        <span>每天一张数字头版，记录网络正在关心什么</span>
        <span>内容版权归原平台及作者所有</span>
      </footer>
    </div>
  )
}
