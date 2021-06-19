const open_button = document.getElementById("open_button");

open_button.addEventListener("click",()=>{
    const info_map = document.querySelector(".info_map");
    info_map.classList.toggle("active");
})



window.addEventListener('load',activateLoader())

function activateLoader(){
    const loader = document.querySelector('.loader');
    loader.classList.add("hidden");
}

document.getElementById("form_geojud").addEventListener("submit",()=>{
  
    const loader = document.querySelector('.loader');
    loader.classList.remove("hidden");
})