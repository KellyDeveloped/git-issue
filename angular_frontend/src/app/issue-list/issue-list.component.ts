import { ActivatedRoute } from '@angular/router';
import { Component, OnInit } from '@angular/core';
import { MatDialog } from '@angular/material';

import { IssueCacheService } from '../model/services/issue-cache.service';
import { Issue } from '../model/issue/issue';
import { GitUser } from '../model/issue/git-user';
import { ErrorDialogueComponent } from '../error-dialogue/error-dialogue.component';

@Component({
	selector: 'app-issue-list',
	templateUrl: './issue-list.component.html',
	styleUrls: ['./issue-list.component.css']
})
export class IssueListComponent implements OnInit {

	page: Array<Issue>;
	pageNumber: number = 1;
	gitUser: GitUser;

	constructor(private dialogue: MatDialog,
		private cacheService: IssueCacheService,
		private route: ActivatedRoute) { }

	getEditLink(issue: Issue) {
		return `${issue.id}/edit`;
	}

	ngOnInit() {
		this.cacheService.getPage(1, 1000).subscribe(res => {
			this.page = res;
			console.log(this.page);
		}, err => {
			this.dialogue.open(ErrorDialogueComponent, {
				'data': err
			});
			this.page = [];
		});
	}

}
