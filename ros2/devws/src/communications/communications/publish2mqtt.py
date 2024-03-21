#!/usr/bin/env python3

import rclpy
from rclpy.time import Time

from time import sleep
import sys
import threading
import numpy as np
import os
import json
import paho.mqtt.client as mqtt
from rclpy.node import Node
from rclpy.qos import qos_profile_system_default
from rclpy.qos import qos_profile_services_default
import time
from geometry_msgs.msg import Twist
from geometry_msgs.msg import TransformStamped

#from geometry_msgs.msg import Point, Pose, Quaternion, Vector3
from std_msgs.msg import Int32, Float32

import json
import ssl

from ament_index_python.packages import get_package_share_directory




class RelayRos2Mqtt(Node):
    def __init__(self):
        super().__init__('rosmqtt')
        
        # ===========================================
       # self.sleep_rate = 0.025
      #  self.rate = 10
        self.r = self.create_rate(500)


        self.broker_address= self.declare_parameter("~broker_ip_address",  "a2wwp2wisduhx5-ats.iot.eu-central-1.amazonaws.com").value
        self.MQTT_SUB_TOPIC = self.declare_parameter("~mqtt_pub_topic", 'controller').value
        self.CLIENT_ID = self.declare_parameter("~client_id", "thing_2825ffcb1a23332b").value

        self.timer = self.create_timer(0.01, self.timer_callback)
        self.command = {"controller": {"x": 0.0, "y": 0.0}}

        # ===========================================
        self.get_logger().info("rosmqtt:: Creating cmd_vel publisher...")
        # See  pub = rospy.Publisher('cmd_vel', Twist, queue_size=10)
        self.vel_pub = self.create_publisher(Twist, "cmd_vel", 10)
        
        # ===========================================
        awsport = 8883

        caPath = os.path.join(get_package_share_directory('rosmqtt'), "certs", "authority.pem")
        certPath = os.path.join(get_package_share_directory('rosmqtt'), "certs", "d3cbb87200878fc0c527de198276de6155a2d486edec9f19a06b6040d59bf4a1-certificate.pem.crt")
        keyPath  = os.path.join(get_package_share_directory('rosmqtt'), "certs", "private.pem.key")




        # Start a new client
        self.mqttclient = mqtt.Client(client_id=self.CLIENT_ID) 

        self.mqttclient.tls_set(
            caPath, 
            certfile=certPath, 
            keyfile=keyPath, 
            cert_reqs=ssl.CERT_REQUIRED, 
            tls_version=ssl.PROTOCOL_TLSv1_2, 
            ciphers=None
        )

        self.mqttclient.tls_insecure_set(False)
        mqtt.Client.connected_flag = False
        mqtt.Client.bad_connection_params=False


        self.mqttclient.on_publish = self.on_publish
        self.mqttclient.on_connect = self.on_connect
        self.mqttclient.on_message = self.on_message

        self.mqttclient.loop_start()

        self.mqttclient.connect(self.broker_address, awsport, keepalive=120)

        time.sleep(1)

        self.get_logger().info(f"rosmqtt:: connected_flag={mqtt.Client.connected_flag}, bad_connection_params={mqtt.Client.bad_connection_params}")

        while mqtt.Client.connected_flag == False and mqtt.Client.bad_connection_params == False:
            self.get_logger().info("rosmqtt:: Waiting for connection...")
            time.sleep(1)
            if mqtt.Client.bad_connection_params == True:
                self.mqttclient.loop_stop()
                sys.exit()


        self.get_logger().info(f'rosmqtt:: started...')
        self.get_logger().info(f'rosmqtt:: broker_address = {self.broker_address}')
        self.get_logger().info(f'rosmqtt:: MQTT_PUB_TOPIC = {self.MQTT_SUB_TOPIC}')





    def on_publish(self, client,userdata,result):             #create function for callback
        self.get_logger().info("data published")


    def on_connect(self, client, userdata, flags, rc):
        if rc==0:
            self.get_logger().info("Connected OK")
            mqtt.Client.connected_flag=True
            mqtt.Client.bad_connection_params=False
            self.get_logger().info(f"Subscribed to {self.MQTT_SUB_TOPIC}")
            client.subscribe(self.MQTT_SUB_TOPIC)
            
        else:
            mqtt.Client.bad_connection_params=True
            if rc==1:
                self.get_logger().info("Failed to connect. Connection refused, unacceptable protocol version. Error Code=", rc)
            elif rc==2:
                self.get_logger().info("Failed to connect.Connection refused, identifier rejected. Error Code=", rc)
            elif rc==3:
                self.get_logger().info("Failed to connect.Connection refused, server unavailable. Error Code=", rc)
            elif rc==4:
                self.get_logger().info("Failed to connect.Connection refused, bad user name or password. Error Code=", rc)
            elif rc==5:
                self.get_logger().info("Failed to connect.Connection refused, not authorized. Error Code=", rc)


    def on_message(self, client, userdata, msg):

        # self.get_logger().info("{0}, {1} - {2}".format(userdata, msg.topic, msg.payload))

        try:

            self.command = json.loads(msg.payload.decode('UTF-8'))

            # twist=Twist()
            # twist.linear.x = float(-command["controller"]["y"])
            # twist.linear.y = 0.0
            # twist.linear.z = 0.0

            # twist.angular.x = 0.0
            # twist.angular.y = 0.0 
            # twist.angular.z = float(-command["controller"]["x"])


           # self.vel_pub.publish(twist)

        except Exception as e:
            self.get_logger().error(f"{e}")


    def timer_callback(self):
        try:
            twist=Twist()
            twist.linear.x = float(-self.command["controller"]["y"])
            twist.linear.y = 0.0
            twist.linear.z = 0.0

            twist.angular.x = 0.0
            twist.angular.y = 0.0 
            twist.angular.z = float(-self.command["controller"]["x"])


            self.vel_pub.publish(twist)

        except Exception as e:
            self.get_logger().error(f"{e}")




def main(args=None):
    

    rclpy.init(args=args)
    try:
        relay_ros2_mqtt = RelayRos2Mqtt()
        rclpy.spin(relay_ros2_mqtt)
    except rclpy.exceptions.ROSInterruptException:
        pass

    relay_ros2_mqtt.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
