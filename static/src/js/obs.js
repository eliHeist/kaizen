//#region faders
const faders = document.querySelectorAll('.obs.fade-in')

const fade_in_options = {
    threshold: 0,
    rootMargin: "0px 0px -200px 0px"
}
const fadeInOnScroll = new IntersectionObserver((entries, fadeInOnScroll) => {
    entries.forEach(entry => {
        if (!entry.isIntersecting) {
            return
        } else {
            entry.target.classList.add('appear')
            fadeInOnScroll.unobserve(entry.target)
        }
    });
},fade_in_options)

faders.forEach(fader => {
    fadeInOnScroll.observe(fader)
});

//#endregion
//#region sliders
const sliders = document.querySelectorAll('.obs.slide-in')

const slide_in_options = {
    threshold: 0,
    rootMargin: "0px 0px -200px 0px",
}
const slideInOnScroll = new IntersectionObserver((entries, slideInOnScroll) => {
    entries.forEach(entry => {
        if (!entry.isIntersecting) {
            return
        } else {
            entry.target.classList.add('appear')
            slideInOnScroll.unobserve(entry.target)
        }
    });
},slide_in_options)

sliders.forEach(slider => {
    slideInOnScroll.observe(slider)
});

//#endregion