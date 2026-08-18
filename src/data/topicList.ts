import type { HotTopic } from '../types'

export function orderTopicsByHeat(topics: HotTopic[]): HotTopic[] {
  return [...topics].sort((a, b) => {
    if (a.hotScore === null && b.hotScore !== null) return 1
    if (a.hotScore !== null && b.hotScore === null) return -1
    if (a.hotScore !== null && b.hotScore !== null && a.hotScore !== b.hotScore) {
      return b.hotScore - a.hotScore
    }
    return a.rank - b.rank || a.source.localeCompare(b.source, 'en') || a.id - b.id
  })
}

function normalizedTitleKey(title: string): string {
  return title.normalize('NFKC').toLocaleLowerCase('zh-CN').replace(/[\p{P}\p{Z}]/gu, '')
}

export function prepareTopics(topics: HotTopic[]): HotTopic[] {
  const seenTitles = new Set<string>()
  return orderTopicsByHeat(topics).filter((topic) => {
    const titleKey = normalizedTitleKey(topic.title)
    if (!titleKey || seenTitles.has(titleKey)) return false
    seenTitles.add(titleKey)
    return true
  })
}
