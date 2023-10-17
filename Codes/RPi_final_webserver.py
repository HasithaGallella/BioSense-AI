#!/usr/bin/env python3

import RPi.GPIO as GPIO
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from random import randint

host_name = '10.10.0.211'  # IP Address of Raspberry Pi
host_port = 8000

def setupGPIO():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(18, GPIO.OUT)
    GPIO.setup(19, GPIO.IN)

spO2 = 97
bpm = 105
state = 'Normal'

def getState():
    global state
    return state

def getSPO2():
    Numbers = [97,98,99,100,95]
    random_number = randint(0,4)
    return str(Numbers[random_number])

def getTemp():
    Numbers = [97, 99, 102, 104, 92]
    random_number = randint(0, 4)
    if Numbers[random_number] > 100:
        return 'High'
    else:
        return 'Very High'

class MyServer(BaseHTTPRequestHandler):

    def do_HEAD(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def _redirect(self, path):
        self.send_response(303)
        self.send_header('Content-type', 'text/html')
        self.send_header('Location', path)
        self.end_headers()

    def do_GET(self):
                
        if self.path == '/state_page':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            spo2_value = getState()
            self.wfile.write(spo2_value.encode("utf-8"))

        elif self.path == '/spo2':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            spo2_value = getSPO2()
            self.wfile.write(spo2_value.encode("utf-8"))

        elif self.path == '/temp':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            temp_value = getTemp()
            self.wfile.write(temp_value.encode("utf-8"))
        else:
            html = '''
<html>

<head>
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/2.9.4/Chart.js"></script>
</head>


<body 
style="width:960px; margin: 20px auto; background-color: lightblue; padding: 20px;">
<h1>Welcome to BioSense-AI</h1>

<canvas id="StressChart" style="width:100%;max-width:600px"></canvas>

<p>Patient's State : <span id="person_id">Loading...</span></p>
<p>Patient's stress level is <span id="stress_id">Loading...</span> % </p>

<br></br>

<form action="/" method="POST">
    Turn SpO2 Sensor ON/OFF:
    <input type="submit" name="submit" value="On">
    <input type="submit" name="submit" value="Off">
    <p>Patient's Blood SpO2 level is <span id="spo2_id">Loading...</span></p>
    <p>Patient's BPM level is <span id="bpm_id">Loading...</span></p>
    <br><br>
    Stethoscope Analysis :
    <input type="submit" name="submit" value="Connect">
    <p>Predictions from Steathascope report: Loading...</span></p>

</form>


<h4> ECG signal of the Patient </h4>
<canvas id="myChart" style="width:100%;max-width:700px"></canvas>
<br></br>
<form action="/" method="POST">
    Generate the AI-report :
    <input type="submit" name="submit" value="Generate now">
</form>


<script> //updateVals chart
    function updateValues() {
        fetch('/state_page')
            .then(response => response.text())
            .then(data => {
                document.getElementById('person_id').innerHTML = data;
            });
        fetch('/spo2')
            .then(response => response.text())
            .then(data => {
                document.getElementById('spo2_id').innerHTML = data;
            });       
        fetch('/temp')
            .then(response => response.text())
            .then(data => {
                document.getElementById('stress_id').innerHTML = data;
            });
    }
    setInterval(updateValues, 1000); // Update every second
</script>


<script> //Stress chart
    var xValues = ["Stressed", "Charam"];
    var yValues = [78, 22];
    var barColors = [
      "#b91d47",
      "#2b5797"
    ];
    
    new Chart("StressChart", {
      type: "doughnut",
      data: {
        labels: xValues,
        datasets: [{
          backgroundColor: barColors,
          data: yValues
        }]
      },
      options: {
        title: {
          display: true,
          text: "Based on Patients SpO2 and BPM Analysis"
        }
      }
    });
</script>


<script> //ECG chart
xValues = [100,200,300,400,500,600,700,800,900,1000];
yValues = [860,1140,1060,1060,1070,1110,1330,2210,7830,2478];

// Function to update the chart
function updateChartData() {
    yValues.push(Math.floor(Math.random() * 2000) + 800);  // Generate random values
    xValues.push(xValues[xValues.length - 1] + 1000);
    if (yValues.length > 10) {
        yValues.shift();
        xValues.shift();
    }
    chart.update();
}

const chart = new Chart("myChart", {
    type: "line",
    data: {
        labels: xValues,
        datasets: [{
            data: yValues,
            borderColor: "red",
            fill: false,
        }],
    },
    options: {
        legend: {display: false}
    },
});

setInterval(updateChartData, 1000);
</script>
</body>
</html>
            '''

            self.do_HEAD()
            self.wfile.write(html.encode("utf-8"))

    def do_POST(self):

        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode("utf-8")
        post_data = post_data.split("=")[1]

        setupGPIO()

        if post_data == 'On':
            GPIO.output(18, GPIO.HIGH)
        else:
            GPIO.output(18, GPIO.LOW)

        print("LED is {}".format(post_data))
        self._redirect('/')

if __name__ == '__main__':
    http_server = HTTPServer((host_name, host_port), MyServer)
    print("Server Starts - %s:%s" % (host_name, host_port))

    try:
        http_server.serve_forever()
    except KeyboardInterrupt:
        http_server.server_close()
