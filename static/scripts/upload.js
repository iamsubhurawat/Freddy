const dragarea=document.querySelector('.drag-area');
const dragareatext=document.querySelector('.header');
let button=document.querySelector('.button');
let input=document.querySelector('input');
let pdf_file;

button.onclick = function() {
    input.click();
};

input.addEventListener('change',(e)=>{
    console.log("HEllo")
    pdf_file = e.target.files[0];
    console.log(typeof(pdf_file));
    sendFileToServer(pdf_file);
});

dragarea.addEventListener('dragover',(event)=>{
    event.preventDefault();
    dragareatext.textContent = "Release to Upload";
    dragarea.classList.add('active');
});

dragarea.addEventListener('dragleave',()=>{
    dragareatext.textContent = "Drag & Drop";
    dragarea.classList.remove('active');
});

dragarea.addEventListener('drop',(event)=>{
    event.preventDefault();
    pdf_file = event.dataTransfer.files[0];
    sendFileToServer(pdf_file);
});

function sendFileToServer(file) {
    const formData = new FormData();
    formData.append('pdf_file',file);
    fetch('/upload',{
        method: 'POST',
        body: formData,
        redirect: 'follow'
    })
    .then(response => response.json())
    .then(data => {
        window.location.href = data.redirect_url;
    })
    .catch(error => console.error(error));
}