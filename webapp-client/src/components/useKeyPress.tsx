import React, {useState} from 'react'

export const useKeyPress = function(targetKey: string) {
  const [keyPressed, setKeyPressed] = useState(false);

  React.useEffect(() => {
    const downHandler = ({ key }:any ) => {
      if (key === targetKey) {
        setKeyPressed(!keyPressed);
        console.log("I'm down---")
      }
    }
  
    const upHandler = ({ key }:any ) => {
      if (key === targetKey) {
        setKeyPressed(false);
      }
    };

    window.addEventListener("keydown", downHandler);
    window.addEventListener("keyup", upHandler);

    return () => {
      window.removeEventListener("keydown", downHandler);
      window.removeEventListener("keyup", upHandler);
    };
  }, [targetKey]);

  return keyPressed;
};
