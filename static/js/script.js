// tabs

var tabLinks = document.querySelectorAll(".tablinks");
var tabContent = document.querySelectorAll(".tabcontent");


tabLinks.forEach(function(el) {
   el.addEventListener("click", openTabs);
});


function openTabs(el) {
   var btnTarget = el.currentTarget;
   var country = btnTarget.dataset.country;

   tabContent.forEach(function(el) {
      el.classList.remove("active");
   });

   tabLinks.forEach(function(el) {
      el.classList.remove("active");
   });

   document.querySelector("#" + country).classList.add("active");
   
   btnTarget.classList.add("active");
}

// var table = new Tabulator("#example-table", {
//    height:"311px",
//    responsiveLayout:"hide",
//    columns:[
//    {title:"Name", field:"name", width:200, responsive:0}, //never hide this column
//    {title:"Progress", field:"progress", hozAlign:"right", sorter:"number", width:150},
//    {title:"Gender", field:"gender", width:150, responsive:2}, //hide this column first
//    {title:"Rating", field:"rating", hozAlign:"center", width:150},
//    {title:"Favourite Color", field:"col", width:150},
//    {title:"Date Of Birth", field:"dob", hozAlign:"center", sorter:"date", width:150},
//    {title:"Driver", field:"car", hozAlign:"center", width:150},
//    ],
// });