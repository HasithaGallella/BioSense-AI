import os
from http.server import BaseHTTPRequestHandler, HTTPServer
import time

host_name = ' 192.168.8.119'  # IP Address of Raspberry Pi
host_port = 8000

def setupGPIO():
    pass
    # GPIO.setmode(GPIO.BCM)
    # GPIO.setwarnings(False)
    # GPIO.setup(18, GPIO.OUT)
    # GPIO.setup(19, GPIO.IN)

spO2 = 67686786

def getSPO2():
    global spO2
    ##########
    spO2 += 1
    return str(spO2)

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
        if self.path == '/spo2':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            spo2_value = getSPO2()
            self.wfile.write(spo2_value.encode("utf-8"))
        else:
            html = '''
               <html>
               <head>
                   <script>
                       function updateSpO2() {
                           fetch('/spo2')
                               .then(response => response.text())
                               .then(data => {
                                   document.getElementById('spo2').innerHTML = data;
                               });
                       }
                       setInterval(updateSpO2, 1000); // Update every second
                   </script>
               </head>


               <body 
                style="width:960px; margin: 20px auto;">
               <h1>Welcome to BioSense-AI</h1>

               <form action="/" method="POST">
                   Stethoscope Analysis :
                   <input type="submit" name="submit" value="On">
                   <input type="submit" name="submit" value="Off">
               </form>

               <p>Patient's BPM level is <span id="spo2">Loading...</span></p>
               <p>Patient's Blood SpO2 level is <span id="spo2">Loading...</span></p>
               <p>Patient's stress level is <span id="spo2">Loading...</span></p>

               <h2>Patient ECG </h2>
               <canvas id="myChart" style="width:100%;max-width:700px"></canvas>
               

               <form action="/" method="POST">
                   Generate the AI-report :
                   <input type="submit" name="submit" value="Generate now">
               </form>
               </body>

                <script src="index.js">
                    // html = content , java script = behavior .... so separate these things in to bundle of files (js & html)
                    // console js script integration (separation of concerns)
                    // scr = source
                </script>

               
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
