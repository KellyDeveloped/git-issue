import { Injectable } from '@angular/core';

import { ReplaySubject } from 'rxjs/ReplaySubject';

import { Issue } from '../issue/issue';
import { GitUser } from '../issue/git-user';
import { CacheEntry } from '../issue/cache-entry';
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
				subject.next([])
				return subject;
			}
			else {
				return this.getPageFromServer(page, limit);
			}
		}
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
