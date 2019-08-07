
// Retorna à página anterior
function goBack() {
    window.history.back();
}

// Adiciona função "onClick" de ir à página anterior no elemento de id "goback_button"
document.addEventListener("DOMContentLoaded", function (event) {
    document.getElementById('goback_button').addEventListener('click', goBack);
});
