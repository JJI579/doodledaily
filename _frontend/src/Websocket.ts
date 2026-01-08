import { defineStore } from "pinia";
import debug from "./types";


type WebsocketPacket = {
	t: string
	d: any
}



export const useWebsocket = defineStore("", () => {
	const websocketURL = debug ? 'ws://localhost:8000/ws' : 'wss://pibble.pics/api/ws'
	const websocket = new WebSocket(websocketURL);



	websocket.onopen = () => {
		console.log('Websocket connection opened');
	};


	websocket.onmessage = (message) => {
		console.log(message)
	};

	return { websocket };
})
