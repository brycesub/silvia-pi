var curtemp = new TimeSeries();
var settemp = new TimeSeries();
var settempm = new TimeSeries();
var settempp = new TimeSeries();
var pterm = new TimeSeries();
var iterm = new TimeSeries();
var dterm = new TimeSeries();
var pidval = new TimeSeries();
var avgpid = new TimeSeries();
var xhttp = new XMLHttpRequest();

setInterval(function() {
  xhttp.open("GET", "./allstats", false);
  xhttp.send();
  var resp = JSON.parse(xhttp.responseText);
  curtemp.append(new Date().getTime(), resp.tempf);
  settemp.append(new Date().getTime(), resp.settemp);
  settempm.append(new Date().getTime(), resp.settemp-4);
  settempp.append(new Date().getTime(), resp.settemp+4);
  pterm.append(new Date().getTime(), resp.pterm);
  iterm.append(new Date().getTime(), resp.iterm);
  dterm.append(new Date().getTime(), resp.dterm);
  pidval.append(new Date().getTime(), resp.pidval);
  avgpid.append(new Date().getTime(), resp.avgpid);
  document.getElementById("curtemp").innerHTML = resp.tempf.toFixed(2);
  document.getElementById("settemp").innerHTML = resp.settemp.toFixed(2);
  document.getElementById("pterm").innerHTML = resp.pterm.toFixed(2);
  document.getElementById("iterm").innerHTML = resp.iterm.toFixed(2);
  document.getElementById("dterm").innerHTML = resp.dterm.toFixed(2);
  document.getElementById("pidval").innerHTML = resp.pidval.toFixed(2);
  document.getElementById("avgpid").innerHTML = resp.avgpid.toFixed(2);
}, 200);

function createTimeline() {
  var chart = new SmoothieChart({grid:{verticalSections:3},minValueScale:1.05,maxValueScale:1.05}),
    canvas = document.getElementById('chart'),
    series = new TimeSeries();

  chart.addTimeSeries(settemp, {lineWidth:1,strokeStyle:'#ffff00'});
  chart.addTimeSeries(settempm, {lineWidth:1,strokeStyle:'#ffffff'});
  chart.addTimeSeries(settempp, {lineWidth:1,strokeStyle:'#ffffff'});
  chart.addTimeSeries(curtemp, {lineWidth:3,strokeStyle:'#ff0000'});
  chart.streamTo(document.getElementById("chart"), 500);

  var pidchart = new SmoothieChart({grid:{verticalSections:3},minValueScale:1.05,maxValueScale:1.05}),
    canvas = document.getElementById('pidchart'),
    series = new TimeSeries();

  pidchart.addTimeSeries(pterm, {lineWidth:2,strokeStyle:'#ff0000'});
  pidchart.addTimeSeries(iterm, {lineWidth:2,strokeStyle:'#00ff00'});
  pidchart.addTimeSeries(dterm, {lineWidth:2,strokeStyle:'#0000ff'});
  pidchart.addTimeSeries(pidval, {lineWidth:2,strokeStyle:'#ffff00'});
  pidchart.addTimeSeries(avgpid, {lineWidth:2,strokeStyle:'#00ffff'});
  pidchart.streamTo(document.getElementById("pidchart"), 500);
}

var advstate = "hidden";

function toggleAdv() {
  var advclass = document.getElementsByClassName('adv');
  if (advstate == "hidden") {
    advstate="visible";
    document.getElementById('toggleadv').innerHTML = "Hide Advanced Stats"
  } else {
    advstate="hidden";
    document.getElementById('toggleadv').innerHTML = "Show Advanced Stats"
  }
  for (i=0; i<advclass.length; i++) {
    advclass[i].style.visibility=advstate;
  }
}
