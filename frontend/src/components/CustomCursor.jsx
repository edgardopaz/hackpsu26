import { useEffect, useRef } from 'react'

function CustomCursor() {
  const dotRef = useRef(null)
  const ringRef = useRef(null)

  useEffect(() => {
    const dot = dotRef.current
    const ring = ringRef.current

    if (!dot || !ring || window.matchMedia('(pointer: coarse)').matches) {
      return undefined
    }

    let animationFrame = 0
    let mouseX = window.innerWidth / 2
    let mouseY = window.innerHeight / 2
    let ringX = mouseX
    let ringY = mouseY

    const interactiveSelector = 'a, button, input, textarea, label, [role="button"]'

    const onMouseMove = (event) => {
      mouseX = event.clientX
      mouseY = event.clientY
      dot.style.transform = `translate3d(${mouseX}px, ${mouseY}px, 0)`
    }

    const onMouseOver = (event) => {
      if (event.target.closest(interactiveSelector)) {
        dot.classList.add('cursor-dot--active')
      }
    }

    const onMouseOut = (event) => {
      if (event.target.closest(interactiveSelector)) {
        dot.classList.remove('cursor-dot--active')
      }
    }

    const render = () => {
      ringX += (mouseX - ringX) * 0.12
      ringY += (mouseY - ringY) * 0.12
      ring.style.transform = `translate3d(${ringX}px, ${ringY}px, 0)`
      animationFrame = window.requestAnimationFrame(render)
    }

    dot.style.opacity = '1'
    ring.style.opacity = '1'
    animationFrame = window.requestAnimationFrame(render)

    window.addEventListener('mousemove', onMouseMove)
    document.addEventListener('mouseover', onMouseOver)
    document.addEventListener('mouseout', onMouseOut)

    return () => {
      window.cancelAnimationFrame(animationFrame)
      window.removeEventListener('mousemove', onMouseMove)
      document.removeEventListener('mouseover', onMouseOver)
      document.removeEventListener('mouseout', onMouseOut)
    }
  }, [])

  return (
    <>
      <div ref={ringRef} className="cursor-ring" aria-hidden="true" />
      <div ref={dotRef} className="cursor-dot" aria-hidden="true" />
    </>
  )
}

export default CustomCursor
