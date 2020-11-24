from http.server import BaseHTTPRequestHandler, HTTPServer
import codecs
import logging
from google.cloud import firestore
from datetime import datetime

class S(BaseHTTPRequestHandler):
    xyz = {
        "accelData" : {
        "x" : [],
        "y" : [],
        "z" : [],
        "t" : []
    }
    }
    exercise = "test"

    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_POST(self):
        content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
        post_data = self.rfile.read(content_length) # <--- Gets the data itself
        self.analyzeData(post_data.decode('utf-8'))
        logging.info("POST request,\nPath: %s\nHeaders:\n%s\n\nBody:\n%s\n",
                str(self.path), str(self.headers), post_data.decode('utf-8'))

        self._set_response()
        self.wfile.write("POST request for {}".format(self.path).encode('utf-8'))

    def do_GET(self):
        self.send_response(200, 'OK')
        self.send_header('Content-type', 'html')
        self.end_headers()
        indexhtml = codecs.open("index.html", "r", "utf-8")
        self.wfile.write(bytes(indexhtml.read(),"utf-8"))
    
    def analyzeData(self, data):
        if (data == "done"):
            #add date
            self.xyz["date"] = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")

            #get data and move it to firebase
            db = firestore.Client()

            db.collection("awaldron12@outlook.com").document("NodeMCUWorkouts").collection(self.exercise).add(self.dataToFloat())

            #reset data
            self.xyz["accelData"]["x"] = []
            self.xyz["accelData"]["y"] = []
            self.xyz["accelData"]["z"] = []
            self.xyz["accelData"]["t"] = []
        else:
            #split on /
            dataPoints = data.split("/")
            dataPoints.pop()
            for dataPoint in dataPoints:
                splitDataList = dataPoint.split()
                #add data to current
                
                self.xyz["accelData"]["x"].append(splitDataList[0])
                self.xyz["accelData"]["y"].append(splitDataList[1])
                self.xyz["accelData"]["z"].append(splitDataList[2])
                self.xyz["accelData"]["t"].append(splitDataList[3])
            
    def dataToFloat(self):
        xyzt = ["x","y","z","t"]
        for key in xyzt:
            self.xyz["accelData"][key] = [float(x) for x in self.xyz["accelData"][key]]
        return self.xyz
if __name__ == "__main__":
    httpd = HTTPServer(('10.0.0.12',8000), S)
    httpd.serve_forever()