

const DEVICETYPE = 'controller'


export class WebsocketClient {
    private endpoint: string
    private port: number
    private hostname: string
    private ssl: boolean
    private token: string
    public ws: WebSocket | null

    public status: string = "not initialized"


    // ---------------------------------------------------
    constructor(hostname: string, port: number, endpoint: string, ssl:boolean=false , token:string='token'){
        this.hostname = hostname;
        this.port = port;
        this.endpoint = endpoint;
        this.ssl = ssl
        
        this.token = token

        this.ws = null
    };

    // ---------------------------------------------------
    activateStream(callback:any, robotId: string | number) {
        console.log("Connecting to "+this.getServerUrl(robotId));
        this.status='ok';
        this.ws = new WebSocket(this.getServerUrl(robotId));

        this.ws.onopen = (event: Event) => {
          this.send("hello from React")
          
        };
        this.ws.onmessage = callback;
        this.ws.onerror = (event: Event) => this.status=`error`;
        
    }

    // ---------------------------------------------------
    getServerUrl(robotId: string | number){
      if (this.ssl) return `wss://${this.hostname}:${this.port}${this.endpoint}?token=${this.token}&robotid=${robotId}&type=${DEVICETYPE}`
      return `ws://${this.hostname}:${this.port}${this.endpoint}?token=${this.token}&robotid=${robotId}&type=${DEVICETYPE}`
    }

    // ---------------------------------------------------
    send(msg:any) {
      if (this.ws !=null && this.ws.readyState === WebSocket.OPEN) {
        this.ws.send(msg);
      } 
      console.log(this.ws !=null)
    }

    // ---------------------------------------------------
    disconnect(){
      console.log(this.ws)
      if (this.ws != null) {
        this.ws.close();
        console.log("Closing socket....")
      }
    }
}