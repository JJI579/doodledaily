import { defineStore } from "pinia";
import debug from "./types";


type WebsocketPacket = {
	t: string
	d: any
}

function generatePacket(type: string, data: any) {
	const packet: WebsocketPacket = {
		t: type.toUpperCase(),
		d: data
	}

	return JSON.stringify(packet)
}

export const useWebsocket = defineStore("", () => {
	const websocketURL = debug ? 'ws://localhost:8000/ws' : 'wss://pibble.pics/api/ws'
	const websocket = new WebSocket(websocketURL);

	websocket.onopen = () => {
		console.log('Websocket connection opened');

		const token = localStorage.getItem('token')
		websocket.send(generatePacket('identify', { token: token }))
	};


	websocket.onmessage = (message) => {
		console.log(message)
	};

	return { websocket };
})
