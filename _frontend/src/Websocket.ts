import { defineStore } from "pinia";
import debug, { type WebsocketPacket } from "./types";
import { usePopupModel } from "./Components/Popup/popup";
import router from "./router";
import { usePhotoStore } from "./Components/Photos/photos";





function generatePacket(type: string, data: any) {
	const packet: WebsocketPacket = {
		t: type.toUpperCase(),
		d: data
	}

	return JSON.stringify(packet)
}

export const useWebsocket = defineStore("websocket", () => {
	const websocketURL = debug ? 'ws://localhost:8000/ws' : 'wss://pibble.pics/api/ws'
	const websocket = new WebSocket(websocketURL);
	const popup = usePopupModel();
	const photos = usePhotoStore();


	websocket.onopen = () => {
		console.log('Websocket connection opened');
		const token = localStorage.getItem('token')
		websocket.send(generatePacket('identify', { token: token }))
	};


	websocket.onmessage = (message) => {

		const data: WebsocketPacket = JSON.parse(message.data)
		switch (data.t) {
			case "PHOTO_CREATE":
				popup.showPopup(data.d.text)
				photos.fetch()

				break
			case "FRIEND_REQUEST":
				popup.showPopup(data.d.text)
				break
			case "COMMENT_CREATE":
				popup.showPopup(data.d.text, data)
				break

			case "PHOTO_LIKE":
				popup.showPopup(data.d.text)
				break
		}
	};

	function disconnect() {
		websocket.send(generatePacket('disconnect', {}))
		websocket.close()
	}
	return { websocket, disconnect };
})
