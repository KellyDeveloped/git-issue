import { Injectable } from '@angular/core'
import { HttpClient, HttpHeaders } from '@angular/common/http';

import { Issue } from '../issue/issue'
import { Comment } from '../issue/comment'

import config = require('../../app.config')

@Injectable()
export class IssueService {

	constructor(private http: HttpClient) {
		
	}

	getIssue(issueID: string) {
		let url = config.specificIssueUrl(issueID);
		return this.http.get<Issue>(url);
	}

	getAllIssues() {
		let url = config.issuesUrl;
		return this.http.get<Array<Issue>>(url);
	}

	createIssue(issue: Issue) {

	}

	editIssue(issue: Issue) {

	}

	getComments(issue: Issue, page: number, limit: number) {

	}

	addComment(issue: Issue, comment: Comment) {

	}

}
