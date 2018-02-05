import { GitUser } from './git-user'

export class Issue {

	id: string;
	date: string;
	summary: string;
	description: string;
	reporter: GitUser;
	assignee: GitUser;
	subscribers: Array<GitUser>;

}
