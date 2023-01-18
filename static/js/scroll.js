const scroller = document.querySelector('.scroller')
const elements = scroller.querySelectorAll('.scroll-element')
const length = elements.length
var current = 0
const scroll = () => {
    if (current === length) {
        current = 0
    }
    console.log('current: ', current);
    elements[current].scrollIntoView()
    current++
    console.log('new current: ', current);
}
// setInterval(scroll, 1000)