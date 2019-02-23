var curtemp = new TimeSeries();
var settemp = new TimeSeries();
var settempm = new TimeSeries();
var settempp = new TimeSeries();
var pterm = new TimeSeries();
var iterm = new TimeSeries();
var dterm = new TimeSeries();
var pidval = new TimeSeries();
var avgpid = new TimeSeries();
var lastreqdone = 1;
var timeout;

function refreshinputs() {
  $.getJSON({
    url: "/allstats",
    timeout: 500,
    success: function ( resp ) {
      $("#inputSetTemp").val( resp.settemp );
      $("#inputSleep").val( resp.sleep_time );
      $("#inputWake").val( resp.wake_time );
    }
  });
}

function resettimer() {
  clearTimeout(timeout);
  timeout = setTimeout(refreshinputs, 30000);
}

function onresize() {
    var h;
    if ($(window).height()*.50 > 450 ) {
      h = 450;
    } else {
      h = $(window).height()*.50;
    }

    $("#chart").attr("width", $("#fullrow").width()-30);
    $("#chart").attr("height", h);
    $("#pidchart").attr("width", $("#fullrow").width()-30);
    $("#pidchart").attr("height", h);

    if ($(document).width() < 600) {
      $("#toggleadv").html("Adv Stats");
    } else {
      $("#toggleadv").html("Advanced Stats");
    }
}

$(document).ready(function(){
  resettimer();
  $(this).mousemove(resettimer);
  $(this).keypress(resettimer);

  onresize();
  $(window).resize(onresize);

  createTimeline();

  $(".adv").hide();
  $("#toggleadv").click(function(){
    $(".adv").toggle();
  });

  refreshinputs();

  $("#inputSetTemp").change(function(){
    $.post(
      "/settemp", 
      { settemp: $("#inputSetTemp").val() } 
    );
  });

  $("#inputSleep").change(function(){
    $.post(
      "/setsleep",
      { sleep: $("#inputSleep").val() }
    );
  });

  $("#inputWake").change(function(){
    $.post(
      "/setwake",
      { wake: $("#inputWake").val() }
    );
  });

  $("#btnTimerDisable").click(function(){
    $.post("/scheduler",{ scheduler: "False" });
    $("#inputWake").hide();
    $("#labelWake").hide();
    $("#inputSleep").hide();
    $("#labelSleep").hide();
    $("#btnTimerDisable").hide();
    $("#btnTimerEnable").show();
  });

  $("#btnTimerEnable").click(function(){
    $.post("/scheduler",{ scheduler: "True" });
    $("#inputWake").show();
    $("#labelWake").show();
    $("#inputSleep").show();
    $("#labelSleep").show();
    $("#btnTimerDisable").show();
    $("#btnTimerEnable").hide();
  });

});

setInterval(function() {
  if (lastreqdone == 1) {
    $.getJSON({
      url: "/allstats",
      timeout: 500,
      success: function ( resp ) {
        if (resp.sched_enabled == true) {
         $("#inputWake").show();
         $("#inputSleep").show();
         $("#btnTimerSet").show();
         $("#btnTimerDisable").show();
         $("#btnTimerEnable").hide();
        } else {
         $("#inputWake").hide();
         $("#inputSleep").hide();
         $("#btnTimerSet").hide();
         $("#btnTimerDisable").hide();
         $("#btnTimerEnable").show();
        }
        curtemp.append(new Date().getTime(), resp.tempf);
        settemp.append(new Date().getTime(), resp.settemp);
        settempm.append(new Date().getTime(), resp.settemp-4);
        settempp.append(new Date().getTime(), resp.settemp+4);
        pterm.append(new Date().getTime(), resp.pterm);
        iterm.append(new Date().getTime(), resp.iterm);
        dterm.append(new Date().getTime(), resp.dterm);
        pidval.append(new Date().getTime(), resp.pidval);
        avgpid.append(new Date().getTime(), resp.avgpid);
        $("#curtemp").html(resp.tempf.toFixed(2));
        $("#pterm").html(resp.pterm.toFixed(2));
        $("#iterm").html(resp.iterm.toFixed(2));
        $("#dterm").html(resp.dterm.toFixed(2));
        $("#pidval").html(resp.pidval.toFixed(2));
        $("#avgpid").html(resp.avgpid.toFixed(2));
      },
      complete: function () {
        lastreqdone = 1;
      }
    });
    lastreqdone = 0;
  }
}, 100);

function createTimeline() {
  var chart = new SmoothieChart({grid:{verticalSections:3},minValueScale:1.05,maxValueScale:1.05});
  chart.addTimeSeries(settemp, {lineWidth:1,strokeStyle:'#ffff00'});
  chart.addTimeSeries(settempm, {lineWidth:1,strokeStyle:'#ffffff'});
  chart.addTimeSeries(settempp, {lineWidth:1,strokeStyle:'#ffffff'});
  chart.addTimeSeries(curtemp, {lineWidth:3,strokeStyle:'#ff0000'});
  chart.streamTo(document.getElementById("chart"), 500);

  var pidchart = new SmoothieChart({grid:{verticalSections:3},minValueScale:1.05,maxValueScale:1.05});
  pidchart.addTimeSeries(pterm, {lineWidth:2,strokeStyle:'#ff0000'});
  pidchart.addTimeSeries(iterm, {lineWidth:2,strokeStyle:'#00ff00'});
  pidchart.addTimeSeries(dterm, {lineWidth:2,strokeStyle:'#0000ff'});
  pidchart.addTimeSeries(pidval, {lineWidth:2,strokeStyle:'#ffff00'});
  pidchart.addTimeSeries(avgpid, {lineWidth:2,strokeStyle:'#ff00ff'});
  pidchart.streamTo(document.getElementById("pidchart"), 500);
}
