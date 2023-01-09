var app = {};
var htmldisp = "<br>";
var miCallback = function (datos) {
  app.usuarios = datos;
  app.usuarios.map((usuario) => {
    for (let propiedad of Object.keys(usuario)) {
      htmldisp += "<li>" + propiedad + ": " + usuario[propiedad] + "</li>";
    }
    htmldisp += "<hr/>";
  });
};

var bandera = 0;
var mostrarI = document.getElementById("mostrarI");
mostrarI.onclick = function (e) {
  e.preventDefault();
  if (bandera == 0) {
    document.getElementById("info").innerHTML = htmldisp;
    bandera = 1;
  } else {
    document.getElementById("info").innerHTML = htmldisp;
    bandera = 0;
  }
};

function validaVacio(valor) {
  valor = valor.replace("&nbsp;", "");
  valor = valor == undefined ? "" : valor;

  if (!valor || 0 === valor.trim().length) {
    return true;
  } else {
    return false;
  }
}
function validaForm() {
  var nom = document.getElementByName("name").value;
  var pass = document.getElementByName("pass").value;
  var correo = document.getElementByName("email").value;

  if (
    validaVacio(nom.value) ||
    validaVacio(pass.value) ||
    validaVacio(correo)
  ) {
    alert("Los campos no pueden estar vacios");
    return false;
  }
  return true;
}
