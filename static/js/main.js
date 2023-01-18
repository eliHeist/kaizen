//#region header
let lastScroll = 0;
const nav = document.getElementById("navbar-sticky");
if (document.getElementById("#hero-space") != null) {
    document.getElementById("#hero-space").style.height = nav.offsetHeight + "px";
}

window.addEventListener("scroll", () => {
    const currentScroll = window.pageYOffset;

    if (currentScroll <= 0) {
        nav.classList.remove("show");
    }
    if (currentScroll > lastScroll && !nav.classList.contains("hidden")) {
        nav.classList.remove("show");
        nav.classList.add("hidden");
    }
    if (currentScroll < lastScroll && nav.classList.contains("hidden")) {
        nav.classList.remove("hidden");
        nav.classList.add("show");
    }
    lastScroll = currentScroll;
});

const smmenu = document.querySelector('.smmenu')
const menubtn = document.querySelector('#menu-btn')
const closemenu = document.querySelector('.close-nav')
menubtn.addEventListener('click', () => {
    smmenu.classList.toggle('hidden')
})
closemenu.addEventListener('click', () => {
    smmenu.classList.toggle('hidden')
})

const banner = document.getElementById("banner")
const links = document.querySelectorAll(".nav-link")

const options = {
    rootMargin: `-${nav.offsetHeight}px`,
    threshold: 0,
}

// const Observer = new IntersectionObserver(function(entries, observer){
//     entries.forEach(entry => {
//         if (entry.isIntersecting) {
//             nav.classList.toggle('bg-white')
//             links.forEach(link => {
//                 link.classList.toggle('text-f')
//             });
//         } else {
//             nav.classList.toggle('bg-white')
//             links.forEach(link => {
//                 link.classList.toggle('text-f')
//             });
//         }
//     });
// }, options)

// Observer.observe(banner)
//#endregion

//#region gallery
const linkBtns = document.querySelectorAll('.more-link')

linkBtns.forEach(link => {
    link.addEventListener('click', (e) => {
        ShowMore(link.getAttribute('data-class'), link.getAttribute('data-number'), e.target)
    })
});

function ShowMore(className, number, el=null) {
    var items = document.querySelectorAll(`.${className}.hidden`)
    let num = number
    if (num > items.length) {
        num = items.length
    }

    let i = 0
    items.forEach(element => {
        if (i < num) {
            element.classList.remove('hidden')
            element.classList.add('show')
            items = document.querySelectorAll(`.${className}.hidden`)
        }
        i++
    });
    
    if (items.length == 0 && el) {
        el.classList.add('hidden')
    }
    console.log(9);
}
//#endregion

//#region single page
const btn = document.getElementById('next-section-btn')
const nextSection = document.getElementById('next-section')

if (btn) {
    btn.addEventListener('click', () => {
        if (!nextSection.classList.contains('show')) {
            nextSection.parentElement.classList.remove('hidden')
            setTimeout(() => {
                nextSection.classList.add('show')
            }, 300)
        }
        nextSection.parentElement.scrollIntoView({
            behavior: 'smooth'
        })
    })
}
//#endregion

//#region car
const car = document.querySelector("img.car")
var previousPosn = 0
window.addEventListener('scroll', () => {
    // window.
})
//#endregion

