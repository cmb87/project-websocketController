
export interface IJoystickStatus {
    x: number
    y: number
    type: string | null
    direction: string | null
    distance: number | null
  }
  
  
export function float2int (value:number) {
    return value | 0;
  }
  
  