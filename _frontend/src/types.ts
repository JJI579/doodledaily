const apiUrl = import.meta.env.VITE_ENVIRONMENT || "not";
const debug = apiUrl == "dev";
export default debug;

type PhotoReturn = {
	photoID: number;
	photoName: string;
	photoCaption: string;
	photoType: string;
	photoData: string;
	photoOwnerID: number;
	photoCreatedAt: Date;
	isFavourited: Boolean | undefined;
	likesCount: number;
	commentCount: number;
};

type LoginReturn = {
	type: string;
	id: number;
	token: string;
	refresh_token: string;
	expires_at: string;
}

type CommentReturn = {
	commentID: number;
	photoID: number;
	userID: number;
	comment: string;
	createdAt: Date;
	likeCount: number
	hasLiked: boolean
};

type UserReturn = {
	userID: number;
	userName: string;
	userCreatedAt: string;
};

type UserReturnCache = UserReturn & {
	fetchedAt: number
}

type SelfReturn = UserReturn & {
	friends: UserReturn[];
}

type FriendUserReturn = UserReturn & {
	isFriend: boolean;
};

type Notification = {
	name: string
	description: string
	createdAt: string
	type: string
}

// Websocket

type WebsocketPacket = {
	t: string
	d: any
}


export type { PhotoReturn, CommentReturn, UserReturn, FriendUserReturn, Notification, SelfReturn, LoginReturn, WebsocketPacket, UserReturnCache };
