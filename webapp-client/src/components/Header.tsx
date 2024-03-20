import React, {useState, useContext } from "react";
import {Link, NavLink, useNavigate} from "react-router-dom";


import UserContext from "../auth/userContext";
import environment from "../environment.json";
//import UserName from "./UserName";


// https://tailwindcomponents.com/component/navbar-with-tagline-and-logo

const Header = () => {
    // const history = createBrowserHistory();
    const navigate = useNavigate();
    const { user, setUser } = useContext(UserContext);

    return (
        <>
        <nav className="font-sans flex flex-col text-center content-center sm:flex-row sm:text-left sm:justify-between py-2 px-6 shadow sm:items-baseline w-full bg-[#1B1534]">

            <div className="mb-2 sm:mb-0 flex flex-row">

              <div>
                <a href="/home" className="text-2xl no-underline text-white hover:text-blue-dark font-sans font-bold"></a>
                <br />
                <span className="text-xs text-white"></span>
              </div>
            </div>

            {/* <div className="sm:mb-0 self-center text-white flex flex-row">
              <UserName name={user.name} initials={user.initials}/>
            </div> */}

        </nav>
        </>);
    };

export default Header;


interface IUserName {
  name: string
  initials: string
}


function UserName({name, initials}:IUserName) {
  return (
    
    <div className="flex flex-row justify-center items-center">
      <span
        className="
        text-m inline-block py-4 px-3
        leading-none text-center whitespace-nowrap
        align-baseline font-bold
        bg-purple-900
        text-white rounded-full">
        <p>{initials}</p>
      </span>
      <div className="px-3">
        {name}
      </div>
      
    </div>
  )
}
