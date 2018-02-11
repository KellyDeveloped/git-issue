import { GitUser } from '../issue/git-user';

export class Payload<T> {

	user: GitUser;
	payload: T;

}
