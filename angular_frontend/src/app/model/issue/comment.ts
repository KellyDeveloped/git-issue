import { GitUser } from './git-user'

export class Comment {

	constructor(comment?: string) {
		this.comment = comment;
	}

	comment: string;
	date: string;
	user: GitUser;
	uuid: string;

}
