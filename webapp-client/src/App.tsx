import React, {useContext, useState, useEffect} from 'react';
import {Navigate, Route, Routes} from "react-router-dom";
import Header from "./components/Header";
import './App.css';

import UserContext from "./auth/userContext";
import Footer from './components/Footer';
import Home from './screens/Home';
import VideoRover from './screens/VideoRover';



function App() {

  const userCtx = useContext(UserContext);
  const [user, setUser] = useState(userCtx.user);
  const value = { user, setUser };


  return (
    <div className="h-screen w-full flex flex-col">

      <Routes>
        <Route path="/" element={<Navigate replace to="/home"/>}/>


        <Route path="*" element={
          <>
    
              <UserContext.Provider value={value}>
                <Header/>
                
                  <br />
                  <main className={'w-full pl-0.5 pr-0.5 lg:pl-5 lg:pr-5 items-center flex flex-col flex-grow '}>
                  {/* <RequestInterceptor> */}
                    <Routes>
                      <Route path="home" element={<VideoRover/>}/>
                      <Route path="videorover" element={<VideoRover/>}/>
                    </Routes>
                  {/* </RequestInterceptor> */}
                  </main>
                

              </UserContext.Provider>
          </>  
        } />
      </Routes>

      <Footer/>
  

    </div>
  );
}

export default App;
