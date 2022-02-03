
import socket
import os
import mimetypes
import multiprocessing, subprocess,sys

class HTTPServer:
    def __init__(self,host,port):
        self.host=host
        self.port=port
        # Create a TCP/IP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (self.host, self.port)
        print('starting up on %s port %s' % server_address)
        sock.bind(server_address)

        sock.listen(1)

        while True:
            print('waiting for a connection')
            connection, client_address = sock.accept()
            print('connection from', client_address)
            server(connection)

def response(response_statuscode,response_headers):
    response_headers_raw = ''.join('%s: %s\n' % (k, v) for k, v in response_headers.items())
    response=[response_statuscode,response_headers_raw]
    response_raw=''.join('%s\n' %(item) for item in response)
    return response_raw

def server(connection):
    cwd=os.getcwd()
    data = connection.recv(2048)
    while True:
        if data.decode()=="":
                connection.close()
                break
        else:
                request=data.decode().replace("\r","\n").replace("\r\n","\n").replace("\n\n","\n")
                request_head = request.splitlines()[0]
                request_headline = request_head.split(" ") [1]
                print(request_headline)
                if request_headline=='/favicon.ico':
                    connection.close()
                    break
                else:
                    response_body=''
                    path=cwd+request_headline
                    if os.path.exists(path):
                        if os.path.isdir(path):
                            dir_list = os.listdir(path)
                            for file in dir_list:
                                url='http://localhost:8888'+request_headline +'/'+ file
                                response_body+='<h1><a href="'+ url +'"> '+ file + ' </a></h1>'
                                content_type=mimetypes.MimeTypes().guess_type(file)[0]
                            response_statuscode="HTTP/1.1 200 OK"
                            response_body_raw = ('<html><body>'+response_body+'</body></html>').encode()
                            response_headers = {
                                'Content-Type': "text/html",
                                'Content-Length': len(response_body_raw),
                                'Connection': 'close',
                                }
                        elif "bin" in path:
                            type=mimetypes.guess_type(path)[0]
                            o=open(path,"rb")
                            r=o.read()
                            response_body_raw = subprocess.run([sys.executable,"-c",r],capture_output=True,text=True).stdout.encode()
                            response_statuscode="HTTP/1.1 200 OK"
                            response_headers = {
                                'Content-Type': mimetypes.guess_type(path),
                                'Content-Length': len(response_body_raw),
                                'Connection': 'close',
                                }
                        else:
                            type=mimetypes.guess_type(path)[0]
                            o=open(path,"rb")
                            r=o.read()
                            response_body_raw = r
                            response_statuscode="HTTP/1.1 200 OK"
                            response_headers = {
                                'Content-Type': mimetypes.guess_type(path),
                                'Content-Length': len(response_body_raw),
                                'Connection': 'close',
                                }

                    else:
                        response_statuscode="HTTP/1.1 404 Not found"
                        response_body_raw = '<html><body><h1 style="color:red">Web Server Under construction</h1></body></html>'
                        response_headers = {
                                'Content-Type': 'text/html',
                                'Content-Length': len(response_body_raw),
                                'Connection': 'close',
                            }
                    response_raw=response(response_statuscode,response_headers)
                    connection.sendall(response_raw.encode()+response_body_raw)
                    connection.close()
                    break

if __name__ == "__main__":
    # creating thread
    t1 = multiprocessing.Process(target=HTTPServer, args=(('127.0.0.1', 8888)))
    t2 = multiprocessing.Process(target=HTTPServer, args=(('127.0.0.1', 8080)))
    # starting thread 1
    t1.start()
    # starting thread 2
    t2.start()
    # wait until thread 1 is completely executed
    t1.join()
    # wait until thread 2 is completely executed
    t2.join()
    # both threads completely executed
    print("Done!")