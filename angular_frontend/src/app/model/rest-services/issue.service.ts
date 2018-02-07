import { Injectable } from '@angular/core'
import { HttpClient, HttpHeaders } from '@angular/common/http';

import { Observable } from 'rxjs/Observable'

import { Payload } from '../issue/payload'
import { Issue } from '../issue/issue'
import { Comment } from '../issue/comment'

import config = require('../../app.config')

@Injectable()
export class IssueService {

	constructor(private http: HttpClient) {
		
	}

	getIssue(issueID: string) {
		let url = config.specificIssueUrl(issueID);
		return this.http.get<Payload<Issue>>(url);
	}

	getAllIssues() {
		let url = config.issuesUrl;
		return this.http.get<Array<Issue>>(url);
	}

	getStatusIndicators(): Observable<Array<string>> {
		let url = config.statusIndicatorsUrl;
		return this.http.get<Array<string>>(url);
	}

	createIssue(issue: Issue) {
		let url = config.issuesUrl;
		const headers = new HttpHeaders({ 'Content-Type': 'application/json' });
		return this.http.post(url, JSON.stringify(issue), { headers: headers }).subscribe();
	}

	editIssue(issue: Issue) {
		let url = config.specificIssueUrl(issue.id);
		const headers = new HttpHeaders({ 'Content-Type': 'application/json' });
		return this.http.put(url, JSON.stringify(issue), { headers: headers });
	}

	getComments(issue: Issue, page: number, limit: number) {

	}

	addComment(issue: Issue, comment: Comment) {

	}

}
