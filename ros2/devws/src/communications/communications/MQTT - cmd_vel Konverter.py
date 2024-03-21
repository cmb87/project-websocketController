#MQTT - cmd_vel Konverter
#20.11.2023
#P.Wech @ SE

import rclpy
from geometry_msgs.msg import Twist
import paho.mqtt.client as mqtt
import json

def on_connect(client, userdata, flags, rc):
    print("Connected wit result code {rc}")
    client.subscribe("PLACEHOLDER") ###PLACEHOLDER




def on_message(client, userdata, msg):
    command = msg.payload.decode('UTF-8')

    commandDict = json.loads(command)

    x = commandDict["controller"]["x"]
    y = commandDict["controller"]["y"]

    twist=Twist()
    twist.linear.x = x
    twist.angular.z = y 

    vel_pub.publish(twist)


def main():
    rclpy.init()
    global vel_pub
    vel_pub = rclpy.create_node('vel_publisher').create_publisher(Twist, "cmd_vel", 10)
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect("MQTT_BROKER",1883,60) ##### Placeholder
    try:
        client.loop_start()
        rclpy.spin(vel_pub)
    except KeyboardInterrupt:
        print(KeyboardInterrupt)
        client.disconnect()
        rclpy.shutdown()

if __name__ == '__main__':
    main()