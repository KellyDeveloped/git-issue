import { Injectable } from '@angular/core';
import { HttpErrorResponse } from '@angular/common/http';
import { ReplaySubject } from 'rxjs/ReplaySubject';

import { Issue } from '../issue/issue';
import { GitUser } from '../issue/git-user';
import { CacheEntry } from '../issue/cache-entry';
import { Payload } from '../rest-responses/payload';
import { IssueService } from '../rest-services/issue.service';

@Injectable()
export class IssueCacheService {

	issues: Array<CacheEntry<Issue>>;
	countCache: CacheEntry<number>;
	currentUser: GitUser;

	constructor(private issueService: IssueService) {
		this.issues = [];
		this.countCache = new CacheEntry<number>(0);
	}

	getIssue(id): ReplaySubject<Issue> {
		const subject = new ReplaySubject<Issue>(1);
		let issue = this.issues.find(i => i.entry.id === id);

		if (issue === undefined) {
			this.issueService.getIssue(id).subscribe(res => {
				const entry = new CacheEntry(res.payload);
				this.currentUser = res.user;

				subject.next(res.payload);

				this.issues.push(entry);
				this.sortIssues()
			});
		}
		else {
			subject.next(issue.entry);
		}

		return subject;
	}

	getPage(page = 1, limit = 10): ReplaySubject<Array<Issue>> {
		const subject = new ReplaySubject<Array<Issue>>(1);
		const offset = this.calculateOffset(page, limit);
		let endPos = offset + limit;

		if (this.countCache.entry > 0 && endPos > this.countCache.entry && !this.countCache.isStale()) {
			endPos = this.countCache.entry;
		}

		if (endPos <= this.issues.length) {
			let issues: Issue[] = []

			for (let i = offset; i < endPos; i++) {
				if (this.issues[i].isStale()) {
					return this.getPageFromServer(page, limit);
				}
				issues.push(this.issues[i].entry);
			}

			subject.next(issues);
			return subject;
		}
		else {
			if (offset > this.countCache.entry) {
				subject.next([]);
				return subject;
			}
			else {
				return this.getPageFromServer(page, limit);
			}
		}
	}

	editIssue(issue: Issue): ReplaySubject<Payload<Issue>> {
		const subject = new ReplaySubject<Payload<Issue>>(1);

		this.issueService.editIssue(issue).subscribe((response) => {
			let body: Payload<Issue>;

			if (response.body !== null) {
				body = response.body;
			}
			else {
				throw Error(`The response to an edit request of ${issue.id} returned no body.
							This goes against what I understand to be the contract.`);
			}

			if (response.status === 200) {
				// Should never be -1 due to API contract.
				let index = this.issues.findIndex(i => i.entry.id === body.payload.id);
				this.issues[index] = new CacheEntry(body.payload);
			}
			else { // If not 200, then it's created a new issue
				this.issues.push(new CacheEntry(body.payload));
				this.sortIssues();
			}

			subject.next(body);
		}, subject.error);

		return subject;
	}

	createIssue(issue: Issue): ReplaySubject<Payload<Issue>> {
		const subject = new ReplaySubject<Payload<Issue>>(1);

		this.issueService.createIssue(issue).subscribe((res) => {
			this.issues.push(new CacheEntry<Issue>(res.payload));
			this.countCache = new CacheEntry<number>(this.countCache.entry + 1);
			this.sortIssues();
			subject.next(res);
		}, err => {
			subject.error(err);
		});

		return subject;
	}

	private calculateOffset(page: number, limit: number) {
		if (page < 1) {
			throw RangeError(`A page number must be greater than zero. Given page number was ${page}`)
		}

		return (page - 1) * limit;
	}

	private getPageFromServer(page: number, limit: number): ReplaySubject<Array<Issue>> {
		const subject = new ReplaySubject<Array<Issue>>(1);

		this.issueService.getIssuePage(page, limit).subscribe(res => {
			this.countCache = new CacheEntry<number>(res.payload.count);
			this.currentUser = res.user;

			subject.next(res.payload.issues);

			for (let issue of res.payload.issues) {
				let entry = new CacheEntry<Issue>(issue);

				let index = this.issues.findIndex(i => i.entry.id === issue.id);

				if (index === -1) {
					this.issues.push(entry);
				}
				else {
					this.issues[index] = entry;
				}
			}

			this.sortIssues();
		}, err => {
			subject.error(err);
		});

		return subject;
	}

	private sortIssues() {
		this.issues.sort((a, b) => {
			if (a.entry > b.entry) {
				return 1;
			}
			else if (a.entry < b.entry) {
				return -1;
			}
			else {
				return 0;
			}
		});
	}

}
