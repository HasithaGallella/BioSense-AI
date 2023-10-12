import os
from http.server import BaseHTTPRequestHandler, HTTPServer
import random

host_name = '192.168.8.119'  # IP Address of Raspberry Pi
host_port = 8000


def setupGPIO():
    pass
    # GPIO.setmode(GPIO.BCM)
    # GPIO.setwarnings(False)
    # GPIO.setup(18, GPIO.OUT)
    # GPIO.setup(19, GPIO.IN)

spO2 =67686786

def getSPO2():
    # spO2 = spO2+1
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
        html = '''
           <html>
           <body 
            style="width:960px; margin: 20px auto;">
           <h1>Welcome to my Raspberry Pi</h1>
           <p>Patient's Blood SpO2 level is {}</p>
           <form action="/" method="POST">
               Turn LED :
               <input type="submit" name="submit" value="On">
               <input type="submit" name="submit" value="Off">
           </form>
           </body>
           </html>
        '''
        MyspO2 = getSPO2()
        self.do_HEAD()
        self.wfile.write(html.format(MyspO2[:]).encode("utf-8"))

    def do_POST(self):
        spO2 = 12345

        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode("utf-8")
        post_data = post_data.split("=")[1]

        setupGPIO()

        if post_data == 'On':
            print("Pi_LED will on")
            spO2 = spO2+1
            # GPIO.output(18, GPIO.HIGH)
        else:
            print("Pi_LED will off")
            # GPIO.output(18, GPIO.LOW)

        print("LED is {}".format(post_data))
        self._redirect('/')  # Redirect back to the root url


# # # # # Main # # # # #

if __name__ == '__main__':
    spO2 = 67686786
    http_server = HTTPServer((host_name, host_port), MyServer)
    print("Server Starts - %s:%s" % (host_name, host_port))

    try:
        http_server.serve_forever()
    except KeyboardInterrupt:
        http_server.server_close()