var processArray = [];

document.addEventListener('DOMContentLoaded', () => {

    // Request - response model to retrieve sensor data
    document.getElementById("unobtn").onclick = () => {
        // Initialize the AJAX request
        const request = new XMLHttpRequest();
        request.open('POST', '/getValue');

        console.log(request);

        // Callback function when the requests completes 
        request.onload = () => {

            //Extract JSON data from request
            const data = JSON.parse(request.response);
            console.log(data);

            // Update the UI
            if(data.success) {
                const uno_read = `The sensor reads: ${data.rate}`;
                document.getElementById("uno_result").innerHTML = uno_read;
            }
            else {
                document.getElementById("uno_result").innerHTML = "There was an error"
            }
            
        }

        // Send request
        request.send();
        return false;
    }

// localStorage - save JSON
if (localStorage.processRecord){
  processArray = JSON.parse(localStorage.processRecord);
  for (var i=0; i < processArray.length; i++){

        var processName = processArray[i].processname;
        var processValue = processArray[i].processvalue;
        var ef_value = processArray[i].ef;
        var total_value = processArray[i].kgCO2e;
        generateTableCell(processName, processValue, ef_value, total_value);

  }
}

document.querySelector('#dynamic_form').onsubmit = () => {

  // Add new item to the table
  var processName = document.getElementById("process_name").value;
  var processValue = document.getElementById("process_value").value;
  var ef_value = document.getElementById("choice_EF").value;
  var kgCO2e_value = document.getElementById("x").value;

  var pObj2 = {processname:processName, 
              processvalue:processValue, 
              ef:ef_value, 
              kgCO2e:kgCO2e_value};
  processArray.push(pObj2);

  console.log(processArray);

  localStorage.processRecord = JSON.stringify(processArray);
  generateTableCell(processName, processValue, ef_value, kgCO2e_value);

  // Clear input field
  document.querySelector('#process_name').value = '';
  document.querySelector('#process_value').value = '';

  // Stop form from submitting
  return false;
};

});

// HTML Table - JavaScript update
function generateTableCell(processName, processValue, ef_value, total_value){

  // Create table
  var table = document.getElementById("user_table");
  var row = table.insertRow();

  var processIDCell = row.insertCell(0);
  var processNameCell = row.insertCell(1);
  var valueNameCell = row.insertCell(2);
  var efCell = row.insertCell(3);
  var resultCell = row.insertCell(4);
  var buttonCell = row.insertCell(5);


  processIDCell.innerHTML = "45";

  processNameCell.innerHTML = processName;
  valueNameCell.innerHTML = processValue;
  efCell.innerHTML = ef_value; 
  resultCell.innerHTML = total_value;

  buttonCell.innerHTML ='<input type="button" value="Delete" onclick="deleteRow(this)">';

}

// HTML deleteRow - JavaScript update
function deleteRow(r) {
  var i = r.parentNode.parentNode.rowIndex;

  // Remove object from JSON array:
  processArray.splice(i-3,1);

  // Delete row from the table/UI
  document.getElementById("user_table").deleteRow(i);
  
  delete localStorage.object[i];
}