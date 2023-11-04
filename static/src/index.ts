import './main.scss'
import './fontawesome/css/all.min.css'

import './js/main.js'
import './js/scroll.js'

import "./ts/alpine"

import Alpine from 'alpinejs'
import { gsap } from "gsap";
import ScrollTrigger from "gsap/ScrollTrigger";

Alpine.start()


// transitions on scroll
gsap.registerPlugin(ScrollTrigger);

class CardAnimation {
    static init() {
        const fadeInElements = document.querySelectorAll(".fade-in");
        const slideInLeftElements = document.querySelectorAll(".slide-in-left");
        const slideInRightElements = document.querySelectorAll(".slide-in-right");
        const slideInTopElements = document.querySelectorAll(".slide-in-top");

        gsap.set('.fade-in', { opacity: 0 })
        gsap.set('.slide-in-left', { opacity: .5, x: -100 })
        gsap.set('.slide-in-right', { opacity: .5, x: 100 })
        gsap.set('.slide-in-top', { opacity: .5, y: 100 })

        const observerOptions = {
            threshold: 0.2, // Intersection threshold (20% of the element must be visible)
        };

        // Intersection Observer for fade-in and slide-in from the left
        const observer = new IntersectionObserver(entries => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    // Fade in and slide in from the left for elements with class "fade-in" and "slide-in-left"
                    if (entry.target.classList.contains("fade-in")) {
                        gsap.to(entry.target, {
                            opacity: 1, // Start with opacity 0 (fade in effect)
                            duration: .5,
                        });
                    }
                    if (entry.target.classList.contains("slide-in-left")) {
                        gsap.to(entry.target, {
                            x: 0, // Move element from the left (slide in from the left)
                            opacity: 1, // Start with opacity 0 (fade in effect)
                            duration: .5,
                        });
                    }
                    // Slide in from the right for elements with class "slide-in-right"
                    if (entry.target.classList.contains("slide-in-right")) {
                        gsap.to(entry.target, {
                            x: 0, // Move element from the right (slide in from the right)
                            opacity: 1, // Start with opacity 0 (fade in effect)
                            duration: .5,
                        });
                    }
                    if (entry.target.classList.contains("slide-in-top")) {
                        gsap.to(entry.target, {
                            y: 0, // Move element from the right (slide in from the right)
                            opacity: 1, // Start with opacity 0 (fade in effect)
                            duration: .5,
                        });
                    }

                    observer.unobserve(entry.target); // Stop observing once animated
                }
                setTimeout(function () {}, 1000);
            });
        }, observerOptions);

        // Start observing elements for fade-in and slide-in animations
        fadeInElements.forEach(element => {
            observer.observe(element);
        });
        slideInLeftElements.forEach(element => {
            observer.observe(element);
        });
        slideInRightElements.forEach(element => {
            observer.observe(element);
        });
        slideInTopElements.forEach(element => {
            observer.observe(element);
        });
    }
}

// Initialize the animations when the DOM is ready
document.addEventListener("DOMContentLoaded", () => {
    CardAnimation.init();
});



document.getElementById('loader')?.classList.add('opacity-0', 'pointer-events-none')