import React, {useEffect, useState, useRef } from 'react'
import { WebsocketClient } from '../components/WebsocketClient';
import { Joystick, JoystickShape } from 'react-joystick-component';

import testimg from '../assets/camera.png';
import {InputFieldSelectSlim}  from '../components/InputFieldSlim';
import { IJoystickStatus, float2int } from '../components/utils';
import environment from '../environment.json';


// Instantiate the socket connections
const wsStreamer = new WebsocketClient(
  environment.websocket.server,
  environment.websocket.port,
  "/control",
  environment.websocket.ssl,
  environment.websocket.token,
)  

const wsVideoStreamer = new WebsocketClient(
  environment.websocket.server,
  environment.websocket.port,
  "/video",
  environment.websocket.ssl,
  environment.websocket.token
)  


export default function VideoRover() {

  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [status, setStatus] = useState<string>("offline");
  const [robotId, setRobotId] = useState<string>("1");
  const [robotState, setRobotState] = useState<string>("{}");


  const [joystickStatus, setJoystickStatus] = useState<IJoystickStatus>({
    x: 0, y:0, type: "stop" ,direction: "IDLE", distance: 0.0
  });
  

  // ----------------------------------
  const drawImage =  (imageSrc: string) => {
    const canvas = canvasRef.current;  
    if (!canvas) return;

    const ctx = canvas.getContext("2d");  

    const image = new Image();  
    image.src = imageSrc; 
    image.onload = () => {  
      // Draw the decoded image on the canvas  
      canvas!.width = image.width;  
      canvas!.height = image.height;  
      ctx!.drawImage(image, 0, 0, image.width, image.height);  
    }
  }

  // ----------------------------------
  useEffect(() => {

    // Disconnect first
    setStatus(`offline`)
    setRobotState("{}")
    wsStreamer.disconnect();
    wsVideoStreamer.disconnect();

    // if nothing is specified draw the testimage
    drawImage(testimg);

    // websocket callback
    const wsUpdateImageCB = ( msg:any ) => {
      try {
      const reader = new FileReader();  
      reader.onload = () => {  
        drawImage(reader.result as string);
      };  

      // Set time stamp
      const d = new Date();
      setStatus(`${d.getTime()}`)

      try {
        reader.readAsDataURL(msg.data);
      } catch(err) {
        console.log(err);
      }

      } catch (err) {
        console.log("Error in WS CB")
      }
    }

    // Now start the streams
    wsVideoStreamer.activateStream(wsUpdateImageCB, robotId);

    wsStreamer.activateStream((msg:any)=> {
      try {
        console.log(msg);
        setRobotState(JSON.stringify(JSON.parse(msg.data))); 
        
      } catch(err) {}
    }, robotId);

  }, [robotId])

  // ----------------------------------
  useEffect(() => {}, [joystickStatus, wsStreamer.status, wsVideoStreamer.status])

  // ----------------------------------
  const publish = (d:IJoystickStatus) => {

    const cmds = {
      t: 0,
      x: float2int(255*d.x),
      y: float2int(255*d.y)
    };
    
    // Sending buffer
    wsStreamer.send(JSON.stringify(cmds));

    // send buffer
    setJoystickStatus({x: d.x, y:-d.y, type: d.type , direction: d.direction, distance: 0.0});

  }

  
  // ----------------------------------
  const publishLightOn = async () => {
    wsStreamer.send(JSON.stringify({t: 2,x: 0,y: 0}));
  }

  // ----------------------------------
  const publishLightOff = async () => {
    wsStreamer.send(JSON.stringify({t: 1,x: 0,y: 0}));
  }

  return (
    <div className="xl:w-5/6 md:w-full sm:w-full w-full">

      <div className="grid md:grid-cols-1 sm:grid-cols-1 xl:grid-cols-2 grid-cols-1">

        <div className="flex-col p-5 w-full">

            <h2 className="my-4 text-xl font-extrabold leading-none tracking-tight text-gray-700 ">Video Stream</h2>
            { status !== "offline" ? <span className={`bg-green-900 text-white text-xs font-medium mr-1 px-1.5 py-0.5 my-3 rounded`}>{status}</span> : 
            <span className={`bg-red-900 text-white text-xs font-medium mr-1 px-1.5 py-0.5 my-3 rounded`}>{status}</span> 
            }
            <canvas width={"100%"} height={"100%"} ref={canvasRef} className='w-full mb-5'></canvas>

        </div>



        <div className="flex-col p-5 w-full">

          {/* Controll */}
          <div className="flex-col">


              <h2 className="my-4 text-xl font-extrabold leading-none tracking-tight text-gray-700 ">Controller</h2>

              <InputFieldSelectSlim
                id={"X"}
                label={'Select Unit:'}
                options={[
                    {key: "Unit 1", value: "1"},
                    {key: "Unit 2", value: "2"},
                    {key: "Unit 3", value: "3"},
                    {key: "Unit 4", value: "4"},
                    {key: "Unit 5", value: "5"},
                    {key: "Unit 6", value: "6"},
                ]}
                onChange={(x:any) => {
                    setRobotId(x);
                }}
                value={robotId}
            />

              <div className='flex flex-row gap-5'>

              <Joystick 
                size={100}
                sticky={false}
                baseColor="gray"
                throttle={40}
                minDistance={10}
                stickColor="#12086F"

                move={(d:any) => publish(d)} 
                stop={(d:any)=>  publish({x: 0, y:0, type: "stop" , direction: "IDLE", distance: 0.0})}
                baseShape={JoystickShape.Square}
              />

              <button className="bg-blue-900 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded-xl" onClick={()=> publishLightOn()}>
                Lights On
              </button>

              <button className="bg-red-800 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded-xl" onClick={()=> publishLightOff()}>
                Lights Off
              </button>
              </div>


              <hr className='mb-5 mt-5'/>
              <div className='flex flex-row gap-5'>
                <pre>
                  Status Control-Socket: <b>{wsStreamer.status}</b>
                </pre>
              </div>

              <div className='flex flex-row gap-5'>
                <pre>
                  Status Video-Socket:   <b>{wsVideoStreamer.status}</b>
                </pre>
              </div>
              

          </div>

          {/* Status
          <div className="flex-col rounded-xl border border-gray-500 p-5 shadow-xl w-full">
            
            <h2 className="my-4 text-xl font-extrabold leading-none tracking-tight text-gray-700 ">Status</h2>

            <span className={`bg-red-900 text-white text-xs font-medium mr-1 px-1.5 py-0.5 my-3 rounded`}>x: {float2int(255*joystickStatus.x)}</span> 
            <span className={`bg-red-900 text-white text-xs font-medium mr-1 px-1.5 py-0.5 my-3 rounded`}>y: {float2int(255*joystickStatus.y)}</span> 
            <span className={`bg-red-900 text-white text-xs font-medium mr-1 px-1.5 py-0.5 my-3 rounded`}>{joystickStatus.direction}</span> 
            <span className={`bg-red-900 text-white text-xs font-medium mr-1 px-1.5 py-0.5 my-3 rounded`}>{joystickStatus.type}</span> 
            <div className="grid grid-cols-2 gap-4 mb-5">

            <div><pre>{JSON.stringify(JSON.parse(robotState), null, 2) }</pre></div>

            </div>    

          </div> */}
          
        </div>


      </div>




    </div>
  )
}


