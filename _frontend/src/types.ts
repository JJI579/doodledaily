
const debug = true;

type PhotoReturn = {
	photoID: number;
	photoName: string;
	photoType: string;
	photoData: string;
	photoOwnerID: number;
	photoCreatedAt: Date;
	isFavourited: Boolean | undefined;
	likesCount: number;
	commentCount: number;
};

type CommentReturn = {
	commentID: number;
	photoID: number;
	userID: number;
	comment: string;
	createdAt: Date;
};

type UserReturn = {
	userID: number;
	userName: string;
	userCreatedAt: string;
};

type FriendUserReturn = UserReturn & {
	isFriend: boolean;
};

type Notification = {
	name: string
	description: string
	createdAt: string
	type: string
}

export default debug;
export type { PhotoReturn, CommentReturn, UserReturn, FriendUserReturn, Notification };