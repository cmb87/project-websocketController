# Use the official Node.js image as the base image  
FROM node:16 
  
# Set the working directory for the container  
WORKDIR /usr/src/app  
  
# Copy package.json and package-lock.json to the working directory  
COPY package*.json ./  
  
# Install the application dependencies  
RUN npm install  
  
# Copy the application source code to the working directory  
COPY . .  
  
# Expose the port on which the Express server will run  
EXPOSE 8080  
  
# Start the Express server  
CMD ["node", "app.js"]  