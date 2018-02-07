import { GitUser } from './git-user';

export class Payload<T> {

	user: GitUser;
	payload: T;

}
