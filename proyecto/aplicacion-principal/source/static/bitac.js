var app={};
var html = "<br>";
var miCallback = function (datos) {
	app.registros=datos;
	app.registros.map(registro => {
		for(let propiedad of Object.keys(registro)){
			html+="<li>"+propiedad+": "+registro[propiedad]+"</li>";
		}
		html+="<hr/>";
	})
}

/*var cargar = document.getElementById("cargar");
cargar.onclick = function(e){
	e.preventDefault();
	document.getElementById("bitacora").innerHTML = html;
}

var borrar = document.getElementById("borrar");
borrar.onclick = function(e){
	e.preventDefault();
	document.getElementById("bitacora").innerHTML = "";
}*/
function ocultar(){
	document.getElementById('tablaB').style.display = "none";
	document.getElementById('tablaB2').style.display = "none";
	document.getElementById('tablaB3').style.display = "none";
}
function mostrar(){
	document.getElementById('tablaB').style.display = "block";
	document.getElementById('tablaB2').style.display = "block";
	document.getElementById('tablaB3').style.display = "block";
}