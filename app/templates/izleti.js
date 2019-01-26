
function AdvanceSearch(){
	if(document.getElementById("search").value != " "){
		console.log("skdjfnkdfsj");
		document.getElementById("advanced_button").style.display = "block";
	}
	
	document.getElementById("advanced_button").onclick = function PokaziAdvance(){
		document.getElementById("advanced").style.display = "block";
		document.getElementById("advanced_button").style.display = "none";
	}

	/*button.addEventListener('click', function (){
			bar.style.display = "block";
			button.style.display = "none";
	})*/
}