const open_button = document.getElementById("open_button");

open_button.addEventListener("click",()=>{
    const info_map = document.querySelector(".info_map");
    info_map.classList.toggle("active");
})