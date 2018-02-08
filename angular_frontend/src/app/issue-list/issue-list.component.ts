import { ActivatedRoute } from '@angular/router';
import { Component, OnInit } from '@angular/core';

import { IssueService } from '../model/rest-services/issue.service'
import { Issue } from '../model/issue/issue'
import { GitUser } from '../model/issue/git-user'

@Component({
	selector: 'app-issue-list',
	templateUrl: './issue-list.component.html',
	styleUrls: ['./issue-list.component.css'],
	providers: [IssueService]
})
export class IssueListComponent implements OnInit {

	issues: Array<Issue> = [];
	gitUser: GitUser;

	constructor(private issueService: IssueService, private route: ActivatedRoute) { }

	ngOnInit() {
		const id = this.route.snapshot.paramMap.get("id");
		this.issueService.getAllIssues().subscribe((res) => {
			this.issues = res.payload
			this.gitUser = res.user
		});
	}

}
