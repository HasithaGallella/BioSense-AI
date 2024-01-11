import os
from http.server import BaseHTTPRequestHandler, HTTPServer
import time
from random import randint

host_name = '192.168.8.119'  # IP Address of Raspberry Pi
host_port = 8000

def setupGPIO():
    pass
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(18, GPIO.OUT)
    GPIO.setup(19, GPIO.IN)

state = 'Normal'
stress= 'High'
spO2 = 97
bpm = 105

def getState():
    global state
    return state

def getStress():
    Numbers = [95,99,102,104,92]
    random_number = randint(0,4)
    if Numbers[random_number] > 100:
        return 'Very High'
    else:
        return 'High'

def getSPO2():
    global spO2
    spO2 += 1
    return str(spO2)

def getBPM():
    Numbers = [95,99,102,104,92]
    random_number = randint(0,4)
    return str(Numbers[random_number])

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
            state_value = getState()
            self.wfile.write(state_value.encode("utf-8"))
        if self.path == '/stress_page':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            stress_value = getStress()
            self.wfile.write(stress_value.encode("utf-8"))
        elif self.path == '/spo2_page':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            spo2_value = getSPO2()
            self.wfile.write(spo2_value.encode("utf-8")) 
        elif self.path == '/bpm_page':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            bpm_value = getBPM()
            self.wfile.write(bpm_value.encode("utf-8"))    
        else:
            html = '''
<html>

<head>
    <script
    src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/2.9.4/Chart.js">
    </script>
</head>


<body 
 style="width:960px; margin: 20px auto; background-color: #76b9e8; overflow: hidden; padding: 20px;">
<h1>Welcome to BioSense-AI</h1>

<canvas id="StressChart" style="width:100%;max-width:600px"></canvas>

<p>Patient's State : <span id="person_id">Loading...</span></p>
<p>Patient's stress level is <span id="stress_id">Loading...</span> % </p>

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

<h6> ECG signal of the Patient </h6>
<canvas id="myChart" style="width:100%;max-width:600px"></canvas>

<form action="/" method="POST">
    Generate the AI-report :
    <input type="submit" name="submit" value="Generate now">
</form>






<script>
     function updateValues() {
         fetch('/person_id')
             .then(response => response.text())
             .then(data => {
                 document.getElementById('person_id').innerHTML = data;
             });

         fetch('/stress_id')
             .then(response => response.text())
             .then(data => {
                 document.getElementById('stress_id').innerHTML = data;
             });

          fetch('/spo2_id')
             .then(response => response.text())
             .then(data => {
                 document.getElementById('spo2_id').innerHTML = data;
             });
             
           fetch('/bpm_id')
             .then(response => response.text())
             .then(data => {
                 document.getElementById('bpm_id').innerHTML = data;
             });           


     }
     setInterval(updateValues, 1000); // Update every second
</script>


<script>
    var xValues = ["Stressed", "Charam"];
    var yValues = [51, 49];
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
          text: "World Wide Wine Production 2018"
        }
      }
    });
    </script>

 <script>
 const xValues = [100,200,300,400,500,600,700,800,900,1000];

 new Chart("myChart", {
 type: "line",
 data: {
     labels: xValues,
     datasets: [{ 
     data: [860,1140,1060,1060,1070,1110,1330,2210,7830,2478],
     borderColor: "red",
     fill: false
     }, { 
     data: [1600,1700,1700,1900,2000,2700,4000,5000,6000,7000],
     borderColor: "green",
     fill: false
     }, { 
     data: [300,700,2000,5000,6000,4000,2000,1000,200,100],
     borderColor: "blue",
     fill: false
     }]
 },
 options: {
     legend: {display: false}
 }
 });
 </script>              


 <script src="index.js"></script>
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
            print("Pi_LED will on")
            # GPIO.output(18, GPIO.HIGH)

        else:
            print("Pi_LED will off")
            # GPIO.output(18, GPIO.LOW)

        print("LED is {}".format(post_data))
        self._redirect('/')  # Redirect back to the root url

# # # # # Main # # # # #

if __name__ == '__main__':
    http_server = HTTPServer((host_name, host_port), MyServer)
    print("Server Starts - %s:%s" % (host_name, host_port))

    try:
        http_server.serve_forever()
    except KeyboardInterrupt:
        http_server.server_close()
