/** index **/
var v=1;
function invisible(){
	if(v==1){
		document.getElementById("tiempo").style.visibility = 'visible';
		v=0;
	}else{
		document.getElementById("tiempo").style.visibility = 'hidden';
		v=1;
	}
}

/** Enrutamiento **/
function dis(elemento){
	var d = elemento.value
	if(d == "null"){
		elemento.disabled = false;
	}else{
		elemento.disabled = true;
	}
}
function ena(elemento){
	elemento.disabled = true;
}
function defa(){
	var select = document.getElementById("tipoER");
	ena(select);
}
function setEnru(){
	var html = "<br>";
	var select = document.getElementById("tipoER");
	/*var indice = select.selectedIndex;
	var valor = select.options[indice].value;*/
	var valor = select.value;
	if(valor == "null"){
		alert("Seleccione un tipo de enrutamiento");
	}else if(valor == "RIP" || valor == "EIGRP"){
		html += "<form action='' method='POST'>";
		html += "<p><label id='text'> network: </label>";
		html += "<input type='text' name='network'/></p>";
		html += "<p><label id='text'> Auto-summary: </label>";
		html += "<input type='radio' name='auto' value='Y' /> Yes";
		html += "<input type='radio' name='auto' value='N' /> No";
		html += "</p><input type='submit' id='send-signup' name='signup' value='Aceptar' class='Boton' onclick='ena(select)'/>";
		html += "</form>";
		document.getElementById("ER").innerHTML = html;
	}else if(valor == "OSPF"){
		html += "<form action='' method='POST'>";
		html += "<label id='text'> Loopback </label>";
		html += "<p><label id='text'> network: </label>";
		html += "<input type='text' name='netloop'/></p>";
		html += "<label id='text'> OSPF </label>";
		html += "<p><label id='text'> network: </label>";
		html += "<input type='text' name='network'/></p>";
		html += "<p><label id='text'> wildcard: </label>";
		html += "<input type='text' name='wildcard'/></p>";
		html += "<p><label id='text'> area: </label>";
		html += "<input type='number' min='0' name='area'/></p>";
		html += "<input type='submit' id='send-signup' name='signup' value='Aceptar' class='Boton' onclick='ena(select)'/>";
		html += "</form>";
		document.getElementById("ER").innerHTML = html;
	}
}