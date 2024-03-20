import React, { Dispatch,SetStateAction} from 'react';

interface IUser {
    name: string
    user_name: string
    authenticated: boolean
    email: string
    role: string
    initials: string
}

export interface IUserContext {
    user: IUser
    setUser: Dispatch<SetStateAction<IUser>>;
  }
  
const UserContext = React.createContext<IUserContext>(
    {
        user: {
            name: "Unauthenticated",
            user_name: "Unauthenticated",
            authenticated: false,
            email: "unauthenticated@unauthenticated",
            role: "dev",
            initials: "UU"
        },
        setUser: () => {}
        
    }
)



export const UserProvider = UserContext.Provider
export default UserContext


// See https://medium.com/@danfyfe/using-react-context-with-functional-components-153cbd9ba214
// https://stackoverflow.com/questions/71333605/how-can-i-correctly-initialize-the-type-dispatchsetstateactionstring-as-a
// https://stackoverflow.com/questions/41030361/how-to-update-react-context-from-inside-a-child-component