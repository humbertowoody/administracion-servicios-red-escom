var app={};
var htmldisp = "<br>";
var miCallback = function (datos) {
	app.dispositivos=datos;
	app.dispositivos.map(dispositivo => {
		for(let propiedad of Object.keys(dispositivo)){
			htmldisp+="<li>"+propiedad+": "+dispositivo[propiedad]+"</li>";
		}
		htmldisp+="<hr/>";
	})
}
var bandera = 0;
var mostrarI = document.getElementById("mostrarI");
mostrarI.onclick = function(e){
	e.preventDefault();
	if(bandera == 0){
		document.getElementById("info").innerHTML = htmldisp;
		bandera = 1;
	}else{
		document.getElementById("info").innerHTML = "";
		bandera = 0;
	}
}
var mostrarU = document.getElementById("mostrarU");
var v=1;
mostrarU.onclick=function invisible(){
	if(v==1){
		document.getElementById("us").style.visibility = 'visible';
		v=0;
	}else{
		document.getElementById("us").style.visibility = 'hidden';
		v=1;
	}
}