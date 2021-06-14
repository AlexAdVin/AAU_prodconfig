var processArray = [];

document.addEventListener('DOMContentLoaded', () => {

    // Request - response model to retrieve sensor data
    document.getElementById("save_btn").onclick = () => {
        // Initialize the AJAX request
        const request = new XMLHttpRequest();
        const processArray = processArray;
        request.open('POST', '/');

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
        request.send(processArray);
        return false;
    }

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