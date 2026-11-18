import './style.css'
import './fontawesome/css/all.min.css'

import Alpine from 'alpinejs'
import collapse from '@alpinejs/collapse'
import focus from '@alpinejs/focus'
import { gsap } from 'gsap'

declare global {
  interface Window {
    Alpine: typeof Alpine
  }
}

const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches

// ---------------------------------------------------------------------------
// Alpine components
// ---------------------------------------------------------------------------

/** Site header: transparent over a hero, solid once scrolled, hides on scroll down. */
Alpine.data('siteHeader', (overlay: boolean = false) => ({
  overlay,
  scrolled: false,
  hidden: false,
  menuOpen: false,
  lastY: 0,
  init() {
    this.onScroll()
    window.addEventListener('scroll', () => this.onScroll(), { passive: true })
    this.$watch('menuOpen', (open: boolean) => document.documentElement.classList.toggle('overflow-hidden', open))
  },
  onScroll() {
    const y = window.scrollY
    this.scrolled = y > 40
    this.hidden = !this.menuOpen && y > 300 && y > this.lastY
    this.lastY = y
  },
  get solid() {
    return !this.overlay || this.scrolled || this.menuOpen
  },
}))

/** Image lightbox for galleries. Items are read from [data-lightbox] children. */
Alpine.data('lightbox', () => ({
  open: false,
  index: 0,
  items: [] as { src: string; caption: string }[],
  init() {
    this.items = Array.from(this.$el.querySelectorAll<HTMLElement>('[data-lightbox]')).map((el) => ({
      src: el.dataset.lightbox || '',
      caption: el.dataset.caption || '',
    }))
  },
  show(i: number) {
    this.index = i
    this.open = true
  },
  next() {
    this.index = (this.index + 1) % this.items.length
  },
  prev() {
    this.index = (this.index - 1 + this.items.length) % this.items.length
  },
  get current() {
    return this.items[this.index] || { src: '', caption: '' }
  },
}))

/** Prev/next buttons for a horizontal .rail scroller. */
Alpine.data('rail', () => ({
  atStart: true,
  atEnd: false,
  init() {
    const el = this.$refs.track as HTMLElement
    const update = () => {
      this.atStart = el.scrollLeft < 8
      this.atEnd = el.scrollLeft + el.clientWidth >= el.scrollWidth - 8
    }
    el.addEventListener('scroll', update, { passive: true })
    window.addEventListener('resize', update)
    update()
  },
  scroll(dir: 1 | -1) {
    const el = this.$refs.track as HTMLElement
    const card = el.firstElementChild as HTMLElement | null
    const step = card ? card.offsetWidth + 20 : el.clientWidth * 0.8
    el.scrollBy({ left: dir * step, behavior: reduceMotion ? 'auto' : 'smooth' })
  },
}))

window.Alpine = Alpine
Alpine.plugin(collapse)
Alpine.plugin(focus)
Alpine.start()

// ---------------------------------------------------------------------------
// Scroll reveal animations (.fade-in, .slide-in-left/right/top)
// ---------------------------------------------------------------------------

const REVEALS: Record<string, gsap.TweenVars> = {
  'fade-in': {},
  'slide-in-left': { x: -60 },
  'slide-in-right': { x: 60 },
  'slide-in-top': { y: 60 },
}

function initReveals() {
  const selector = Object.keys(REVEALS).map((c) => `.${c}`).join(',')
  const elements = document.querySelectorAll<HTMLElement>(selector)
  if (reduceMotion || !('IntersectionObserver' in window)) {
    elements.forEach((el) => (el.style.opacity = '1'))
    return
  }
  elements.forEach((el) => {
    const cls = Object.keys(REVEALS).find((c) => el.classList.contains(c))!
    gsap.set(el, { opacity: 0, ...REVEALS[cls] })
  })
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return
        const el = entry.target as HTMLElement
        const delay = Number(el.dataset.delay || 0)
        gsap.to(el, { opacity: 1, x: 0, y: 0, duration: 0.7, delay, ease: 'power3.out' })
        observer.unobserve(el)
      })
    },
    { threshold: 0.15, rootMargin: '0px 0px -40px 0px' },
  )
  elements.forEach((el) => observer.observe(el))
}

initReveals()
