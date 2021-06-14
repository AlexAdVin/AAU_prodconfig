document.addEventListener('DOMContentLoaded',function() {
    console.log("LOADED!");
    
    var data1 = {'sql': 'SELECT DISTINCT "Minutes5DK", "CO2Emission" FROM "co2emis" \
                            ORDER BY "Minutes5DK" DESC LIMIT 1'};
  
    $.ajax({
        url: 'https://www.energidataservice.dk/proxy/api/datastore_search_sql',
        type: "GET",
        data: data1,
        dataType: 'jsonp',
        success: function(data) {
          //console.log("success:", data.result.records[0]['CO2Emission'])
          document.getElementById('CO2e_now').innerHTML = data.result.records[0]['CO2Emission'];
          document.getElementById('t_stamp_now').innerHTML = data.result.records[0]['Minutes5DK'];
        }
    });
});
