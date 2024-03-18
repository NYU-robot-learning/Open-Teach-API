import zmq
import cv2
import pickle
import base64
import threading
import blosc as bl
import numpy as np

def create_request_socket(host, port):
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect('tcp://{}:{}'.format(host, port))
    return socket

class ZMQCameraSubscriber(threading.Thread):
    def __init__(self, host, port, topic_type):
        self._host, self._port, self._topic_type = host, port, topic_type
        self._init_subscriber()

    def _init_subscriber(self):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.SUB)
        self.socket.setsockopt(zmq.CONFLATE, 1)
        self.socket.connect('tcp://{}:{}'.format(self._host, self._port))

        if self._topic_type == 'Intrinsics':
            self.socket.setsockopt(zmq.SUBSCRIBE, b"intrinsics")
        elif self._topic_type == 'RGB':
            self.socket.setsockopt(zmq.SUBSCRIBE, b"rgb_image")
        elif self._topic_type == 'Depth':
            self.socket.setsockopt(zmq.SUBSCRIBE, b"depth_image")

    def recv_intrinsics(self):
        raw_data = self.socket.recv()
        raw_array = raw_data.lstrip(b"intrinsics ")
        return pickle.loads(raw_array)

    def recv_rgb_image(self):
        raw_data = self.socket.recv()
        data = raw_data.lstrip(b"rgb_image ")
        data = pickle.loads(data)
        encoded_data = np.fromstring(base64.b64decode(data['rgb_image']), np.uint8)
        return cv2.imdecode(encoded_data, 1), data['timestamp']
        
    def recv_depth_image(self):
        raw_data = self.socket.recv()
        striped_data = raw_data.lstrip(b"depth_image ")
        data = pickle.loads(striped_data)
        depth_image = bl.unpack_array(data['depth_image'])
        return np.array(depth_image, dtype = np.int16), data['timestamp']
        
    def stop(self):
        print('Closing the subscriber socket in {}:{}.'.format(self._host, self._port))
        self.socket.close()
        self.context.term()