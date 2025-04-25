function generateSheet(){
  let sheetUrl = ""
  let sheetCode = ""
  let dataArray = []
  let dataArrayFormatted = ""
  document.getElementById("id01").innerHTML = ""
  var xmlhttp = new XMLHttpRequest();
  sheetUrl = document.getElementById("sheetUrl").value;
  for (i=0;i<sheetUrl.length;i++){
    if (sheetUrl[i] == "/" && sheetUrl[i-1] == "d" && sheetUrl[i-2] == "/"){
      for (j=i+1;j<sheetUrl.length;j++){
        sheetCode += sheetUrl[j]
        if (sheetUrl[j+1] === "/") { break; }
      }
    }
  }
  if(sheetCode == ""){ 
    document.getElementById("id01").innerHTML += "Incorrect URL"
  }
  var url = "https://spreadsheets.google.com/feeds/cells/" + sheetCode + "/1/public/full?alt=json"
  
  xmlhttp.onreadystatechange = function() {
    setTimeout(function(){
      if(document.getElementById("id01").innerHTML == ""){
        document.getElementById("id01").innerHTML = 'Unable to load data. Please go to "File > Publish To Web" on your Google Sheets page and ensure that it is published.'
      }
    }, 1500)
    if (this.readyState == 4 && this.status == 200) {
      var siteJson = JSON.parse(this.responseText)
      document.getElementById("id01").innerHTML += siteJson.feed.title.$t + ":<br>";
      for (let i=0; i<siteJson.feed.entry.length; i++){
          if(!Array.isArray(dataArray[siteJson.feed.entry[i].gs$cell.row-1])){
            dataArray[siteJson.feed.entry[i].gs$cell.row-1] = []
          }
          dataArray[siteJson.feed.entry[i].gs$cell.row-1][siteJson.feed.entry[i].gs$cell.col-1] = siteJson.feed.entry[i].gs$cell.inputValue 
      }
     arrayFormat()
    }
  }
  xmlhttp.open("GET", url, true)
  xmlhttp.send()
  function arrayFormat(){ 
    for (i=0; i<dataArray.length; i++){
      document.getElementById("id01").innerHTML += "["
      if(dataArray[i]){
        for (j=0; j<dataArray[i].length; j++){
          let contents= ""
          if(dataArray[i][j]){
             contents = dataArray[i][j] 
          }
          document.getElementById("id01").innerHTML += "[" + contents + "]"
        }
      }
      document.getElementById("id01").innerHTML += "] <br>"
    }
  }
}
