var table = document.querySelector(".dataframe.data");

// Získání hodnoty z prvního řádku a druhého sloupce
if (table) {
  console.log("ADDSS");
  var firstRow = table.querySelector("tbody tr:nth-child(1)");
  var lastRow = table.querySelector("tbody tr:last-child");
  var min = firstRow.querySelector("td:nth-child(2)").innerText;
  var formatted_min = convert_date(min);
  var max = lastRow.querySelector("td:nth-child(2)").innerText;
  var formatted_max = convert_date(max);
  var dateTimeInput = document.getElementById("date_time_input"); //ANNOTATION
  dateTimeInput.min = formatted_min;
  dateTimeInput.max = formatted_max;
  console.log("sdasds");
  var date_time_start = document.getElementById("date_time_start"); // CHART RANGE - START
  date_time_start.min = formatted_min;
  date_time_start.max = formatted_max;
  var date_time_end = document.getElementById("date_time_end"); // CHART RANGE - END
  date_time_end.min = formatted_min;
  date_time_end.max = formatted_max;
  console.log(
    "Hodnota z prvního řádku a druhého sloupce:" + formatted_min + " do " + max
  );
} else {
  console.error("Tabulka nebyla nalezena.");
}

function convert_date(date_time) {
  var day = date_time.substring(0, 2);
  var month = date_time.substring(3, 5);
  var year = date_time.substring(6, 10);
  var hours = date_time.substring(11, 13);
  var minutes = date_time.substring(14, 16);
  var seconds = date_time.substring(17, 19);

  return year + "-" + month + "-" + day + "T" + hours + ":" + minutes;
}
