FROM ros:iron-ros-base

# install ros package
# RUN sh -c 'echo "deb http://packages.ros.org/ros/ubuntu $(lsb_release -sc) main" > /etc/apt/sources.list.d/ros-latest.list' && \
#       apt-get update && apt-get install -y curl && \
#       curl -sSL 'http://keyserver.ubuntu.com/pks/lookupop=get&search=0xC1CF6E31E6BADE8868B172B4F42ED6FBAB17C654' | apt-key add - && \
#       apt update

RUN apt-get update -y && apt-get install -y \
      ros-${ROS_DISTRO}-rviz2 \ 
      ros-${ROS_DISTRO}-joint-state-publisher-gui \
      ros-${ROS_DISTRO}-cv-bridge \
      ros-${ROS_DISTRO}-robot-state-publisher \
      ros-${ROS_DISTRO}-gazebo-ros-pkgs \
      ros-${ROS_DISTRO}-teleop-twist-joy \
      ros-${ROS_DISTRO}-turtlesim \
      # ros-${ROS_DISTRO}-gazebo-ros-control \
      ros-${ROS_DISTRO}-demo-nodes-py \
      python3-pip iputils-ping && \
    rm -rf /var/lib/apt/lists/*

RUN pip3 install xacro paho-mqtt


# launch ros package
CMD ["tail" ,"-f", "/dev/null" ]