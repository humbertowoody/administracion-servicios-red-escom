
var html = "<br>";
var miCallback = function (datos) {
	const registros = datos;
	var router = document.getElementById("routers").value;
	var keys;
	var xValues = ["paquetes enviados y recividos", "paquetes dañados", "paquetes perdidos"];
	var yValues = [];
	var barColors = ["green", "red", "blue"];
	for(var i=0; i< registros.length; i++){
		if(router == registros[i].host){
			yValues.push(registros[i].eyr); 
			yValues.push(registros[i].dañados); 
			yValues.push(registros[i].perdidos); 
		}
	}
	if(router != "null"){
		new Chart("myChart", {
			type: "doughnut",
			data: {
				labels: xValues,
				datasets: [{
					backgroundColor: barColors,
					data: yValues
				}]
			},
			options: {
				legend: {
					//display: true,
					fontSize: 16,
					//fontColor: "red",
				},
				title:{
					display: true,
					text: "Estadisticas de "+router,
					fontSize: 16,
					fontColor: "black"
				}
			}
		});
	}
}