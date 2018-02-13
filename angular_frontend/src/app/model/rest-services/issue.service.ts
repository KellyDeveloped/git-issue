import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders, HttpResponse } from '@angular/common/http';

import { Observable } from 'rxjs/Observable';

import { Payload } from '../rest-responses/payload';
import { IssueList } from '../rest-responses/issue-list';
import { Issue } from '../issue/issue';
import { Comment } from '../issue/comment';

import config = require('../../app.config');

@Injectable()
export class IssueService {

	constructor(private http: HttpClient) {
		
	}

	getIssue(issueID: string): Observable<Payload<Issue>> {
		let url = config.specificIssueUrl(issueID);
		return this.http.get<Payload<Issue>>(url);
	}

	getIssuePage(page: number = 1, limit: number = 10): Observable<Payload<IssueList>> {
		let url = config.issuePageUrl(page, limit)
		return this.http.get<Payload<IssueList>>(url);
	}

	getStatusIndicators(): Observable<Array<string>> {
		let url = config.statusIndicatorsUrl;
		return this.http.get<Array<string>>(url);
	}

	createIssue(issue: Issue) {
		let url = config.issuesUrl;
		const headers = new HttpHeaders({ 'Content-Type': 'application/json' });
		return this.http.post<Payload<Issue>>(url, JSON.stringify(issue), { headers: headers });
	}

	editIssue(issue: Issue) {
		let url = config.specificIssueUrl(issue.id);
		const headers = new HttpHeaders({ 'Content-Type': 'application/json' });
		return this.http.put<Payload<Issue>>(url, JSON.stringify(issue), { headers: headers, observe: 'response' });
	}

	getComments(issue: Issue, page: number, limit: number): Observable<Array<Comment>> {
		let url = config.commentUrl(issue.id);
		return this.http.get<Array<Comment>>(url);
	}

	addComment(issue: Issue, comment: Comment) {

	}

}
