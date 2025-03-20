let slideIndex = 1;


function plusSlides(n) {
    showSlides(slideIndex += n);
}


function currentSlide(n) {
    showSlides(slideIndex = n);
}

function showSlides(n) {
    let slides = document.getElementsByClassName("mySlides");
    let dots = document.getElementsByClassName("dot");

    if (n > slides.length) {
        slideIndex = 1;
    }

    if (n < 1) {
        slideIndex = slides.length;
    }
    
    for (let i = 0; i < slides.length; i++) {
        slides[i].style.display = "none";
    }

    for (let i = 0; i < dots.length; i++) {
        dots[i].className = dots[i].className.replace(" active", "" );
    }

    // slideIndex - 1 = 0, first img
    // slideIndex +0 = 1, second img
    // slideIndex +1 = 2, third img
    // slideIndex  +2 = 3, fourth img
    slides[slideIndex-1].style.display = 'block';

    dots[slideIndex-1].className += " active";
}

showSlides();