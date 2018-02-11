import { ActivatedRoute } from '@angular/router';
import { Component, OnInit } from '@angular/core';

import { IssueCacheService } from '../model/services/issue-cache.service'
import { Issue } from '../model/issue/issue'
import { GitUser } from '../model/issue/git-user'

@Component({
	selector: 'app-issue-list',
	templateUrl: './issue-list.component.html',
	styleUrls: ['./issue-list.component.css']
})
export class IssueListComponent implements OnInit {

	page: Array<Issue>;
	pageNumber: number = 1;
	gitUser: GitUser;

	constructor(private cacheService: IssueCacheService, private route: ActivatedRoute) { }

	ngOnInit() {
		this.cacheService.getPage(1, 10).subscribe(res => {
			this.page = res;
			console.log(this.page);
		});
	}

}
