

function Toggle() {


    let hamNav = document.querySelector(".ham-nav");
    let sideItem = document.querySelector(".sidebar-item");
    let hamIcon = document.querySelector(".ham-icon");


    if (hamNav.className == "ham-nav")  {

        hamNav.className += " active";
        sideItem.className += " active";
        hamIcon.src = "../img/ham-open.svg"

    }else {
        hamNav.className = "ham-nav";
        sideItem.className = "sidebar-item";
         hamIcon.src = "../img/ham-close.svg"
    }
    
}

let hamNav = document.querySelector(".ham-nav");

hamNav.addEventListener("click", Toggle);