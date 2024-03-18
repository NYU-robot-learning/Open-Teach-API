import pickle
from .constants import *
from .network import create_request_socket, ZMQCameraSubscriber

class DeployAPI(object):
    def __init__(self, host_address, required_data):
        """
        Data structure for required_data: {
            'rgb_idxs': []
            'depth_idxs': []
        }
        """
        self._host_address = host_address
        self.required_data = required_data

        # Connect to the server
        self._connect_to_robot_server()

        # Initializing the required camera classes
        self._init_camera_subscribers()

    def _connect_to_robot_server(self):
        self.robot_socket = create_request_socket(
            host = self._host_address,
            port = DEPLOYMENT_PORT
        )

    def _init_camera_subscribers(self):
        self._rgb_streams, self._depth_streams = [], []

        for cam_idx in self.required_data['rgb_idxs']:
            self._rgb_streams.append(ZMQCameraSubscriber(
                host = self._host_address,
                port = RGB_PORT_OFFSET + cam_idx,
                topic_type = 'RGB'
            ))

            self._depth_streams.append(ZMQCameraSubscriber(
                host = self._host_address,
                port = RGB_PORT_OFFSET + DEPTH_PORT_OFFSET + cam_idx,
                topic_type = 'Depth'
            ))

    def get_robot_state(self):
        self.robot_socket.send(pickle.dumps('get_state', protocol = -1))
        robot_states = pickle.loads(self.robot_socket.recv())
        return robot_states

    def get_rgb_images(self):
        images = [stream.recv_rgb_image() for stream in self._rgb_streams]
        return images

    def get_depth_images(self):
        images = [stream.recv_depth_image() for stream in self._depth_streams]
        return images

    def  get_sensor_state(self):
        print('sending get_sensor_state!')
        self.robot_socket.send(pickle.dumps('get_sensor_state', protocol = -1))
        sensor_states = pickle.loads(self.robot_socket.recv())
        return sensor_states
        


    def send_robot_action(self, action_dict):
        """
        action_dict = {
            '<robot_1_name>': <robot_1_action>,
            '<robot_2_name>': <robot_2_action>
        }
        """
        self.robot_socket.send(pickle.dumps(action_dict, protocol = -1))
        self.robot_socket.recv()